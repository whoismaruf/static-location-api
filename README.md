# Static Location API

A lightning-fast, static geographic data API built with Flask, heavily optimized with `orjson` and backed by Redis.

This project delivers country, state, and city structures purely through HTTP GET endpoints. Using `data.json` as the unified source of truth, it dynamically populates the Redis cache at bootup, prioritizing zero-overhead queries.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

## Quick Start

1. Review `data.json` - this is the source of truth for geographical data. You can freely edit or augment the nodes before launch.
2. Start the stack:
   ```bash
   docker-compose up -d --build
   ```

The API will instantly serve requests at `http://localhost:5000`.

## API Endpoints

### 1. **Countries**
Fetches a list of all globally recognized countries mapped directly from the `data.json` object.

- **GET** `/countries`
- **Returns:**
```json
[
  { "country": "Afghanistan", "code": "AF" },
  { "country": "United States", "code": "US" }
]
```

### 2. **States**
Fetches the states/regions bound to a specific ISO country code. Slugs are auto-generated natively by parsing the state `name` properties!

- **GET** `/states/<country_code>`
- **Returns:**
```json
[
  { "name": "Badakhshan", "slug": "badakhshan" },
  { "name": "Kabul", "slug": "kabul" }
]
```

### 3. **Cities (Country & State filtering)**
A responsive endpoint that drills down into specific city datasets dynamically.

- **GET** `/cities/<country_code>`
*(Fetches a flat array of ALL cities assigned to the targeted Country)*
- **Returns:** `["Ashkāsham", "Fayzabad", "Kabul", ...]`

- **GET** `/cities/<country_code>/<state_slug>`
*(Narrows the scope strictly to a specified state within the targeted Country)*
- **Returns:** `["Kabul", "Mīr Bachah Kōṯ", "Paghmān"]`

## How it works

The container deploys two resilient services:
- **Web**: A Gunicorn worker running the Flask API utilizing threaded `orjson` serialization and direct Redis pooling.
- **Redis**: An Alpine-based `redis` node mapping out the localized strings as lightning-fast lookup sets.

On initialization, the Python application automatically consumes `data.json`, processing the detailed arrays of city objects into dynamic string lists, generating system slugs, and creating distributed subsets across the Redis layer. Modification is handled purely by rebooting the container!
