import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
