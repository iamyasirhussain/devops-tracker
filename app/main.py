"""
DevOps Learning Tracker — the "kitchen".
Handles requests, keeps a list of learning items, and keeps a tally
sheet at /metrics for Prometheus to read later.
"""

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Open the restaurant.
app = FastAPI(title="DevOps Learning Tracker")

# Our "order book": a simple list kept in memory.
# It clears when the app restarts — we add a real database in Phase 5.
items = []

# --- The tally sheet (Prometheus metrics) ---
# Counter: a number that only goes up — how many requests we've served.
REQUEST_COUNT = Counter(
    "app_requests_total", "Total requests received", ["method", "path"]
)
# Histogram: timing buckets — how long each request took.
REQUEST_LATENCY = Histogram(
    "app_request_seconds", "How long requests took", ["path"]
)

# Runs for EVERY request: like a clipboard by the door that notes each
# order and times it, then lets it through to the kitchen.
@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)          # handle the request
    seconds = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(seconds)
    return response

# --- The dining room: serve the web page at "/" ---
@app.get("/", response_class=HTMLResponse)
def home():
    return Path(__file__).parent.joinpath("static/index.html").read_text()

# --- The order API (what the page talks to) ---
@app.get("/api/items")
def list_items():
    return items

@app.post("/api/items")
async def add_item(request: Request):
    data = await request.json()
    item = {"id": len(items) + 1, "text": data["text"], "done": False}
    items.append(item)
    return item

@app.post("/api/items/{item_id}/toggle")
def toggle_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            item["done"] = not item["done"]
            return item
    return Response(status_code=404)

# --- The tally sheet, exposed for Prometheus ---
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
