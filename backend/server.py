from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Character(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    occupation: str
    current_health_status: str
    insurance_choice: Optional[str] = None

class InsuranceOption(BaseModel):
    id: str
    name: str
    type: str  # "basic" or "enhanced"
    monthly_premium: float
    annual_deductible: float
    copayment_percentage: float
    coverage_limit: float
    key_benefits: List[str]
    
class GameState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    current_chapter: int
    characters: List[Character]
    completed_decisions: Dict[str, str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Decision(BaseModel):
    character_id: str
    insurance_option_id: str
    reasoning: Optional[str] = None

class Scenario(BaseModel):
    id: str
    title: str
    description: str
    medical_situation: str
    treatment_cost: float
    urgency_level: str  # "low", "medium", "high"
    
class DecisionCreate(BaseModel):
    session_id: str
    decision: Decision

class GameStateCreate(BaseModel):
    session_id: str

# Game Data
INSURANCE_OPTIONS = [
    InsuranceOption(
        id="medishield_basic",
        name="MediShield Life (Basic)",
        type="basic",
        monthly_premium=150.0,
        annual_deductible=3000.0,
        copayment_percentage=10.0,
        coverage_limit=150000.0,
        key_benefits=[
            "Basic hospital coverage",
            "Subsidized ward coverage",
            "Emergency treatment",
            "Day surgery procedures"
        ]
    ),
    InsuranceOption(
        id="integrated_shield",
        name="Integrated Shield Plan",
        type="enhanced",
        monthly_premium=450.0,
        annual_deductible=1000.0,
        copayment_percentage=5.0,
        coverage_limit=1000000.0,
        key_benefits=[
            "Private hospital coverage",
            "Specialist consultations",
            "Advanced treatments",
            "Overseas emergency coverage",
            "Cancer treatment coverage"
        ]
    )
]

CHARACTERS_DATA = [
    Character(
        id="alex",
        name="Alex",
        age=25,
        occupation="Software Developer",
        current_health_status="Generally healthy, occasional stress"
    ),
    Character(
        id="jamie",
        name="Jamie", 
        age=28,
        occupation="Marketing Executive",
        current_health_status="Active lifestyle, family history of diabetes"
    )
]

SCENARIOS = [
    Scenario(
        id="appendix_surgery",
        title="Emergency Appendectomy",
        description="Sudden severe abdominal pain requiring immediate surgery",
        medical_situation="Emergency appendix removal with 3 days hospital stay",
        treatment_cost=25000.0,
        urgency_level="high"
    ),
    Scenario(
        id="cancer_diagnosis",
        title="Cancer Diagnosis",
        description="Routine check-up reveals early stage cancer requiring treatment",
        medical_situation="Cancer treatment including chemotherapy and specialist care",
        treatment_cost=180000.0,
        urgency_level="high"
    ),
    Scenario(
        id="broken_arm",
        title="Broken Arm",
        description="Accident results in fractured arm requiring surgery and physiotherapy",
        medical_situation="Orthopedic surgery with follow-up treatment",
        treatment_cost=15000.0,
        urgency_level="medium"
    )
]

# Routes
@api_router.get("/")
async def root():
    return {"message": "MediShield Story Game API"}

@api_router.get("/insurance-options", response_model=List[InsuranceOption])
async def get_insurance_options():
    return INSURANCE_OPTIONS

@api_router.get("/characters", response_model=List[Character])
async def get_characters():
    return CHARACTERS_DATA

@api_router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios():
    return SCENARIOS

@api_router.post("/game/start", response_model=GameState)
async def start_game(game_data: GameStateCreate):
    # Create new game state
    game_state = GameState(
        session_id=game_data.session_id,
        current_chapter=1,
        characters=CHARACTERS_DATA.copy(),
        completed_decisions={}
    )
    
    # Save to database
    await db.game_states.insert_one(game_state.dict())
    return game_state

@api_router.get("/game/{session_id}", response_model=GameState)
async def get_game_state(session_id: str):
    game_state = await db.game_states.find_one({"session_id": session_id})
    if not game_state:
        raise HTTPException(status_code=404, detail="Game session not found")
    return GameState(**game_state)

@api_router.post("/game/decision")
async def make_decision(decision_data: DecisionCreate):
    # Find game state
    game_state = await db.game_states.find_one({"session_id": decision_data.session_id})
    if not game_state:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Update character insurance choice
    for character in game_state["characters"]:
        if character["id"] == decision_data.decision.character_id:
            character["insurance_choice"] = decision_data.decision.insurance_option_id
            break
    
    # Update completed decisions
    game_state["completed_decisions"][decision_data.decision.character_id] = decision_data.decision.insurance_option_id
    
    # Save updated state
    await db.game_states.update_one(
        {"session_id": decision_data.session_id},
        {"$set": game_state}
    )
    
    return {"message": "Decision recorded successfully"}

@api_router.post("/game/calculate-outcome")
async def calculate_outcome(session_id: str, scenario_id: str):
    # Get game state
    game_state = await db.game_states.find_one({"session_id": session_id})
    if not game_state:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Find scenario
    scenario = next((s for s in SCENARIOS if s.id == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Calculate outcomes for each character
    outcomes = {}
    for character in game_state["characters"]:
        if character["insurance_choice"]:
            insurance = next((ins for ins in INSURANCE_OPTIONS if ins.id == character["insurance_choice"]), None)
            if insurance:
                # Calculate out-of-pocket cost
                deductible_cost = min(insurance.annual_deductible, scenario.treatment_cost)
                remaining_cost = max(0, scenario.treatment_cost - insurance.annual_deductible)
                copayment_cost = remaining_cost * (insurance.copayment_percentage / 100)
                total_out_of_pocket = deductible_cost + copayment_cost
                
                # Check if within coverage limit
                if scenario.treatment_cost > insurance.coverage_limit:
                    excess_cost = scenario.treatment_cost - insurance.coverage_limit
                    total_out_of_pocket += excess_cost
                
                outcomes[character["id"]] = {
                    "character_name": character["name"],
                    "insurance_plan": insurance.name,
                    "total_treatment_cost": scenario.treatment_cost,
                    "out_of_pocket_cost": total_out_of_pocket,
                    "insurance_covered": scenario.treatment_cost - total_out_of_pocket,
                    "financial_impact": "Low" if total_out_of_pocket < 5000 else "Medium" if total_out_of_pocket < 20000 else "High"
                }
    
    return {
        "scenario": scenario.dict(),
        "outcomes": outcomes
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()