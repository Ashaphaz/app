import requests
import unittest
import uuid
import json
import os
from dotenv import load_dotenv

# Load environment variables from frontend/.env
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"

class TestMediShieldStoryGameAPI(unittest.TestCase):
    
    def setUp(self):
        # Generate a unique session ID for each test run
        self.session_id = str(uuid.uuid4())
        
    def test_01_api_health_check(self):
        """Test the basic API health check endpoint"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "MediShield Story Game API")
        print("✅ API health check passed")
        
    def test_02_get_insurance_options(self):
        """Test the insurance options endpoint"""
        response = requests.get(f"{API_URL}/insurance-options")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Should have 2 insurance options
        
        # Verify MediShield Life (Basic) option
        medishield = next((ins for ins in data if ins["id"] == "medishield_basic"), None)
        self.assertIsNotNone(medishield)
        self.assertEqual(medishield["name"], "MediShield Life (Basic)")
        self.assertEqual(medishield["type"], "basic")
        self.assertEqual(medishield["monthly_premium"], 150.0)
        self.assertEqual(medishield["annual_deductible"], 3000.0)
        self.assertEqual(medishield["copayment_percentage"], 10.0)
        self.assertEqual(medishield["coverage_limit"], 150000.0)
        
        # Verify Integrated Shield Plan option
        integrated = next((ins for ins in data if ins["id"] == "integrated_shield"), None)
        self.assertIsNotNone(integrated)
        self.assertEqual(integrated["name"], "Integrated Shield Plan")
        self.assertEqual(integrated["type"], "enhanced")
        self.assertEqual(integrated["monthly_premium"], 450.0)
        self.assertEqual(integrated["annual_deductible"], 1000.0)
        self.assertEqual(integrated["copayment_percentage"], 5.0)
        self.assertEqual(integrated["coverage_limit"], 1000000.0)
        
        print("✅ Insurance options endpoint passed")
        
    def test_03_get_characters(self):
        """Test the characters endpoint"""
        response = requests.get(f"{API_URL}/characters")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Should have 2 characters
        
        # Verify Alex character
        alex = next((char for char in data if char["id"] == "alex"), None)
        self.assertIsNotNone(alex)
        self.assertEqual(alex["name"], "Alex")
        self.assertEqual(alex["age"], 25)
        self.assertEqual(alex["occupation"], "Software Developer")
        
        # Verify Jamie character
        jamie = next((char for char in data if char["id"] == "jamie"), None)
        self.assertIsNotNone(jamie)
        self.assertEqual(jamie["name"], "Jamie")
        self.assertEqual(jamie["age"], 28)
        self.assertEqual(jamie["occupation"], "Marketing Executive")
        
        print("✅ Characters endpoint passed")
        
    def test_04_get_scenarios(self):
        """Test the scenarios endpoint"""
        response = requests.get(f"{API_URL}/scenarios")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)  # Should have 3 scenarios
        
        # Verify appendectomy scenario
        appendix = next((s for s in data if s["id"] == "appendix_surgery"), None)
        self.assertIsNotNone(appendix)
        self.assertEqual(appendix["title"], "Emergency Appendectomy")
        self.assertEqual(appendix["treatment_cost"], 25000.0)
        
        # Verify cancer scenario
        cancer = next((s for s in data if s["id"] == "cancer_diagnosis"), None)
        self.assertIsNotNone(cancer)
        self.assertEqual(cancer["title"], "Cancer Diagnosis")
        self.assertEqual(cancer["treatment_cost"], 180000.0)
        
        # Verify broken arm scenario
        broken_arm = next((s for s in data if s["id"] == "broken_arm"), None)
        self.assertIsNotNone(broken_arm)
        self.assertEqual(broken_arm["title"], "Broken Arm")
        self.assertEqual(broken_arm["treatment_cost"], 15000.0)
        
        print("✅ Scenarios endpoint passed")
        
    def test_05_game_session_management(self):
        """Test game session creation and retrieval"""
        # Create a new game session
        response = requests.post(
            f"{API_URL}/game/start",
            json={"session_id": self.session_id}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], self.session_id)
        self.assertEqual(data["current_chapter"], 1)
        self.assertEqual(len(data["characters"]), 2)
        self.assertEqual(data["completed_decisions"], {})
        
        # Retrieve the game state
        response = requests.get(f"{API_URL}/game/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], self.session_id)
        
        print("✅ Game session management passed")
        
    def test_06_decision_making_system(self):
        """Test the decision making system"""
        # Create a new game session
        response = requests.post(
            f"{API_URL}/game/start",
            json={"session_id": self.session_id}
        )
        self.assertEqual(response.status_code, 200)
        
        # Make a decision for Alex
        alex_decision = {
            "session_id": self.session_id,
            "decision": {
                "character_id": "alex",
                "insurance_option_id": "medishield_basic",
                "reasoning": "Choosing basic coverage to save on premiums"
            }
        }
        response = requests.post(f"{API_URL}/game/decision", json=alex_decision)
        self.assertEqual(response.status_code, 200)
        
        # Make a decision for Jamie
        jamie_decision = {
            "session_id": self.session_id,
            "decision": {
                "character_id": "jamie",
                "insurance_option_id": "integrated_shield",
                "reasoning": "Choosing enhanced coverage for better protection"
            }
        }
        response = requests.post(f"{API_URL}/game/decision", json=jamie_decision)
        self.assertEqual(response.status_code, 200)
        
        # Verify decisions were stored
        response = requests.get(f"{API_URL}/game/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check completed decisions
        self.assertEqual(len(data["completed_decisions"]), 2)
        self.assertEqual(data["completed_decisions"]["alex"], "medishield_basic")
        self.assertEqual(data["completed_decisions"]["jamie"], "integrated_shield")
        
        # Check character insurance choices
        alex = next((char for char in data["characters"] if char["id"] == "alex"), None)
        self.assertEqual(alex["insurance_choice"], "medishield_basic")
        
        jamie = next((char for char in data["characters"] if char["id"] == "jamie"), None)
        self.assertEqual(jamie["insurance_choice"], "integrated_shield")
        
        print("✅ Decision making system passed")
        
    def test_07_outcome_calculation_appendectomy(self):
        """Test outcome calculation for appendectomy scenario"""
        # Create a new game session with decisions
        self.test_06_decision_making_system()
        
        # Calculate outcome for appendectomy
        response = requests.post(
            f"{API_URL}/game/calculate-outcome",
            params={"session_id": self.session_id, "scenario_id": "appendix_surgery"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify scenario data
        self.assertEqual(data["scenario"]["id"], "appendix_surgery")
        self.assertEqual(data["scenario"]["treatment_cost"], 25000.0)
        
        # Verify Alex's outcome (MediShield Basic)
        alex_outcome = data["outcomes"]["alex"]
        self.assertEqual(alex_outcome["character_name"], "Alex")
        self.assertEqual(alex_outcome["insurance_plan"], "MediShield Life (Basic)")
        
        # Calculate expected costs for Alex with MediShield Basic
        # Deductible: 3000
        # Remaining cost: 25000 - 3000 = 22000
        # Copayment: 22000 * 10% = 2200
        # Total out of pocket: 3000 + 2200 = 5200
        # Insurance covered: 25000 - 5200 = 19800
        self.assertAlmostEqual(alex_outcome["out_of_pocket_cost"], 5200.0, places=1)
        self.assertAlmostEqual(alex_outcome["insurance_covered"], 19800.0, places=1)
        self.assertEqual(alex_outcome["financial_impact"], "Medium")
        
        # Verify Jamie's outcome (Integrated Shield)
        jamie_outcome = data["outcomes"]["jamie"]
        self.assertEqual(jamie_outcome["character_name"], "Jamie")
        self.assertEqual(jamie_outcome["insurance_plan"], "Integrated Shield Plan")
        
        # Calculate expected costs for Jamie with Integrated Shield
        # Deductible: 1000
        # Remaining cost: 25000 - 1000 = 24000
        # Copayment: 24000 * 5% = 1200
        # Total out of pocket: 1000 + 1200 = 2200
        # Insurance covered: 25000 - 2200 = 22800
        self.assertAlmostEqual(jamie_outcome["out_of_pocket_cost"], 2200.0, places=1)
        self.assertAlmostEqual(jamie_outcome["insurance_covered"], 22800.0, places=1)
        self.assertEqual(jamie_outcome["financial_impact"], "Low")
        
        print("✅ Outcome calculation for appendectomy passed")
        
    def test_08_outcome_calculation_cancer(self):
        """Test outcome calculation for cancer scenario"""
        # Create a new game session with decisions
        self.test_06_decision_making_system()
        
        # Calculate outcome for cancer diagnosis
        response = requests.post(
            f"{API_URL}/game/calculate-outcome",
            params={"session_id": self.session_id, "scenario_id": "cancer_diagnosis"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify scenario data
        self.assertEqual(data["scenario"]["id"], "cancer_diagnosis")
        self.assertEqual(data["scenario"]["treatment_cost"], 180000.0)
        
        # Verify Alex's outcome (MediShield Basic)
        alex_outcome = data["outcomes"]["alex"]
        
        # Calculate expected costs for Alex with MediShield Basic
        # Coverage limit: 150000
        # Excess cost: 180000 - 150000 = 30000
        # Deductible: 3000
        # Remaining cost within coverage: 150000 - 3000 = 147000
        # Copayment: 147000 * 10% = 14700
        # Total out of pocket: 3000 + 14700 + 30000 = 47700
        # Insurance covered: 180000 - 47700 = 132300
        self.assertAlmostEqual(alex_outcome["out_of_pocket_cost"], 47700.0, places=1)
        self.assertAlmostEqual(alex_outcome["insurance_covered"], 132300.0, places=1)
        self.assertEqual(alex_outcome["financial_impact"], "High")
        
        # Verify Jamie's outcome (Integrated Shield)
        jamie_outcome = data["outcomes"]["jamie"]
        
        # Calculate expected costs for Jamie with Integrated Shield
        # Coverage limit: 1000000 (not exceeded)
        # Deductible: 1000
        # Remaining cost: 180000 - 1000 = 179000
        # Copayment: 179000 * 5% = 8950
        # Total out of pocket: 1000 + 8950 = 9950
        # Insurance covered: 180000 - 9950 = 170050
        self.assertAlmostEqual(jamie_outcome["out_of_pocket_cost"], 9950.0, places=1)
        self.assertAlmostEqual(jamie_outcome["insurance_covered"], 170050.0, places=1)
        self.assertEqual(jamie_outcome["financial_impact"], "Medium")
        
        print("✅ Outcome calculation for cancer diagnosis passed")
        
    def test_09_outcome_calculation_broken_arm(self):
        """Test outcome calculation for broken arm scenario"""
        # Create a new game session with decisions
        self.test_06_decision_making_system()
        
        # Calculate outcome for broken arm
        response = requests.post(
            f"{API_URL}/game/calculate-outcome",
            params={"session_id": self.session_id, "scenario_id": "broken_arm"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify scenario data
        self.assertEqual(data["scenario"]["id"], "broken_arm")
        self.assertEqual(data["scenario"]["treatment_cost"], 15000.0)
        
        # Verify Alex's outcome (MediShield Basic)
        alex_outcome = data["outcomes"]["alex"]
        
        # Calculate expected costs for Alex with MediShield Basic
        # Deductible: 3000
        # Remaining cost: 15000 - 3000 = 12000
        # Copayment: 12000 * 10% = 1200
        # Total out of pocket: 3000 + 1200 = 4200
        # Insurance covered: 15000 - 4200 = 10800
        self.assertAlmostEqual(alex_outcome["out_of_pocket_cost"], 4200.0, places=1)
        self.assertAlmostEqual(alex_outcome["insurance_covered"], 10800.0, places=1)
        self.assertEqual(alex_outcome["financial_impact"], "Low")
        
        # Verify Jamie's outcome (Integrated Shield)
        jamie_outcome = data["outcomes"]["jamie"]
        
        # Calculate expected costs for Jamie with Integrated Shield
        # Deductible: 1000
        # Remaining cost: 15000 - 1000 = 14000
        # Copayment: 14000 * 5% = 700
        # Total out of pocket: 1000 + 700 = 1700
        # Insurance covered: 15000 - 1700 = 13300
        self.assertAlmostEqual(jamie_outcome["out_of_pocket_cost"], 1700.0, places=1)
        self.assertAlmostEqual(jamie_outcome["insurance_covered"], 13300.0, places=1)
        self.assertEqual(jamie_outcome["financial_impact"], "Low")
        
        print("✅ Outcome calculation for broken arm passed")
        
    def test_10_session_persistence(self):
        """Test session persistence with multiple sessions"""
        # Create first session
        session_id_1 = str(uuid.uuid4())
        response = requests.post(
            f"{API_URL}/game/start",
            json={"session_id": session_id_1}
        )
        self.assertEqual(response.status_code, 200)
        
        # Create second session
        session_id_2 = str(uuid.uuid4())
        response = requests.post(
            f"{API_URL}/game/start",
            json={"session_id": session_id_2}
        )
        self.assertEqual(response.status_code, 200)
        
        # Make decisions in first session
        alex_decision = {
            "session_id": session_id_1,
            "decision": {
                "character_id": "alex",
                "insurance_option_id": "medishield_basic"
            }
        }
        response = requests.post(f"{API_URL}/game/decision", json=alex_decision)
        self.assertEqual(response.status_code, 200)
        
        # Make different decisions in second session
        alex_decision_2 = {
            "session_id": session_id_2,
            "decision": {
                "character_id": "alex",
                "insurance_option_id": "integrated_shield"
            }
        }
        response = requests.post(f"{API_URL}/game/decision", json=alex_decision_2)
        self.assertEqual(response.status_code, 200)
        
        # Verify first session data
        response = requests.get(f"{API_URL}/game/{session_id_1}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["completed_decisions"]["alex"], "medishield_basic")
        
        # Verify second session data
        response = requests.get(f"{API_URL}/game/{session_id_2}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["completed_decisions"]["alex"], "integrated_shield")
        
        print("✅ Session persistence passed")
        
    def test_11_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test invalid session ID
        invalid_session = str(uuid.uuid4())
        response = requests.get(f"{API_URL}/game/{invalid_session}")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid scenario ID
        response = requests.post(
            f"{API_URL}/game/calculate-outcome",
            params={"session_id": self.session_id, "scenario_id": "nonexistent_scenario"}
        )
        self.assertEqual(response.status_code, 404)
        
        # Test invalid character ID in decision
        invalid_decision = {
            "session_id": self.session_id,
            "decision": {
                "character_id": "nonexistent_character",
                "insurance_option_id": "medishield_basic"
            }
        }
        # Create a session first
        requests.post(
            f"{API_URL}/game/start",
            json={"session_id": self.session_id}
        )
        # Try invalid decision
        response = requests.post(f"{API_URL}/game/decision", json=invalid_decision)
        self.assertEqual(response.status_code, 200)  # API accepts but character won't be found
        
        # Verify decision wasn't recorded for nonexistent character
        response = requests.get(f"{API_URL}/game/{self.session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn("nonexistent_character", data["completed_decisions"])
        
        print("✅ Error handling passed")


if __name__ == "__main__":
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)