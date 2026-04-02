from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Tuple

class TicketTriageAction(BaseModel):
    category: Optional[str] = Field(None, description="Set the category of the ticket. Options: 'Technical', 'Billing', 'Security', 'Sales'")
    priority: Optional[str] = Field(None, description="Set the priority of the ticket. Options: 'Low', 'Medium', 'High', 'Critical'")
    team: Optional[str] = Field(None, description="Set the escalation team. Options: 'L1_Support', 'Billing_Dept', 'Engineering', 'Sales_Team'")
    submit: bool = Field(False, description="Set to True to finish triage and close the episode")

class TicketTriageObservation(BaseModel):
    ticket_id: str
    subject: str
    body: str
    current_category: Optional[str] = None
    current_priority: Optional[str] = None
    current_team: Optional[str] = None
    feedback: str = ""

class TicketTriageReward(BaseModel):
    value: float

class TicketTriageState(BaseModel):
    task_id: str
    ticket_id: str
    subject: str
    body: str
    ground_truth_category: str
    ground_truth_priority: str
    ground_truth_team: str
    
    current_category: Optional[str] = None
    current_priority: Optional[str] = None
    current_team: Optional[str] = None
    
    steps_taken: int = 0
    done: bool = False
    
class Environment:
    def __init__(self, task_name: str = "easy"):
        self.task_name = task_name
        self._init_task()
        
    def _init_task(self):
        if self.task_name == "easy":
            self._state = TicketTriageState(
                task_id=self.task_name,
                ticket_id="TKT-1001",
                subject="Forgot my password",
                body="Hi there, I seem to have forgotten my password. Can you please help me reset it? My account email is user@example.com.",
                ground_truth_category="Technical",
                ground_truth_priority="Low",
                ground_truth_team="L1_Support"
            )
        elif self.task_name == "medium":
            self._state = TicketTriageState(
                task_id=self.task_name,
                ticket_id="TKT-2053",
                subject="URGENT: Double charged on my last invoice!",
                body="I just checked my credit card statement and you guys charged me twice for the March billing cycle! Invoice #8482. Fix this immediately or I am reporting fraud.",
                ground_truth_category="Billing",
                ground_truth_priority="High",
                ground_truth_team="Billing_Dept"
            )
        elif self.task_name == "hard":
            self._state = TicketTriageState(
                task_id=self.task_name,
                ticket_id="TKT-9999",
                subject="Critical Unauthenticated RCE zero-day in your main API",
                body="Hello security team. I am a researcher and I found a critical Remote Code Execution vulnerability in your /api/v2/upload endpoint. It does not require authentication. I've attached a proof-of-concept python script. Please patch this ASAP before it gets exploited in the wild.",
                ground_truth_category="Security",
                ground_truth_priority="Critical",
                ground_truth_team="Engineering"
            )
        else:
            raise ValueError(f"Unknown task: {self.task_name}")

    def reset(self) -> TicketTriageObservation:
        self._init_task()
        return self._get_obs(feedback="Ticket opened. Please route this ticket correctly.")

    def _get_obs(self, feedback: str = "") -> TicketTriageObservation:
        return TicketTriageObservation(
            ticket_id=self._state.ticket_id,
            subject=self._state.subject,
            body=self._state.body,
            current_category=self._state.current_category,
            current_priority=self._state.current_priority,
            current_team=self._state.current_team,
            feedback=feedback
        )
        
    def _calculate_potential(self, state: TicketTriageState) -> float:
        score = 0.0
        if state.current_category == state.ground_truth_category:
            score += 0.3
        if state.current_priority == state.ground_truth_priority:
            score += 0.3
        if state.current_team == state.ground_truth_team:
            score += 0.4
        return score

    def step(self, action: TicketTriageAction) -> Tuple[TicketTriageObservation, TicketTriageReward, bool, Dict[str, Any]]:
        self._state.steps_taken += 1
        
        if self._state.done:
            return self._get_obs("Episode already done."), TicketTriageReward(value=0.0), True, {}
            
        old_potential = self._calculate_potential(self._state)
        
        feedback_msgs = []
        if action.category and action.category != self._state.current_category:
            self._state.current_category = action.category
            feedback_msgs.append(f"Category set to {action.category}")
            
        if action.priority and action.priority != self._state.current_priority:
            self._state.current_priority = action.priority
            feedback_msgs.append(f"Priority set to {action.priority}")
            
        if action.team and action.team != self._state.current_team:
            self._state.current_team = action.team
            feedback_msgs.append(f"Team set to {action.team}")
            
        if action.submit:
            self._state.done = True
            feedback_msgs.append("Ticket submitted and routed.")
            
        if not feedback_msgs:
            feedback_msgs.append("No changes made.")
            
        new_potential = self._calculate_potential(self._state)
        reward_value = new_potential - old_potential - 0.01
        
        feedback_str = ". ".join(feedback_msgs)
        obs = self._get_obs(feedback=feedback_str)
        
        return obs, TicketTriageReward(value=float(reward_value)), self._state.done, {}

    def state(self) -> TicketTriageState:
        return self._state

def grader(state: TicketTriageState) -> float:
    score = 0.0
    if state.current_category == state.ground_truth_category:
        score += 0.3
    if state.current_priority == state.ground_truth_priority:
        score += 0.3
    if state.current_team == state.ground_truth_team:
        score += 0.4
    return score
