---
title: Openenv Ticket Triage
emoji: 🎟️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
tags: ["openenv"]
---
# Ticket Triage - OpenEnv Benchmark Environment

## Description & Motivation
This environment simulates a real-world customer support scenario. An AI agent is acting as a Level 1 dispatcher. Its goal is to analyze an incoming customer support ticket (including the subject and message body) and perform triage by accurately assigning its `category`, `priority`, and routing it to the proper `team`. 

This is a critical real-world task for many organizations, helping automate the routing of thousands of user requests daily and ensuring critical issues (like security vulnerabilities) are escalated immediately.

## Action & Observation Spaces

### Observation Space
The observation space is represented by the `TicketTriageObservation` model:
- `ticket_id` (str): Unique ticket identifier.
- `subject` (str): The subject line of the ticket.
- `body` (str): The full message body of the ticket.
- `current_category` (str, optional): The currently assigned category.
- `current_priority` (str, optional): The currently assigned priority.
- `current_team` (str, optional): The currently assigned escalation team.
- `feedback` (str): Feedback string about the last action taken.

### Action Space
The agent responds with a `TicketTriageAction` model (JSON object in the baseline):
- `category` (str, optional): Assign the category ('Technical', 'Billing', 'Security', 'Sales').
- `priority` (str, optional): Assign the priority ('Low', 'Medium', 'High', 'Critical').
- `team` (str, optional): Assign the escalation team ('L1_Support', 'Billing_Dept', 'Engineering', 'Sales_Team').
- `submit` (bool): If True, submits the ticket and ends the episode.

## Tasks & Difficulty

The environment features 3 tasks of increasing difficulty, graded from 0.0 to 1.0 based on how closely the assigned properties match the ground truth.

1. **Easy (`easy`)**: Triage a simple password reset request. Very clear indicators for Technical/Low/L1_Support.
2. **Medium (`medium`)**: Triage an angry customer regarding a billing dispute. The emotional tone might distract, but it firmly belongs to Billing/High/Billing_Dept.
3. **Hard (`hard`)**: Triage a critical security vulnerability report (a zero-day unauthenticated RCE). Requires the agent to recognize the severity and route it directly to Engineering with Critical priority.

## Setup & Usage Instructions

### Docker Setup
To build the Docker container and test it using the local HF Space equivalent port:
```bash
docker build -t openenv-ticket-triage .
docker run -p 7860:7860 openenv-ticket-triage
```

### Local Setup
Ensure Python 3.10+ is installed.
```bash
pip install -r requirements.txt
```

To validate the environment locally:
```bash
openenv validate
```

To run the baseline inference:
```bash
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export API_BASE_URL="https://router.huggingface.co/v1"
export HF_TOKEN="your_hf_token_here"
python inference.py
```

## Baseline Scores
Running the baseline `inference.py` using `Qwen/Qwen2.5-72B-Instruct` yields the following expected scores:
- **Easy**: 1.0 (100% correct)
- **Medium**: 1.0 (100% correct)
- **Hard**: 1.0 (100% correct)
