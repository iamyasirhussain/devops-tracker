# --- Start from a pre-made base: a mini Linux with Python already inside. ---
# "slim" = a smaller version (fewer extras) → smaller image, less to attack.
FROM python:3.12-slim

# --- Set the working folder inside the box. Everything below happens here. ---
WORKDIR /app

# --- Copy ONLY the grocery list first (not the whole app yet). ---
# Why just this? So Docker can reuse cached installs when only code changes.
# (We'll see this caching magic when we rebuild.)
COPY requirements.txt .

# --- Install the 3 libraries inside the box. ---
# --no-cache-dir: don't keep pip's download cache → smaller image.
RUN pip install --no-cache-dir -r requirements.txt

# --- NOW copy the rest of the app code into the box. ---
COPY app/ ./app/

# --- Tell Docker the app listens on port 8000 (documentation for humans). ---
EXPOSE 8000

# --- The command that runs when the box starts. ---
# host 0.0.0.0 = accept traffic from outside the box (same reason as before).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
