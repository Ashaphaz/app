import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Image assets for better visual experience
const IMAGES = {
  characters: "https://images.unsplash.com/photo-1605516363551-96facdffba02",
  diverseGroup: "https://images.unsplash.com/photo-1659019729984-59db3b81d8f2", 
  healthcare: "https://images.pexels.com/photos/236380/pexels-photo-236380.jpeg",
  doctor: "https://images.pexels.com/photos/8376277/pexels-photo-8376277.jpeg",
  medical: "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7",
  hospital: "https://images.pexels.com/photos/236380/pexels-photo-236380.jpeg",
  consultation: "https://images.pexels.com/photos/8376277/pexels-photo-8376277.jpeg"
};

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
  const [comparisonData, setComparisonData] = useState(null);

  useEffect(() => {
    initializeGame();
  }, []);

  const initializeGame = async () => {
    try {
      setLoading(true);
      
      // Fetch game data
      const [charactersRes, insuranceRes, scenariosRes, comparisonRes] = await Promise.all([
        axios.get(`${API}/characters`),
        axios.get(`${API}/insurance-options`),
        axios.get(`${API}/scenarios`),
        axios.get(`${API}/stats/comparison`)
      ]);

      setCharacters(charactersRes.data);
      setInsuranceOptions(insuranceRes.data);
      setScenarios(scenariosRes.data);
      setComparisonData(comparisonRes.data);

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

  const getProgressPercentage = () => {
    return (currentChapter / 4) * 100;
  };

  const getCostBreakdown = (outcome) => {
    const totalCost = outcome.total_treatment_cost;
    const insuranceCovered = outcome.insurance_covered;
    const outOfPocket = outcome.out_of_pocket_cost;
    
    return {
      insurance_percentage: (insuranceCovered / totalCost) * 100,
      out_of_pocket_percentage: (outOfPocket / totalCost) * 100
    };
  };

  const getScenarioImage = (scenarioId) => {
    const imageMap = {
      'appendix_surgery': IMAGES.hospital,
      'cancer_diagnosis': IMAGES.doctor,
      'broken_arm': IMAGES.medical,
      'dental_emergency': IMAGES.consultation,
      'mental_health': IMAGES.doctor,
      'maternity_care': IMAGES.healthcare,
      'eye_surgery': IMAGES.consultation,
      'heart_condition': IMAGES.medical,
      'accident_injury': IMAGES.hospital,
      'chronic_condition': IMAGES.doctor
    };
    return imageMap[scenarioId] || IMAGES.healthcare;
  };

  const renderChapter1 = () => (
    <div className="chapter-container">
      <div className="story-header">
        <h1 className="chapter-title">Chapter 1: The Conversation</h1>
        <p className="chapter-subtitle">Two friends discussing health insurance options in Singapore</p>
      </div>
      
      <div className="story-section">
        <div className="character-intro">
          <div className="image-gallery">
            <img 
              src={IMAGES.characters} 
              alt="Young adults discussing insurance" 
              className="story-image main-image" 
            />
            <img 
              src={IMAGES.diverseGroup} 
              alt="Diverse group representation" 
              className="story-image secondary-image" 
            />
          </div>
          <div className="dialogue-box">
            <p className="dialogue">
              <strong>Alex:</strong> "Eh Jamie, you know what? I've been thinking about this health insurance thing. 
              My colleague just got hit with a huge medical bill after his appendix surgery, and I'm wondering if we should upgrade our coverage."
            </p>
            <p className="dialogue">
              <strong>Jamie:</strong> "Wah, really? Ya lor, I've been thinking the same thing! But honestly, I'm quite blur about all these 
              insurance options. MediShield Life is basic right? But got this Integrated Shield Plan also... the premium difference quite big sia."
            </p>
            <p className="dialogue">
              <strong>Alex:</strong> "Exactly! That's why I think we need to understand what we're getting into. Let's explore the options properly."
            </p>
          </div>
        </div>
        
        <div className="characters-display">
          {characters.map((character, index) => (
            <div key={character.id} className="character-card">
              <div className="character-avatar">
                <img 
                  src={index === 0 ? IMAGES.consultation : IMAGES.medical} 
                  alt={`${character.name} avatar`}
                  className="avatar-image"
                />
                <div className="character-badge">{character.name}</div>
              </div>
              <div className="character-info">
                <h3>{character.name}</h3>
                <p><strong>Age:</strong> {character.age}</p>
                <p><strong>Occupation:</strong> {character.occupation}</p>
                <p><strong>Health Status:</strong> {character.current_health_status}</p>
                <p><strong>Lifestyle:</strong> {character.lifestyle}</p>
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
        <h1 className="chapter-title">Chapter 2: Understanding Your Options</h1>
        <p className="chapter-subtitle">Comparing MediShield Life vs Integrated Shield Plans</p>
      </div>

      <div className="insurance-intro">
        <img 
          src={IMAGES.healthcare} 
          alt="Healthcare planning" 
          className="insurance-hero-image" 
        />
        <div className="insurance-intro-text">
          <h3>💡 Making Informed Decisions</h3>
          <p>Health insurance isn't just about monthly premiums. It's about protecting your financial future and ensuring access to quality healthcare when you need it most.</p>
        </div>
      </div>
      
      <div className="insurance-comparison">
        {insuranceOptions.map((option, index) => (
          <div key={option.id} className="insurance-card">
            <div className="insurance-visual">
              <img 
                src={index === 0 ? IMAGES.doctor : IMAGES.medical} 
                alt={`${option.name} visual`}
                className="insurance-image"
              />
              <div className="insurance-overlay">
                <span className={`plan-type ${option.type}`}>{option.type}</span>
              </div>
            </div>
            <div className="insurance-header">
              <h3>{option.name}</h3>
            </div>
            
            <div className="insurance-details">
              <div className="cost-info">
                <h4>💰 Cost Details</h4>
                <p><strong>Monthly Premium:</strong> ${option.monthly_premium}</p>
                <p><strong>Annual Premium:</strong> ${(option.monthly_premium * 12).toLocaleString()}</p>
                <p><strong>Annual Deductible:</strong> ${option.annual_deductible.toLocaleString()}</p>
                <p><strong>Co-payment:</strong> {option.copayment_percentage}%</p>
                <p><strong>Coverage Limit:</strong> ${option.coverage_limit.toLocaleString()}</p>
              </div>
              
              <div className="benefits-list">
                <h4>✨ Key Benefits</h4>
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

      {comparisonData && (
        <div className="cost-comparison-section">
          <div className="comparison-visual">
            <img 
              src={IMAGES.consultation} 
              alt="Cost comparison" 
              className="comparison-image" 
            />
            <div className="cost-breakdown">
              <h4>📊 Annual Cost Comparison</h4>
              <div className="cost-bar">
                <div className="cost-label">Basic Plan</div>
                <div className="cost-visual">
                  <div 
                    className="cost-fill basic-plan" 
                    style={{ width: '40%' }}
                  ></div>
                </div>
                <div className="cost-amount">${comparisonData.basic_plan.annual_cost}</div>
              </div>
              <div className="cost-bar">
                <div className="cost-label">Enhanced Plan</div>
                <div className="cost-visual">
                  <div 
                    className="cost-fill enhanced-plan" 
                    style={{ width: '100%' }}
                  ></div>
                </div>
                <div className="cost-amount">${comparisonData.enhanced_plan.annual_cost}</div>
              </div>
              <div className="cost-bar">
                <div className="cost-label">Difference</div>
                <div className="cost-visual">
                  <div 
                    className="cost-fill difference" 
                    style={{ width: '60%' }}
                  ></div>
                </div>
                <div className="cost-amount">+${comparisonData.cost_difference.annual}</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="dialogue-box">
        <p className="dialogue">
          <strong>Alex:</strong> "Wah, the premium difference is like ${comparisonData?.cost_difference.monthly || 300} per month eh? But look at the benefits and coverage limits..."
        </p>
        <p className="dialogue">
          <strong>Jamie:</strong> "Ya lor, but if anything serious happens, the out-of-pocket cost difference could be even bigger. Let's think about this carefully."
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

      <div className="decision-intro">
        <img 
          src={IMAGES.diverseGroup} 
          alt="Making decisions together" 
          className="decision-hero-image" 
        />
        <div className="decision-intro-text">
          <h3>🎯 Your Choices Matter</h3>
          <p>Every insurance decision has real consequences. Consider each character's lifestyle, health status, and financial situation.</p>
        </div>
      </div>
      
      <div className="decision-section">
        {characters.map((character, index) => (
          <div key={character.id} className="character-decision">
            <div className="character-profile">
              <div className="profile-image-container">
                <img 
                  src={index === 0 ? IMAGES.doctor : IMAGES.consultation} 
                  alt={`${character.name} profile`}
                  className="profile-image"
                />
                <div className="profile-overlay">
                  <h3>{character.name}</h3>
                </div>
              </div>
              <div className="profile-details">
                <p><strong>Age:</strong> {character.age} | <strong>Occupation:</strong> {character.occupation}</p>
                <p><strong>Health:</strong> {character.current_health_status}</p>
                <p><strong>Lifestyle:</strong> {character.lifestyle}</p>
              </div>
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
                    <div className="choice-name">
                      {option.name}
                      <div className="choice-description">
                        {option.type === 'basic' ? '💡 Budget-friendly option' : '⭐ Premium protection'}
                      </div>
                    </div>
                    <div className="choice-premium">
                      ${option.monthly_premium}/month
                      <div className="choice-annual">
                        ${(option.monthly_premium * 12).toLocaleString()}/year
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {Object.keys(selectedDecisions).length === characters.length && (
        <div className="scenario-selection">
          <div className="scenario-header">
            <img 
              src={IMAGES.healthcare} 
              alt="Healthcare scenarios" 
              className="scenario-header-image" 
            />
            <div className="scenario-header-text">
              <h3>🎭 Now, let's see what happens...</h3>
              <p>Life is unpredictable. Choose a medical scenario to see how their insurance decisions play out:</p>
            </div>
          </div>
          
          <div className="scenario-grid">
            {scenarios.map(scenario => (
              <button
                key={scenario.id}
                className="scenario-button"
                onClick={() => calculateOutcome(scenario.id)}
              >
                <div className="scenario-image-container">
                  <img 
                    src={getScenarioImage(scenario.id)} 
                    alt={scenario.title}
                    className="scenario-thumbnail"
                  />
                  <div className="scenario-overlay">
                    <div className="scenario-tags">
                      <span className={`scenario-tag ${scenario.category}`}>
                        {scenario.category}
                      </span>
                      <span className={`scenario-tag ${scenario.urgency_level}`}>
                        {scenario.urgency_level}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="scenario-content">
                  <h4>{scenario.title}</h4>
                  <p>{scenario.description}</p>
                  <div className="scenario-cost">
                    💰 Treatment Cost: ${scenario.treatment_cost.toLocaleString()}
                  </div>
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
        <p className="chapter-subtitle">How insurance decisions impact financial outcomes</p>
      </div>
      
      {gameOutcome && (
        <div className="outcome-section">
          <div className="scenario-details">
            <div className="scenario-visual">
              <img 
                src={getScenarioImage(gameOutcome.scenario.id)} 
                alt="Healthcare scenario" 
                className="scenario-image" 
              />
              <div className="scenario-badge">
                <span className={`badge ${gameOutcome.scenario.urgency_level}`}>
                  {gameOutcome.scenario.urgency_level} priority
                </span>
              </div>
            </div>
            <div className="scenario-info">
              <h3>📋 {gameOutcome.scenario.title}</h3>
              <p><strong>Situation:</strong> {gameOutcome.scenario.description}</p>
              <p><strong>Medical Treatment:</strong> {gameOutcome.scenario.medical_situation}</p>
              <p><strong>Total Treatment Cost:</strong> ${gameOutcome.scenario.treatment_cost.toLocaleString()}</p>
              <div className="scenario-tags">
                <span className={`scenario-tag ${gameOutcome.scenario.category}`}>
                  {gameOutcome.scenario.category}
                </span>
                <span className={`scenario-tag ${gameOutcome.scenario.urgency_level}`}>
                  {gameOutcome.scenario.urgency_level} priority
                </span>
              </div>
            </div>
          </div>
          
          <div className="outcomes-comparison">
            {Object.entries(gameOutcome.outcomes).map(([characterId, outcome], index) => {
              const breakdown = getCostBreakdown(outcome);
              return (
                <div key={characterId} className="outcome-card">
                  <div className="outcome-header">
                    <img 
                      src={index === 0 ? IMAGES.doctor : IMAGES.consultation} 
                      alt={`${outcome.character_name} outcome`}
                      className="outcome-avatar"
                    />
                    <h3>👤 {outcome.character_name}</h3>
                  </div>
                  <div className="outcome-details">
                    <p><strong>🏥 Insurance Plan:</strong> {outcome.insurance_plan}</p>
                    <p><strong>💰 Annual Premium:</strong> ${outcome.annual_premium.toLocaleString()}</p>
                    <p><strong>🏥 Total Treatment Cost:</strong> ${outcome.total_treatment_cost.toLocaleString()}</p>
                    <p><strong>✅ Insurance Covered:</strong> ${outcome.insurance_covered.toLocaleString()}</p>
                    
                    <div className="cost-comparison">
                      <div className="cost-breakdown">
                        <h4>Cost Breakdown</h4>
                        <div className="cost-bar">
                          <div className="cost-label">Insurance</div>
                          <div className="cost-visual">
                            <div 
                              className="cost-fill insurance-fill" 
                              style={{ width: `${breakdown.insurance_percentage}%` }}
                            ></div>
                          </div>
                          <div className="cost-amount">{breakdown.insurance_percentage.toFixed(1)}%</div>
                        </div>
                        <div className="cost-bar">
                          <div className="cost-label">Out-of-Pocket</div>
                          <div className="cost-visual">
                            <div 
                              className="cost-fill pocket-fill" 
                              style={{ width: `${breakdown.out_of_pocket_percentage}%` }}
                            ></div>
                          </div>
                          <div className="cost-amount">{breakdown.out_of_pocket_percentage.toFixed(1)}%</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="out-of-pocket">
                      <strong>💸 Your Out-of-Pocket Cost: ${outcome.out_of_pocket_cost.toLocaleString()}</strong>
                    </div>
                    
                    <span className={`financial-impact ${outcome.financial_impact.toLowerCase()}`}>
                      Financial Impact: {outcome.financial_impact}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
          
          <div className="moral-section">
            <div className="moral-visual">
              <img 
                src={IMAGES.diverseGroup} 
                alt="Learning together" 
                className="moral-image" 
              />
              <div className="moral-content">
                <h3>🎓 Key Insights</h3>
                <p>
                  This simulation demonstrates how insurance choices can dramatically affect your financial well-being 
                  during medical emergencies. While higher premiums might seem expensive monthly, they often provide 
                  substantial savings when you need medical care most.
                </p>
                <p>
                  <strong>Consider these factors when choosing insurance:</strong>
                </p>
                <ul>
                  <li>Your current health status and family medical history</li>
                  <li>Your financial ability to handle large unexpected expenses</li>
                  <li>The types of medical services you're likely to need</li>
                  <li>Your age and life stage (young professionals vs. planning for family)</li>
                  <li>The long-term cost-benefit analysis, not just monthly premiums</li>
                </ul>
                <p>
                  Remember: Health insurance is not just about the monthly premium—it's about protecting your financial future 
                  and ensuring you can access quality healthcare when you need it most. In Singapore's healthcare system, 
                  the right insurance choice can mean the difference between financial stability and significant debt during health crises.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <button 
        className="reset-button"
        onClick={resetGame}
      >
        🔄 Try Different Scenarios
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your InsurEdge experience...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="progress-container">
        <div 
          className="progress-bar" 
          style={{ width: `${getProgressPercentage()}%` }}
        ></div>
      </div>
      
      <header className="app-header">
        <h1>InsurEdge</h1>
        <p>The Interactive Story Game About Smart Health Insurance Choices</p>
      </header>
      
      <main className="app-main">
        {currentChapter === 1 && renderChapter1()}
        {currentChapter === 2 && renderChapter2()}
        {currentChapter === 3 && renderChapter3()}
        {currentChapter === 4 && renderChapter4()}
      </main>
      
      <footer className="app-footer">
        <p>📖 Learn more about MediShield Life and Integrated Shield Plans at <strong>cpf.gov.sg</strong> and <strong>moh.gov.sg</strong></p>
        <p className="game-brand">🎮 Powered by <strong>InsurEdge</strong> - Making Insurance Education Interactive</p>
      </footer>
    </div>
  );
}

export default App;