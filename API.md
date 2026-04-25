# Static Location API Documentation

This API serves robust geographical structures (countries, states, and cities) using a high-performance HTTP GET implementation backed by memory-optimized Redis mapping sets.

## Base URL
When run natively via Docker Compose, endpoints exist directly on your mapped edge:
`http://localhost:5000`

---

## 🔗 Endpoints

### 1. Health Status
Check if the web-worker container has surfaced properly.
- **URL**: `/`
- **Method**: `GET`
- **Returns**: `{"status": "healthy"}`

---

### 2. Get All Countries
Renders the list containing the minimized core country nodes generated from the base indices.
- **URL**: `/countries`
- **Method**: `GET`
- **Response**:
```json
[
  { "country": "Afghanistan", "code": "AF" },
  { "country": "United States", "code": "US" }
]
```

---

### 3. Get Full Country Profile
Renders the *complete, unmodified, raw JSON entity* stored natively inside the origin dataset. Includes all nested variables ranging from `timezone` loops, `currency_symbol` mappings, to `population` sizes!
- **URL**: `/country/<country_code>`
- **Method**: `GET`
- **Path Params**: 
  - `<country_code>` (e.g. `AF` for Afghanistan, `US` for United States)
- **Response**:
```json
{
  "id": 1,
  "name": "Afghanistan",
  "iso2": "AF",
  "currency": "AFN",
  "timezones": [...],
  "states": [...]
}
```

---

### 4. Get States For Country
Fetches the designated child `states` cleanly attached underneath a given country. Note that the object exposes the system's `slug` generation logic, which is used natively for querying child locations!
- **URL**: `/states/<country_code>`
- **Method**: `GET`
- **Path Params**:
  - `<country_code>` (e.g. `AF`)
- **Response**:
```json
[
  { "name": "Badakhshan", "slug": "badakhshan" },
  { "name": "Kabul", "slug": "kabul" }
]
```

---

### 5. Get Cities (Query Parameters)
Dynamically fetch arrays of nested `cities` using flexible and interchangeable HTTP query parameters. All cities are sorted natively inside the response layer!

- **URL**: `/cities`
- **Method**: `GET`
- **Query Params**:
  *(At least 1 required)*
  - `country`: The generic `code` identifier of a country (e.g. `AF`).
  - `state`: The computational `slug` calculated for a state (e.g. `badakhshan`).

#### Common Application Examples

**Lookup by State exclusively:**
`GET /cities?state=badakhshan`
Instantly outputs all matching cities locally structured under that state globally.
```json
["Ashkāsham", "Fayzabad", "Jurm", "Wākhān"]
```

**Lookup by Country exclusively:**
`GET /cities?country=AF`
Returns a comprehensively flattened pool of *all* child cities housed deeply inside the selected country core, securely parsing past boundaries to merge the array organically!
```json
["Ashkāsham", "Bāmyān", "Herāt", "Kabul", "Lashkar Gāh", ...]
```

**Intersection Lookup by exact coordinates:**
`GET /cities?country=AF&state=badakhshan`
Strictest validation structure, exclusively pulling sets that guarantee exact matches! (Helpful if navigating a collision where similar state slugs overlap in different countries).

---

### HTTP Errors Models
If an endpoint does not find a match or requires explicit query parameters, execution breaks safely to return natively categorized HTTP `400` or HTTP `404` error objects dynamically. 
```json
{ "error": "Missing params. Use ?country= or ?state=" }
```
