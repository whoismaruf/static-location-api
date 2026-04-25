import os
import json
import orjson
import redis
from flask import Flask, Response, request

app = Flask(__name__)

# Redis configuration
# Initialize Redis Connection Pool natively hardcoded
redis_pool = redis.ConnectionPool(
    host="redis", port=6379, db=0, decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)


def load_data_to_redis():
    """Load JSON data to Redis database dynamically at startup."""
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Fast and clean flush to prevent orphan keys natively
        redis_client.flushdb()

        for item in data:
            country_name = item.get("name")
            country_code = item.get("iso2")
            if not country_code or not country_name:
                continue
                
            # Full structured country storage for the deep-dive endpoint
            redis_client.set(f"country_raw:{country_code.upper()}", orjson.dumps(item))

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
                    
                # New data source lacks slugs, safely generate dynamically
                state_slug = state_obj.get("slug")
                if not state_slug:
                    state_slug = state_name.lower().replace(" ", "-")
                else:
                    state_slug = state_slug.lower()
                
                state_data_list.append(orjson.dumps({"name": state_name, "slug": state_slug}))
                
                # Handle objects in cities arrays
                cities_complex = state_obj.get("cities") or []
                cities = []
                for city_obj in cities_complex:
                    if city_obj and city_obj.get("name"):
                        cities.append(city_obj.get("name"))
                        
                all_cities.extend(cities)
                
                if cities:
                    redis_client.sadd(f"cities:{country_code}:{state_slug}", *cities)
                    redis_client.sadd(f"cities_by_state:{state_slug}", *cities)
                
            if state_data_list:
                redis_client.sadd(f"states:{country_code}", *state_data_list)
                
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
    countries_raw = redis_client.smembers("countries")
    countries = [orjson.loads(c) for c in countries_raw]
    countries.sort(key=lambda x: x["country"])
    return json_response(countries)


@app.route("/country/<country_code>", methods=["GET"])
def get_country(country_code):
    raw_data = redis_client.get(f"country_raw:{country_code.upper()}")
    if not raw_data:
        return json_response({"error": "Country not found"}, status=404)
    # The JSON is already parsed natively by orjson upon cache initialization
    return Response(raw_data, status=200, mimetype="application/json")


@app.route("/states/<country_code>", methods=["GET"])
def get_states(country_code):
    states_raw = redis_client.smembers(f"states:{country_code.upper()}")
    states = [orjson.loads(s) for s in states_raw]
    states.sort(key=lambda x: x["name"])
    return json_response(states)


@app.route("/cities", methods=["GET"])
def get_cities():
    country = request.args.get("country")
    state = request.args.get("state")
    
    cities = []
    if country and state:
        cities = redis_client.smembers(f"cities:{country.upper()}:{state.lower()}")
    elif country:
        cities = redis_client.smembers(f"cities:{country.upper()}")
    elif state:
        cities = redis_client.smembers(f"cities_by_state:{state.lower()}")
    else:
        return json_response({"error": "Missing params. Use ?country= or ?state="}, status=400)
        
    return json_response(sorted(list(cities)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
