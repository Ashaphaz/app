import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [gameState, setGameState] = useState(null);
  const [currentChapter, setCurrentChapter] = useState(1);
  const [characters, setCharacters] = useState([]);
  const [insuranceOptions, setInsuranceOptions] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [selectedDecisions, setSelectedDecisions] = useState({});
  const [gameOutcome, setGameOutcome] = useState(null);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initializeGame();
  }, []);

  const initializeGame = async () => {
    try {
      setLoading(true);
      
      // Fetch game data
      const [charactersRes, insuranceRes, scenariosRes] = await Promise.all([
        axios.get(`${API}/characters`),
        axios.get(`${API}/insurance-options`),
        axios.get(`${API}/scenarios`)
      ]);

      setCharacters(charactersRes.data);
      setInsuranceOptions(insuranceRes.data);
      setScenarios(scenariosRes.data);

      // Start game session
      await axios.post(`${API}/game/start`, { session_id: sessionId });
      
      setLoading(false);
    } catch (error) {
      console.error('Error initializing game:', error);
      setLoading(false);
    }
  };

  const makeDecision = async (characterId, insuranceOptionId) => {
    try {
      await axios.post(`${API}/game/decision`, {
        session_id: sessionId,
        decision: {
          character_id: characterId,
          insurance_option_id: insuranceOptionId
        }
      });

      setSelectedDecisions(prev => ({
        ...prev,
        [characterId]: insuranceOptionId
      }));
    } catch (error) {
      console.error('Error making decision:', error);
    }
  };

  const calculateOutcome = async (scenarioId) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/game/calculate-outcome?session_id=${sessionId}&scenario_id=${scenarioId}`);
      setGameOutcome(response.data);
      setCurrentChapter(4);
      setLoading(false);
    } catch (error) {
      console.error('Error calculating outcome:', error);
      setLoading(false);
    }
  };

  const resetGame = () => {
    setCurrentChapter(1);
    setSelectedDecisions({});
    setGameOutcome(null);
    window.location.reload();
  };

  const renderChapter1 = () => (
    <div className="chapter-container">
      <div className="story-header">
        <h1 className="chapter-title">Chapter 1: The Conversation</h1>
        <p className="chapter-subtitle">Two friends discussing health insurance options</p>
      </div>
      
      <div className="story-section">
        <div className="character-intro">
          <img src="https://images.unsplash.com/photo-1605516363551-96facdffba02" alt="Characters" className="story-image" />
          <div className="dialogue-box">
            <p className="dialogue">
              <strong>Alex:</strong> "Eh Jamie, you know what? I've been thinking about this health insurance thing. 
              My colleague just got hit with a huge medical bill, and I'm wondering if we should upgrade our coverage."
            </p>
            <p className="dialogue">
              <strong>Jamie:</strong> "Ya lor, I've been thinking the same thing! But honestly, I'm quite blur about all these 
              insurance options. MediShield Life is basic right? But got this Integrated Shield Plan also..."
            </p>
          </div>
        </div>
        
        <div className="characters-display">
          {characters.map(character => (
            <div key={character.id} className="character-card">
              <div className="character-info">
                <h3>{character.name}</h3>
                <p><strong>Age:</strong> {character.age}</p>
                <p><strong>Job:</strong> {character.occupation}</p>
                <p><strong>Health:</strong> {character.current_health_status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <button 
        className="next-button"
        onClick={() => setCurrentChapter(2)}
      >
        Learn About Insurance Options →
      </button>
    </div>
  );

  const renderChapter2 = () => (
    <div className="chapter-container">
      <div className="story-header">
        <h1 className="chapter-title">Chapter 2: Understanding Options</h1>
        <p className="chapter-subtitle">Comparing MediShield Life vs Integrated Shield Plans</p>
      </div>
      
      <div className="insurance-comparison">
        {insuranceOptions.map(option => (
          <div key={option.id} className="insurance-card">
            <div className="insurance-header">
              <h3>{option.name}</h3>
              <span className={`plan-type ${option.type}`}>{option.type.toUpperCase()}</span>
            </div>
            
            <div className="insurance-details">
              <div className="cost-info">
                <p><strong>Monthly Premium:</strong> ${option.monthly_premium}</p>
                <p><strong>Annual Deductible:</strong> ${option.annual_deductible}</p>
                <p><strong>Co-payment:</strong> {option.copayment_percentage}%</p>
                <p><strong>Coverage Limit:</strong> ${option.coverage_limit.toLocaleString()}</p>
              </div>
              
              <div className="benefits-list">
                <h4>Key Benefits:</h4>
                <ul>
                  {option.key_benefits.map((benefit, index) => (
                    <li key={index}>{benefit}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="dialogue-box">
        <p className="dialogue">
          <strong>Alex:</strong> "Wah, the premium difference quite big eh? But the coverage also very different."
        </p>
        <p className="dialogue">
          <strong>Jamie:</strong> "Ya lor, but if anything happens, the out-of-pocket cost could be super high with basic plan."
        </p>
      </div>
      
      <button 
        className="next-button"
        onClick={() => setCurrentChapter(3)}
      >
        Make Your Decisions →
      </button>
    </div>
  );

  const renderChapter3 = () => (
    <div className="chapter-container">
      <div className="story-header">
        <h1 className="chapter-title">Chapter 3: Decision Time</h1>
        <p className="chapter-subtitle">Choose insurance plans for both characters</p>
      </div>
      
      <div className="decision-section">
        {characters.map(character => (
          <div key={character.id} className="character-decision">
            <div className="character-profile">
              <h3>{character.name}</h3>
              <p>{character.current_health_status}</p>
            </div>
            
            <div className="insurance-choices">
              <h4>Choose {character.name}'s insurance plan:</h4>
              {insuranceOptions.map(option => (
                <button
                  key={option.id}
                  className={`choice-button ${selectedDecisions[character.id] === option.id ? 'selected' : ''}`}
                  onClick={() => makeDecision(character.id, option.id)}
                >
                  <div className="choice-content">
                    <span className="choice-name">{option.name}</span>
                    <span className="choice-premium">${option.monthly_premium}/month</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {Object.keys(selectedDecisions).length === characters.length && (
        <div className="scenario-selection">
          <h3>Now, let's see what happens...</h3>
          <p>Choose a medical scenario to see how their insurance decisions play out:</p>
          <div className="scenario-buttons">
            {scenarios.map(scenario => (
              <button
                key={scenario.id}
                className="scenario-button"
                onClick={() => calculateOutcome(scenario.id)}
              >
                <div className="scenario-content">
                  <h4>{scenario.title}</h4>
                  <p>{scenario.description}</p>
                  <span className="scenario-cost">Cost: ${scenario.treatment_cost.toLocaleString()}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderChapter4 = () => (
    <div className="chapter-container">
      <div className="story-header">
        <h1 className="chapter-title">Chapter 4: The Reality Check</h1>
        <p className="chapter-subtitle">See how their decisions affected their financial outcomes</p>
      </div>
      
      {gameOutcome && (
        <div className="outcome-section">
          <div className="scenario-details">
            <img src="https://images.pexels.com/photos/236380/pexels-photo-236380.jpeg" alt="Hospital" className="scenario-image" />
            <div className="scenario-info">
              <h3>{gameOutcome.scenario.title}</h3>
              <p>{gameOutcome.scenario.description}</p>
              <p><strong>Total Treatment Cost:</strong> ${gameOutcome.scenario.treatment_cost.toLocaleString()}</p>
            </div>
          </div>
          
          <div className="outcomes-comparison">
            {Object.entries(gameOutcome.outcomes).map(([characterId, outcome]) => (
              <div key={characterId} className="outcome-card">
                <h3>{outcome.character_name}</h3>
                <div className="outcome-details">
                  <p><strong>Insurance Plan:</strong> {outcome.insurance_plan}</p>
                  <p><strong>Total Treatment Cost:</strong> ${outcome.total_treatment_cost.toLocaleString()}</p>
                  <p><strong>Insurance Covered:</strong> ${outcome.insurance_covered.toLocaleString()}</p>
                  <p className="out-of-pocket"><strong>Out-of-Pocket Cost:</strong> ${outcome.out_of_pocket_cost.toLocaleString()}</p>
                  <span className={`financial-impact ${outcome.financial_impact.toLowerCase()}`}>
                    Financial Impact: {outcome.financial_impact}
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="moral-section">
            <h3>The Lesson</h3>
            <p>
              This simulation shows how different insurance choices can significantly impact your financial well-being 
              during medical emergencies. While higher premiums might seem expensive monthly, they can save you 
              thousands when you need medical care most.
            </p>
            <p>
              Consider your health history, family medical background, and financial situation when choosing 
              your insurance coverage. Remember, it's not just about the premium - it's about protecting your future.
            </p>
          </div>
        </div>
      )}
      
      <button 
        className="reset-button"
        onClick={resetGame}
      >
        Try Different Scenarios
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your health insurance story...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>MediShield Decision Game</h1>
        <p>An Interactive Story About Health Insurance Choices</p>
      </header>
      
      <main className="app-main">
        {currentChapter === 1 && renderChapter1()}
        {currentChapter === 2 && renderChapter2()}
        {currentChapter === 3 && renderChapter3()}
        {currentChapter === 4 && renderChapter4()}
      </main>
      
      <footer className="app-footer">
        <p>Learn more about MediShield Life and Integrated Shield Plans at gov.sg</p>
      </footer>
    </div>
  );
}

export default App;