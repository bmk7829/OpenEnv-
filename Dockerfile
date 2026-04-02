FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Valid openenv spaces need to be able to be run somehow, wait openenv sets the FASTAPI port usually internally depending on the library.
# We will just expose standard space port 7860
EXPOSE 7860

# The standard command to run an openenv api server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
