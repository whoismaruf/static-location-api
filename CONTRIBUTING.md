# Contributing to Static Location API

Thank you for your interest in enhancing the Static Location API! We welcome extensions to the `data.json` file as well as codebase PRs for the backend.

## Editing Location Data

The core truth of this API sits exclusively inside `data.json`. Any geographical updates (adding cities, correcting states, merging countries) must be executed natively here.

### Rules for `data.json`
1. **JSON Validation**: The file supports deep object nesting. Each primary entry must define `"name"` (mapping to country) and `"iso2"` (mapping to `code`).
2. **States & Cities**: Inside the `"states"` array, each state requires a `"name"`. The system will safely backwards-calculate slugs using this name string (e.g. "New York" -> "new-york"). Cities within the state must sit inside a `"cities"` array as objects which respectively specify their `"name"`.
3. **Array Cleanliness**: Keep arrays uniformly formatted!

### How to test Updates locally
If you modified `data.json` and want to ensure it is structured appropriately:
1. Re-initialize your application via: 
   ```bash
   docker-compose up -d --build --force-recreate web
   ```
2. Test the API paths like `localhost:5000/states/AF` or `localhost:5000/cities/AF` to ensure your newly added blocks render and serialize gracefully.

## Architecture Guidelines

Currently, this API runs completely independently with `Flask`, `orjson`, and standard Redis caching. 

Pull Requests attempting to drift away from this architecture (e.g., adding SQLAlchemy, Django migration systems, heavy Auth libraries) should be opened as a Feature Request/Issue discussion prior to rewriting logic, to ensure we keep the application horizontally scalable and perfectly slim.

Thank you!
