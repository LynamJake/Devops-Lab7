import json
import os
import time

import redis
from flask import Flask

app = Flask(__name__)

# Docker Compose sets REDIS_HOST=redis-server (see compose.yaml).
# In Kubernetes (Lab 7) it isn't set, so it falls back to the service name
# "the-redis-server" from redis-service.yaml.
REDIS_HOST = os.environ.get("REDIS_HOST", "the-redis-server")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

CACHE_SECONDS = 600  # 10 minutes


def page(title, body):
    """Build the HTML for a page (this is the 'expensive' part we cache)."""
    return f"""<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body>
  <nav><a href="/">Home</a> | <a href="/about">About</a> | <a href="/contact">Contact</a></nav>
  <h1>{title}</h1>
  {body}
  <p><small>Generated at {time.strftime('%H:%M:%S')}</small></p>
</body>
</html>"""


@app.route("/")
def home():
    data = r.get("home")
    if data is not None:
        data = json.loads(data)
        # 600 seconds == 10 minutes
        if time.time() - data["time"] <= CACHE_SECONDS:
            return data["html"]

    data = page("Home", "<p>Welcome to my Flask app, now cached with Redis!</p>")
    r.set("home", json.dumps({"html": data, "time": time.time()}))
    return data


@app.route("/about")
def about():
    data = r.get("about")
    if data is not None:
        data = json.loads(data)
        if time.time() - data["time"] <= CACHE_SECONDS:
            return data["html"]

    data = page("About", "<p>This app runs Flask and Redis in separate containers.</p>")
    r.set("about", json.dumps({"html": data, "time": time.time()}))
    return data


@app.route("/contact")
def contact():
    data = r.get("contact")
    if data is not None:
        data = json.loads(data)
        if time.time() - data["time"] <= CACHE_SECONDS:
            return data["html"]

    data = page("Contact", "<p>Email: someone@example.com</p>")
    r.set("contact", json.dumps({"html": data, "time": time.time()}))
    return data


if __name__ == "__main__":
    # 0.0.0.0 so the app is reachable from outside the container
    app.run(host="0.0.0.0", port=5000)