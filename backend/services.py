import requests
import time

MONITORED_SERVICES = [
    {"id": 1, "name": "JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1"},
    {"id": 2, "name": "Open-Meteo Weather", "url": "https://api.open-meteo.com/v1/forecast?latitude=17.38&longitude=78.48&current_weather=true"},
    {"id": 3, "name": "GitHub API", "url": "https://api.github.com"},
]

def check_service(service):
    start = time.time()
    try:
        response = requests.get(service["url"], timeout=5)
        response_time_ms = round((time.time() - start) * 1000)
        status = "up" if response.status_code < 400 else "down"
        return {
            "id": service["id"],
            "name": service["name"],
            "status": status,
            "status_code": response.status_code,
            "response_time_ms": response_time_ms
        }
    except requests.exceptions.RequestException:
        response_time_ms = round((time.time() - start) * 1000)
        return {
            "id": service["id"],
            "name": service["name"],
            "status": "down",
            "status_code": None,
            "response_time_ms": response_time_ms
        }

def check_all_services():
    return [check_service(s) for s in MONITORED_SERVICES]