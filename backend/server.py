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
    lifestyle: str
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
    category: str  # "emergency", "routine", "preventive", "specialist"
    age_relevance: str  # "high", "medium", "low"
    
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
            "Day surgery procedures",
            "Basic specialist consultations"
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
            "Cancer treatment coverage",
            "Mental health support",
            "Dental & optical coverage",
            "Maternity benefits"
        ]
    )
]

CHARACTERS_DATA = [
    Character(
        id="alex",
        name="Alex",
        age=25,
        occupation="Software Developer",
        current_health_status="Generally healthy, occasional stress",
        lifestyle="Sedentary work, exercises 2x weekly, healthy diet"
    ),
    Character(
        id="jamie",
        name="Jamie", 
        age=28,
        occupation="Marketing Executive",
        current_health_status="Active lifestyle, family history of diabetes",
        lifestyle="Very active, plays sports regularly, social drinker"
    )
]

SCENARIOS = [
    Scenario(
        id="appendix_surgery",
        title="Emergency Appendectomy",
        description="Sudden severe abdominal pain requiring immediate surgery",
        medical_situation="Emergency appendix removal with 3 days hospital stay",
        treatment_cost=25000.0,
        urgency_level="high",
        category="emergency",
        age_relevance="high"
    ),
    Scenario(
        id="cancer_diagnosis",
        title="Early Cancer Diagnosis",
        description="Routine check-up reveals early stage cancer requiring treatment",
        medical_situation="Cancer treatment including chemotherapy and specialist care over 6 months",
        treatment_cost=180000.0,
        urgency_level="high",
        category="specialist",
        age_relevance="medium"
    ),
    Scenario(
        id="broken_arm",
        title="Sports Injury - Broken Arm",
        description="Weekend basketball game results in fractured arm",
        medical_situation="Orthopedic surgery with 3 months physiotherapy",
        treatment_cost=15000.0,
        urgency_level="medium",
        category="emergency",
        age_relevance="high"
    ),
    Scenario(
        id="dental_emergency",
        title="Dental Emergency",
        description="Severe tooth pain requires immediate root canal and crown",
        medical_situation="Emergency dental treatment with follow-up procedures",
        treatment_cost=3500.0,
        urgency_level="medium",
        category="routine",
        age_relevance="high"
    ),
    Scenario(
        id="mental_health",
        title="Mental Health Support",
        description="Work stress leads to anxiety requiring professional counseling",
        medical_situation="6 months of therapy sessions with psychiatrist consultation",
        treatment_cost=4800.0,
        urgency_level="medium",
        category="specialist",
        age_relevance="high"
    ),
    Scenario(
        id="maternity_care",
        title="Maternity & Childbirth",
        description="Pregnancy requires prenatal care and delivery",
        medical_situation="Complete maternity package with specialist care",
        treatment_cost=12000.0,
        urgency_level="low",
        category="routine",
        age_relevance="high"
    ),
    Scenario(
        id="eye_surgery",
        title="LASIK Eye Surgery",
        description="Corrective eye surgery to eliminate dependence on glasses",
        medical_situation="Bilateral LASIK surgery with follow-up care",
        treatment_cost=8000.0,
        urgency_level="low",
        category="routine",
        age_relevance="medium"
    ),
    Scenario(
        id="heart_condition",
        title="Heart Condition Discovery",
        description="Routine health screening reveals heart irregularity",
        medical_situation="Cardiac tests, specialist consultation, and ongoing monitoring",
        treatment_cost=35000.0,
        urgency_level="high",
        category="specialist",
        age_relevance="medium"
    ),
    Scenario(
        id="accident_injury",
        title="Traffic Accident",
        description="Minor traffic accident results in multiple injuries",
        medical_situation="Emergency room treatment, X-rays, and physical therapy",
        treatment_cost=8500.0,
        urgency_level="high",
        category="emergency",
        age_relevance="high"
    ),
    Scenario(
        id="chronic_condition",
        title="Chronic Condition Diagnosis",
        description="Diagnosed with chronic condition requiring ongoing treatment",
        medical_situation="Long-term medication and regular specialist visits",
        treatment_cost=18000.0,
        urgency_level="medium",
        category="specialist",
        age_relevance="medium"
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

@api_router.get("/scenarios/random/{count}")
async def get_random_scenarios(count: int = 3):
    import random
    if count > len(SCENARIOS):
        count = len(SCENARIOS)
    return random.sample(SCENARIOS, count)

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
                
                # Determine financial impact
                if total_out_of_pocket < 2000:
                    financial_impact = "Low"
                elif total_out_of_pocket < 10000:
                    financial_impact = "Medium"
                else:
                    financial_impact = "High"
                
                outcomes[character["id"]] = {
                    "character_name": character["name"],
                    "insurance_plan": insurance.name,
                    "total_treatment_cost": scenario.treatment_cost,
                    "out_of_pocket_cost": total_out_of_pocket,
                    "insurance_covered": scenario.treatment_cost - total_out_of_pocket,
                    "financial_impact": financial_impact,
                    "monthly_premium": insurance.monthly_premium,
                    "annual_premium": insurance.monthly_premium * 12
                }
    
    return {
        "scenario": scenario.dict(),
        "outcomes": outcomes
    }

@api_router.get("/stats/comparison")
async def get_insurance_comparison_stats():
    """Get detailed comparison statistics between insurance plans"""
    basic_plan = INSURANCE_OPTIONS[0]
    enhanced_plan = INSURANCE_OPTIONS[1]
    
    comparison_data = {
        "basic_plan": {
            "name": basic_plan.name,
            "monthly_cost": basic_plan.monthly_premium,
            "annual_cost": basic_plan.monthly_premium * 12,
            "deductible": basic_plan.annual_deductible,
            "copayment": basic_plan.copayment_percentage,
            "coverage_limit": basic_plan.coverage_limit
        },
        "enhanced_plan": {
            "name": enhanced_plan.name,
            "monthly_cost": enhanced_plan.monthly_premium,
            "annual_cost": enhanced_plan.monthly_premium * 12,
            "deductible": enhanced_plan.annual_deductible,
            "copayment": enhanced_plan.copayment_percentage,
            "coverage_limit": enhanced_plan.coverage_limit
        },
        "cost_difference": {
            "monthly": enhanced_plan.monthly_premium - basic_plan.monthly_premium,
            "annual": (enhanced_plan.monthly_premium - basic_plan.monthly_premium) * 12
        }
    }
    
    return comparison_data

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