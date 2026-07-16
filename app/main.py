"""
DevOps Learning Tracker — the "kitchen".
Items now live in Redis (shared) instead of in memory (per-pod).
"""

import json
import os
import time
from pathlib import Path

import redis
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="DevOps Learning Tracker")

# Where's Redis? Read from the environment, default to "redis".
# Hardcoding would mean rebuilding the image to change it — this is the
# groundwork for ConfigMaps.
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT_NUMBER", "6379"))
db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

ITEMS_KEY = "items"


def load_items():
    """Read the whole list out of Redis."""
    raw = db.get(ITEMS_KEY)
    return json.loads(raw) if raw else []


def save_items(items):
    """Write the whole list back to Redis."""
    db.set(ITEMS_KEY, json.dumps(items))


# --- Metrics (unchanged) ---
REQUEST_COUNT = Counter(
    "app_requests_total", "Total requests received", ["method", "path"]
)
REQUEST_LATENCY = Histogram(
    "app_request_seconds", "How long requests took", ["path"]
)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    seconds = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(seconds)
    return response


@app.get("/", response_class=HTMLResponse)
def home():
    return Path(__file__).parent.joinpath("static/index.html").read_text()


@app.get("/api/items")
def list_items():
    return load_items()


@app.post("/api/items")
async def add_item(request: Request):
    data = await request.json()
    items = load_items()
    item = {"id": len(items) + 1, "text": data["text"], "done": False}
    items.append(item)
    save_items(items)
    return item


@app.post("/api/items/{item_id}/toggle")
def toggle_item(item_id: int):
    items = load_items()
    for item in items:
        if item["id"] == item_id:
            item["done"] = not item["done"]
            save_items(items)
            return item
    return Response(status_code=404)


# --- Health endpoints ---

@app.get("/healthz")
def healthz():
    """LIVENESS: am *I* broken? Checks nothing but itself.
    Deliberately does NOT touch Redis — if it did, a Redis blip would
    make K8s kill every pod in the fleet."""
    return {"status": "alive"}


@app.get("/ready")
def ready():
    """READINESS: can I actually serve? Checks Redis, because without it
    this pod can't do its job. Failing here removes the pod from the
    Service — it stays alive and rejoins when Redis recovers."""
    try:
        db.ping()
        return {"status": "ready"}
    except Exception:
        return Response(status_code=503, content="redis unreachable")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
