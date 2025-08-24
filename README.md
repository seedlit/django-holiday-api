

# Holiday Planner API (Backend)

This is a Django REST Framework backend for planning holidays:
users can create destinations, build travel schedules, and see weather forecasts at each stop.

---

## Features
- **Destinations API**: create/list destinations with search filter.
- **Schedules API**: create schedules with ordered stops and retrieve them with weather summaries.
- **Geocoding API**: search city names (via Open-Meteo Geocoding).
- **Weather API**: fetch daily forecasts (via Open-Meteo Forecast).
- **Weather in Schedules**: schedule detail includes summarized forecast (temp, precipitation, wind, humidity).
- **Throttling**: rate limiting on geocode & weather endpoints.
- **Dockerized**: runs with Postgres in Docker Compose, SQLite fallback available.
- **Tested**: automated pytest suite with mocked APIs.

---

## Setup

### 1. Clone and setup env
```bash
git clone https://github.com/seedlit/django-holiday-api.git
cd django-holiday-api
cp .env.example .env
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

* App runs on: [http://localhost:8000](http://localhost:8000)
* Health check: [http://localhost:8000/health/](http://localhost:8000/health/)


## API Endpoints: sample requests and responses
Try out the following endpoints after running `docker-compose up`
### Health
```bash
curl -X GET http://localhost:8000/health/
```
response:
```bash
{"status": "ok"}
```

### Destinations
**Create a Destination**
```bash
curl -X POST http://localhost:8000/api/v1/destinations/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Berlin", "latitude": 52.52, "longitude": 13.405, "country": "Germany"}'
```
response:
```bash
{"id":23,"name":"Berlin","latitude":52.52,"longitude":13.405,"country":"Germany"}
```

**List destinations**
```bash
curl -X GET http://localhost:8000/api/v1/destinations/
```
response:
```bash
{"count":1,"next":null,"previous":null,"results":[{"id":23,"name":"Berlin","latitude":52.52,"longitude":13.405,"country":"Germany"}]}
```

**Filter destinations**
```bash
curl -X GET "http://localhost:8000/api/v1/destinations/?q=ber"
```
response:
```bash
{"count":1,"next":null,"previous":null,"results":[{"id":23,"name":"Berlin","latitude":52.52,"longitude":13.405,"country":"Germany"}]}
```

### Geocode
**Geocode a city name**
```bash
curl -X POST http://localhost:8000/api/v1/geocode/ \
     -H "Content-Type: application/json" \
     -d '{"query": "Berlin"}'
```
response:
```bash
{"name":"Berlin","latitude":52.52437,"longitude":13.41053,"country":"Germany"}
```

### Weather
**Preview weather for a location**
```bash
curl -X GET "http://localhost:8000/api/v1/weather/preview?lat=52.52&lon=13.405&start=2025-09-01&end=2025-09-03"
```
response:
```bash
{"summary":{"avg_temp_c":17.78333333333333,"max_precip_mm":0.9,"avg_wind_speed_kmh":25.7,"avg_humidity_percent":81.33333333333333},"raw":{"time":["2025-09-01","2025-09-02","2025-09-03"],"temperature_2m_max":[23.2,19.0,20.6],"temperature_2m_min":[15.6,13.6,14.7],"precipitation_sum":[0.0,0.9,0.3],"windspeed_10m_max":[23.0,24.1,30.0],"relative_humidity_2m_max":[79,83,82]}}
```

### Schedules
**Create a schedule with items**
```bash
curl -X POST http://localhost:8000/api/v1/schedules/ \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Euro hop",
           "items": [
             {"destination_id": 1, "start_date": "2025-09-01", "end_date": "2025-09-03"},
             {"destination_id": 2, "start_date": "2025-09-04", "end_date": "2025-09-07"}
           ]
         }'
```
response:
```bash
{"id":11,"name":"Euro hop","created_at":"2025-08-24T14:56:21.788278Z","items":[{"id":21,"destination":{"id":1,"name":"Berlin","latitude":34.0,"longitude":44.0,"country":""},"start_date":"2025-09-01","end_date":"2025-09-03","order_index":0,"weather_summary":{"avg_temp_c":36.233333333333334,"max_precip_mm":0.0,"avg_wind_speed_kmh":20.5,"avg_humidity_percent":26.666666666666668}},{"id":22,"destination":{"id":2,"name":"Berlin","latitude":52.52,"longitude":13.405,"country":"Germany"},"start_date":"2025-09-04","end_date":"2025-09-07","order_index":1,"weather_summary":{"avg_temp_c":19.15,"max_precip_mm":1.2,"avg_wind_speed_kmh":16.975,"avg_humidity_percent":75.5}}]}
```

**Get schedule detail**
```bash
curl -X GET http://localhost:8000/api/v1/schedules/1/

```
response:
```bash
{"id":1,"name":"Euro hop","created_at":"2025-08-24T13:26:12.477796Z","items":[{"id":1,"destination":{"id":1,"name":"Berlin","latitude":34.0,"longitude":44.0,"country":""},"start_date":"2025-09-01","end_date":"2025-09-03","order_index":0,"weather_summary":{"avg_temp_c":36.233333333333334,"max_precip_mm":0.0,"avg_wind_speed_kmh":20.5,"avg_humidity_percent":26.666666666666668}},{"id":2,"destination":{"id":2,"name":"Berlin","latitude":52.52,"longitude":13.405,"country":"Germany"},"start_date":"2025-09-04","end_date":"2025-09-07","order_index":1,"weather_summary":{"avg_temp_c":19.15,"max_precip_mm":1.2,"avg_wind_speed_kmh":16.975,"avg_humidity_percent":75.5}}]}
```

### Throttling Example (429 Too Many Requests)

If you exceed the configured rate limit (e.g. 10 requests per minute for geocode), the API responds with HTTP 429 Too Many Requests:

```bash
# Make 11 quick requests in a row to trigger throttling
for i in {1..11}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
       -X POST http://localhost:8000/api/v1/geocode/ \
       -H "Content-Type: application/json" \
       -d '{"query": "Berlin"}'
done
```

---

### 4. Run tests

```bash
docker-compose run --rm web pytest -v -m "not integration"
```


* Full run output is saved to [`test_output.txt`](./test_output.txt).

---

## Notes

* Uses [Open-Meteo](https://open-meteo.com/) APIs for geocoding & forecast.
* Rate limits: 10/min per scope (configurable).


---

## Limitations / Wishlist
- No persistent weather caching (each GET hits API) --> Cache weather responses
- No user accounts / auth
- get rid of requirements.txt and soley rely on uv
- Swagger / OpenAPI schema generation
- cloud deployment for playing around in real time
- isort pre-commit hooks failing - resolve the issue

---
## Known Bugs
- None blocking core functionality at time of implementation.
