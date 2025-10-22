import React, { useState, useRef, useEffect } from 'react';
import { Upload, Video, TrendingUp, Target, Shield, Users, Play, CheckCircle, AlertCircle, Camera, BarChart3, Award, Calendar, Brain, Clock, Zap, MessageCircle, Send } from 'lucide-react';

const PlaySmart = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState('shooting');
  const [selectedSubSkill, setSelectedSubSkill] = useState('power_shot');
  const [hoursPerWeek, setHoursPerWeek] = useState(5);
  const [chatMessages, setChatMessages] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const skills = {
    shooting: {
      name: 'Shooting',
      icon: Target,
      color: 'red',
      subSkills: ['power_shot', 'finesse', 'chip', 'volley', 'bicycle', 'penalty', 'trivela']
    },
    passing: {
      name: 'Passing',
      icon: Users,
      color: 'blue',
      subSkills: ['ground_pass', 'lob', 'through_ball', 'cross', 'long_ball', 'one_touch']
    },
    defending: {
      name: 'Defending',
      icon: Shield,
      color: 'green',
      subSkills: ['jockeying', 'tackling', 'interception', 'marking', 'clearance', 'blocking']
    },
    positioning: {
      name: 'Positioning',
      icon: TrendingUp,
      color: 'purple',
      subSkills: ['off_ball', 'spacing', 'pressing', 'transition', 'shape']
    }
  };

  const subSkillNames = {
    power_shot: 'Power Shot', finesse: 'Finesse Shot', chip: 'Chip Shot', volley: 'Volley',
    bicycle: 'Bicycle Kick', penalty: 'Penalty', trivela: 'Trivela',
    ground_pass: 'Ground Pass', lob: 'Lob Pass', through_ball: 'Through Ball', cross: 'Cross',
    long_ball: 'Long Ball', one_touch: 'One Touch',
    jockeying: 'Jockeying', tackling: 'Tackling', interception: 'Interception',
    marking: 'Marking', clearance: 'Clearance', blocking: 'Blocking',
    off_ball: 'Off Ball Movement', spacing: 'Spacing', pressing: 'Pressing',
    transition: 'Transition', shape: 'Team Shape'
  };

  const progressData = {
    shooting: { current: 72, target: 85, improved: 12 },
    passing: { current: 78, target: 88, improved: 8 },
    defending: { current: 65, target: 80, improved: 5 },
    positioning: { current: 70, target: 85, improved: 10 }
  };

  const matchAnalysis = {
    nervousPoints: [
      { time: '12:34', situation: 'Receiving ball under pressure', action: 'Quick decision needed' },
      { time: '23:45', situation: 'One-on-one with defender', action: 'Hesitated on dribble choice' }
    ],
    confusedPoints: [
      { time: '34:21', situation: 'Team transition', action: 'Unsure whether to press or drop' }
    ],
    positioningErrors: [
      { time: '15:20', error: 'Too narrow - lost width', correction: 'Stay wider to stretch defense' },
      { time: '45:10', error: 'Ball-watching during attack', correction: 'Scan and move into space' }
    ]
  };

  const getAnalysisData = () => {
    const analyses = {
      power_shot: {
        score: 58, proScore: 92,
        issues: [
          { severity: 'high', issue: 'Plant foot 18cm too far from ball (Pro avg: 11cm)', fix: 'Position 10-12cm beside ball' },
          { severity: 'high', issue: 'Body leaning backward 12° at contact (Pro: 5° forward)', fix: 'Keep chest over ball' }
        ],
        strengths: ['Ankle remains locked during strike', 'Approach angle consistent at 30-35°'],
        drills: ['Plant foot drill - 20 reps', 'Body balance over ball - 15 mins']
      },
      finesse: {
        score: 51, proScore: 88,
        issues: [
          { severity: 'high', issue: 'Ankle opening only 22° vs Pro 40-50°', fix: 'Open ankle wider' },
          { severity: 'high', issue: 'Contact point too low', fix: 'Strike center of ball' }
        ],
        strengths: ['Body shape opens correctly', 'Head stays down'],
        drills: ['Inside foot technique - 25 reps', 'Curl practice - 15 mins']
      },
      ground_pass: {
        score: 68, proScore: 95,
        issues: [
          { severity: 'medium', issue: 'Pass weight varies ±15%', fix: 'Focus on consistent weight' }
        ],
        strengths: ['Accuracy within 1m 78% of time', 'Good inside-foot technique'],
        drills: ['Gates drill', 'Target passing']
      }
    };
    return analyses[selectedSubSkill] || analyses.power_shot;
  };

  const generateSchedule = (hours) => {
    const sessionsPerWeek = Math.floor(hours / 1.5);
    const drills = {
      shooting: ['Power shot (15 mins)', 'Finesse (10 mins)'],
      passing: ['Ground pass (10 mins)', 'Through ball (10 mins)'],
      defending: ['Jockeying (15 mins)', 'Positioning (10 mins)'],
      positioning: ['Off-ball movement (15 mins)', 'Scanning (10 mins)']
    };
    
    return Array.from({ length: Math.min(sessionsPerWeek, 7) }, (_, i) => ({
      day: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i],
      focus: Object.keys(skills)[i % 4],
      drills: drills[Object.keys(skills)[i % 4]],
      duration: 90
    }));
  };

  const getAIResponse = (message) => {
    const lowerMsg = message.toLowerCase();
    
    if (lowerMsg.includes('power shot')) {
      return 'Power Shot Technique:\n\n1️⃣ Plant foot 10-12cm beside ball\n2️⃣ Lock ankle, strike with laces\n3️⃣ Body over ball, head down\n4️⃣ Full follow-through\n\nPractice: 20 shots daily!';
    }
    if (lowerMsg.includes('finesse')) {
      return 'Finesse Shot:\n\n1️⃣ Open ankle 40-45°\n2️⃣ Use inside of foot\n3️⃣ Strike center of ball\n4️⃣ Follow through across body\n\nDrill: Curl around cones!';
    }
    if (lowerMsg.includes('pass')) {
      return 'Ground Pass:\n\n1️⃣ Plant foot pointing at target\n2️⃣ Strike with inside of foot\n3️⃣ Contact center of ball\n4️⃣ Follow through\n\nPractice: Gates drill - 30 passes!';
    }
    if (lowerMsg.includes('defend')) {
      return 'Defending 1v1:\n\n1️⃣ Body at 45° angle\n2️⃣ Wide stance for balance\n3️⃣ Stay 1.5-2m away\n4️⃣ Don\'t dive in\n\nDrill: Jockeying practice - 15 reps!';
    }
    if (lowerMsg.includes('weak foot')) {
      return 'Weak Foot Training:\n\n1️⃣ Use only weak foot one session/week\n2️⃣ Start with wall passes\n3️⃣ 200 touches daily\n4️⃣ Force yourself in games\n\nPros train weak foot 30% of time!';
    }
    if (lowerMsg.includes('improve') || lowerMsg.includes('fast')) {
      return 'Improve Fast:\n\n1️⃣ Focus ONE skill per week\n2️⃣ Practice 30 mins daily\n3️⃣ Video yourself\n4️⃣ Use PlaySmart AI\n5️⃣ Quality > quantity\n\nConsistency is key! 🚀';
    }
    
    return 'I can help with:\n\n⚽ Shooting (power, finesse, volley)\n👟 Passing (ground, through ball, cross)\n🛡️ Defending (jockeying, tackling)\n📍 Positioning\n💪 Fitness & drills\n\nAsk me: "How to improve power shot?" or "Tips for defending?"';
  };

  const handleSendMessage = () => {
    if (userMessage.trim() === '') return;
    setChatMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setTimeout(() => {
      setChatMessages(prev => [...prev, { type: 'ai', text: getAIResponse(userMessage) }]);
    }, 500);
    setUserMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedVideo(URL.createObjectURL(file));
      setAnalysisComplete(false);
    }
  };

  const simulateAnalysis = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      setAnalysisComplete(true);
      setCurrentAnalysis(getAnalysisData());
      setActiveTab('analysis');
    }, 3000);
  };

  const schedule = generateSchedule(hoursPerWeek);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto p-4 md:p-6">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-xl flex items-center justify-center">
              <Zap className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">PlaySmart</h1>
          </div>
          <p className="text-gray-400">AI-Powered Football Training Platform</p>
        </div>

        <div className="flex flex-wrap gap-2 mb-6 bg-slate-800/50 p-2 rounded-xl">
          {[
            { id: 'upload', icon: Upload, label: 'Upload' },
            { id: 'analysis', icon: BarChart3, label: 'Analysis' },
            { id: 'progress', icon: TrendingUp, label: 'Progress' },
            { id: 'schedule', icon: Calendar, label: 'Schedule' },
            { id: 'match', icon: Brain, label: 'Match AI' },
            { id: 'coach', icon: MessageCircle, label: 'AI Coach' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={tab.id === 'analysis' && !analysisComplete}
              className={`flex-1 min-w-[90px] py-2 px-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 text-sm ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'upload' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Upload Footage</h2>
              <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept="video/*" className="hidden" />
              
              {!uploadedVideo ? (
                <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 transition-all">
                  <Upload className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <p className="text-lg text-gray-300">Click to upload video</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <video src={uploadedVideo} controls className="w-full rounded-lg max-h-64" />
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(skills).map(([key, skill]) => (
                      <button
                        key={key}
                        onClick={() => setSelectedSkill(key)}
                        className={`p-3 rounded-lg border-2 transition-all ${
                          selectedSkill === key ? 'border-blue-500 bg-blue-500/20' : 'border-slate-700 bg-slate-800/50'
                        }`}
                      >
                        <skill.icon className={`w-6 h-6 mx-auto mb-1 ${selectedSkill === key ? 'text-blue-400' : 'text-gray-400'}`} />
                        <p className={`text-sm ${selectedSkill === key ? 'text-white' : 'text-gray-400'}`}>{skill.name}</p>
                      </button>
                    ))}
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    {skills[selectedSkill].subSkills.map(sub => (
                      <button
                        key={sub}
                        onClick={() => setSelectedSubSkill(sub)}
                        className={`p-2 rounded-lg text-xs transition-all ${
                          selectedSubSkill === sub ? 'bg-blue-600 text-white' : 'bg-slate-700 text-gray-300'
                        }`}
                      >
                        {subSkillNames[sub]}
                      </button>
                    ))}
                  </div>

                  {analyzing ? (
                    <div className="bg-blue-600 text-white py-3 px-4 rounded-xl text-center">
                      <div className="animate-pulse">Analyzing {subSkillNames[selectedSubSkill]}...</div>
                    </div>
                  ) : (
                    <button onClick={simulateAnalysis} className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2">
                      <Play className="w-5 h-5" />
                      Analyze {subSkillNames[selectedSubSkill]}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analysis' && analysisComplete && currentAnalysis && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <div className="flex justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-white">{subSkillNames[selectedSubSkill]}</h2>
                  <p className="text-gray-400 text-sm">vs Professional level</p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-blue-400">{currentAnalysis.score}</div>
                  <div className="text-xs text-green-400">Pro: {currentAnalysis.proScore}</div>
                </div>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 relative">
                <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${currentAnalysis.score}%` }}></div>
              </div>
              <div className="text-center text-sm mt-2 text-orange-400">Gap: {currentAnalysis.proScore - currentAnalysis.score} points</div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3">Issues Detected</h3>
              <div className="space-y-2">
                {currentAnalysis.issues.map((item, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border-l-4 ${item.severity === 'high' ? 'bg-red-500/10 border-red-500' : 'bg-orange-500/10 border-orange-500'}`}>
                    <p className="text-white text-sm mb-1">{item.issue}</p>
                    <p className="text-green-400 text-xs">✓ {item.fix}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3">Strengths</h3>
              <div className="flex flex-wrap gap-2">
                {currentAnalysis.strengths.map((s, i) => (
                  <span key={i} className="bg-green-500/10 border border-green-500/30 rounded-lg px-3 py-1 text-green-400 text-sm">{s}</span>
                ))}
              </div>
            </div>

            <div className="bg-blue-600/20 rounded-xl p-6 border border-blue-500/30">
              <h3 className="text-lg font-bold text-white mb-3">Training Plan</h3>
              {currentAnalysis.drills.map((drill, idx) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-3 mb-2 flex items-center gap-3">
                  <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">{idx + 1}</div>
                  <p className="text-gray-300 text-sm">{drill}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Progress Tracker</h2>
              {Object.entries(progressData).map(([key, data]) => (
                <div key={key} className="mb-4">
                  <div className="flex justify-between mb-2">
                    <span className="text-white capitalize">{skills[key].name}</span>
                    <span className="text-white">{data.current} / {data.target}</span>
                  </div>
                  <div className="bg-slate-700 rounded-full h-3">
                    <div className={`bg-${skills[key].color}-500 h-3 rounded-full`} style={{ width: `${(data.current / data.target) * 100}%` }}></div>
                  </div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className="text-green-400">+{data.improved} improved</span>
                    <span className="text-orange-400">{data.target - data.current} to target</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-4">Training Schedule</h2>
            <div className="mb-4">
              <label className="text-gray-300 mb-2 block">Hours per week: {hoursPerWeek}h</label>
              <input
                type="range"
                min="2"
                max="15"
                value={hoursPerWeek}
                onChange={(e) => setHoursPerWeek(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
            <div className="space-y-3">
              {schedule.map((session, idx) => (
                <div key={idx} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="flex justify-between mb-2">
                    <div className="text-white font-semibold">{session.day}</div>
                    <div className="text-blue-400">{session.duration} min</div>
                  </div>
                  {session.drills.map((drill, i) => (
                    <div key={i} className="text-gray-300 text-sm">• {drill}</div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'match' && (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-4">Match Intelligence</h2>
            
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-red-400 mb-2">Nervous Moments</h3>
              {matchAnalysis.nervousPoints.map((point, idx) => (
                <div key={idx} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-2">
                  <div className="flex justify-between">
                    <span className="text-white">{point.situation}</span>
                    <span className="text-red-400 text-sm">{point.time}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mb-4">
              <h3 className="text-lg font-semibold text-orange-400 mb-2">Confusion Points</h3>
              {matchAnalysis.confusedPoints.map((point, idx) => (
                <div key={idx} className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-2">
                  <div className="flex justify-between">
                    <span className="text-white">{point.situation}</span>
                    <span className="text-orange-400 text-sm">{point.time}</span>
                  </div>
                </div>
              ))}
            </div>

            <div>
              <h3 className="text-lg font-semibold text-blue-400 mb-2">Positioning Errors</h3>
              {matchAnalysis.positioningErrors.map((point, idx) => (
                <div key={idx} className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-2">
                  <div className="flex justify-between mb-1">
                    <span className="text-white">{point.error}</span>
                    <span className="text-blue-400 text-sm">{point.time}</span>
                  </div>
                  <p className="text-green-400 text-sm">✓ {point.correction}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'coach' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 h-[600px] flex flex-col">
              <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-700">
                <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">AI Football Coach</h2>
                  <p className="text-gray-400 text-sm">Ask anything about techniques & training</p>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto mb-4 space-y-3">
                {chatMessages.length === 0 ? (
                  <div className="text-center py-12">
                    <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 mb-4">Ask me about:</p>
                    <div className="grid grid-cols-2 gap-2 max-w-md mx-auto">
                      {['Power shots', 'Finesse technique', 'Defending', 'Passing', 'Weak foot', 'Fitness'].map((topic, i) => (
                        <button
                          key={i}
                          onClick={() => setUserMessage(`How to improve ${topic.toLowerCase()}?`)}
                          className="bg-slate-700 hover:bg-slate-600 text-gray-300 text-sm py-2 px-3 rounded-lg"
                        >
                          {topic}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg ${msg.type === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-gray-200'}`}>
                          <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                        </div>
                      </div>
                    ))}
                    <div ref={chatEndRef} />
                  </>
                )}
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={userMessage}
                  onChange={(e) => setUserMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  className="flex-1 bg-slate-700 text-white px-4 py-3 rounded-lg focus:outline-none"
                />
                <button onClick={handleSendMessage} className="bg-blue-600 text-white px-6 py-3 rounded-lg">
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaySmart;
