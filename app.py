import os
import json
import orjson
import redis
from flask import Flask, Response

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Initialize Redis Connection Pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)


def load_data_to_redis():
    """Load JSON data to Redis database dynamically at startup."""
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)

        redis_client.delete("countries")

        for item in data:
            country_name = item.get("name")
            country_code = item.get("iso2")
            if not country_code or not country_name:
                continue

            states_list = item.get("states") or []
            
            # Pack country name and code as JSON string for the set
            country_data = orjson.dumps({"country": country_name, "code": country_code})
            redis_client.sadd("countries", country_data)
            
            state_data_list = []
            all_cities = []
            
            for state_obj in states_list:
                state_name = state_obj.get("name")
                if not state_name:
                    continue
                    
                # New data source lacks slugs, so we safely generate them dynamically
                state_slug = state_obj.get("slug")
                if not state_slug:
                    state_slug = state_name.lower().replace(" ", "-")
                else:
                    state_slug = state_slug.lower()
                
                # Push a json object for the states list
                state_data_list.append(orjson.dumps({"name": state_name, "slug": state_slug}))
                
                # New data source cities are objects {"name": "Ashkāsham", etc...} 
                cities_complex = state_obj.get("cities") or []
                cities = []
                for city_obj in cities_complex:
                    if city_obj and city_obj.get("name"):
                        cities.append(city_obj.get("name"))
                        
                all_cities.extend(cities)
                
                redis_client.delete(f"cities:{country_code}:{state_slug}")
                if cities:
                    redis_client.sadd(f"cities:{country_code}:{state_slug}", *cities)
                
            redis_client.delete(f"states:{country_code}")
            if state_data_list:
                redis_client.sadd(f"states:{country_code}", *state_data_list)
                
            # Maintain flat city list if desired
            redis_client.delete(f"cities:{country_code}")
            if all_cities:
                redis_client.sadd(f"cities:{country_code}", *all_cities)


# Execute data upload at startup
try:
    load_data_to_redis()
except Exception as e:
    print(f"Failed to load data to Redis: {e}")


# Fast JSON formatter
def json_response(data, status=200):
    return Response(orjson.dumps(data), status=status, mimetype="application/json")


@app.route("/", methods=["GET"])
def health_check():
    return json_response({"status": "healthy"})


@app.route("/countries", methods=["GET"])
def get_countries():
    # smembers returns a set of JSON strings
    countries_raw = redis_client.smembers("countries")
    # Parse them back into dicts to return them natively
    countries = [orjson.loads(c) for c in countries_raw]
    countries.sort(key=lambda x: x["country"])
    return json_response(countries)


@app.route("/cities/<country_code>", defaults={'state_slug': None}, methods=["GET"])
@app.route("/cities/<country_code>/<state_slug>", methods=["GET"])
def get_cities(country_code, state_slug):
    if state_slug:
        cities = redis_client.smembers(f"cities:{country_code.upper()}:{state_slug.lower()}")
    else:
        cities = redis_client.smembers(f"cities:{country_code.upper()}")
    return json_response(sorted(list(cities)))

@app.route("/states/<country_code>", methods=["GET"])
def get_states(country_code):
    states_raw = redis_client.smembers(f"states:{country_code.upper()}")
    states = [orjson.loads(s) for s in states_raw]
    states.sort(key=lambda x: x["name"])
    return json_response(states)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
