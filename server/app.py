import os
import sys

# Safely prioritize local package paths to prevent import errors with pre-installed packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Also add extracted core if it exists
extract_path = os.path.join(root_dir, "openenv_core_extract")
if os.path.exists(extract_path) and extract_path not in sys.path:
    sys.path.insert(0, extract_path)

import argparse
from openenv.core.env_server.http_server import create_app
from env import Environment, TicketTriageAction, TicketTriageObservation

app = create_app(
    Environment,
    TicketTriageAction,
    TicketTriageObservation,
    env_name="ticket_triage",
    max_concurrent_envs=1,
)

@app.get("/")
def read_root():
    return {"status": "ok"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
