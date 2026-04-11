import os
import json
import sys
from typing import List, Optional, Any
from openai import OpenAI
from env import Environment, TicketTriageAction

# Environment variables will be fetched dynamically inside the action generator
# to prevent import-time environment variable freezing and ensure late-injected
# Phase 2 proxy credentials are unequivocally captured.

MAX_STEPS = 5
TEMPERATURE = 0.7
MAX_TOKENS = 500

SYSTEM_PROMPT = """
You are acting as an AI Level 1 Dispatcher for a customer support ticketing system.
You will be provided with the current ticket state and feedback from your last action.
Your goal is to parse the ticket content, and carefully route the ticket by setting its Category, Priority, and Team, and then submitting it.

Categories: 'Technical', 'Billing', 'Security', 'Sales'
Priorities: 'Low', 'Medium', 'High', 'Critical'
Teams: 'L1_Support', 'Billing_Dept', 'Engineering', 'Sales_Team'

Reply ONLY with a valid JSON object representing your Action. Do not include markdown formatting or extra text.
Format:
{
  "category": "<str or null>",
  "priority": "<str or null>",
  "team": "<str or null>",
  "submit": <boolean>
}
"""

def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)

def log_step(step: int, action_str: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_user_prompt(step: int, state: Any, feedback: str) -> str:
    return f'''
Step: {step}
Ticket Subject: {state.subject}
Ticket Body: {state.body}
Current Category: {state.current_category}
Current Priority: {state.current_priority}
Current Team: {state.current_team}
Last Feedback: {feedback}

Provide your next JSON action.
'''

def get_model_action(step: int, state: Any, feedback: str) -> TicketTriageAction:
    user_prompt = build_user_prompt(step, state, feedback)
    
    # Dynamically initialize client exactly as instructed to guarantee 
    # capturing the late-injected platform proxy variables.
    client = OpenAI(base_url=os.environ["API_BASE_URL"], api_key=os.environ["API_KEY"])
    model_name_runtime = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
    
    # Intentionally removing the broad try/except around this network call.
    # If the LLM proxy rejects the request, we want the script to hard-crash 
    # so we can see the exact proxy error in the validator logs instead of 
    # silently exiting and getting a vague "no API calls observed" result.
    completion = client.chat.completions.create(
        model=model_name_runtime,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
    
    text = (completion.choices[0].message.content or "").strip()
    
    # Remove markdown format if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        data = json.loads(text)
    except Exception:
        data = {}
        
    return TicketTriageAction(
        category=data.get('category'),
        priority=data.get('priority'),
        team=data.get('team'),
        submit=data.get('submit', False)
    )

def run_task(task_name: str) -> None:
    env = Environment(task_name=task_name)
    
    rewards: List[float] = []
    steps_taken = 0
    final_score = 0.0
    success = False
    
    # log model correctly with fallback evaluation for stdout parsing
    log_start(task=task_name, env_name="ticket_triage", model=os.environ.get("MODEL_NAME", "gpt-3.5-turbo"))
    
    obs = env.reset()
    last_feedback = obs.feedback
    
    try:
        for step in range(1, MAX_STEPS + 1):
            if env.state.done:
                break
                
            action_obj = get_model_action(step, env.state, last_feedback)
            action_str = action_obj.model_dump_json(exclude_none=True).replace(" ", "")
            
            new_obs = env.step(action_obj)
            reward_val = new_obs.reward
            done = new_obs.done
            
            # if reward is an object, get its value; else use float
            reward = float(reward_val.value) if hasattr(reward_val, "value") else float(reward_val)
            
            rewards.append(reward)
            steps_taken = step
            last_feedback = new_obs.feedback
            
            log_step(step=step, action_str=action_str, reward=reward, done=done, error=None)
            
            if done:
                break
                
        from env import grader
        final_score = grader(env.state)
        success = final_score >= 1.0
        
    finally:
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)

def main():
    tasks = ["easy", "medium", "hard"]
    for task in tasks:
        run_task(task)

if __name__ == "__main__":
    main()
