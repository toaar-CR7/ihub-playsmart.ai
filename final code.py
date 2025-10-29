import React, { useState, useRef, useEffect } from 'react';
// UPDATED: Removed 'Brain' icon
import { Upload, Video, TrendingUp, Target, Shield, Users, Play, CheckCircle, AlertCircle, Camera, BarChart3, Award, Calendar, Clock, Zap, MessageCircle, Send, Loader2, X, Image as ImageIcon } from 'lucide-react';

/**
 * --- GEMINI API CALLER ---
 */
const callGeminiAPI = async (payload, retries = 3, delay = 1000) => {
  const apiKey = ""; // Leave this empty. Canvas will handle it.
  const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;

  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const candidate = result.candidates?.[0];

      if (candidate && candidate.content?.parts?.[0]?.text) {
        return candidate.content.parts[0].text;
      } else {
        console.error('Invalid response structure:', result);
        throw new Error('Invalid response structure from API.');
      }

    } catch (error) {
      console.error(`Attempt ${i + 1} failed:`, error);
      if (i === retries - 1) {
        return `Error: Unable to get response from AI. ${error.message}`;
      }
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

/**
 * --- HELPER FUNCTION: FILE TO BASE64 ---
 */
const convertFileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]); // Get just the base64 part
    reader.onerror = (error) => reject(error);
  });
};

// --- SYSTEM PROMPTS ---

const AI_COACH_SYSTEM_PROMPT = `
You are "Coach AI," an expert football coach and tactician. Your personality is encouraging, clear, and professional.
Your mission is to help coaches, players, and fans understand football. You must provide safe, practical, and well-explained advice.
RULES:
1. NEVER give medical advice. If asked about an injury, your *only* response is to tell the user to consult a qualified medical professional.
2. Be specific. Don't just say "practice passing." Give a specific drill.
3. Format your answers clearly. Use headings, bullet points, and numbered lists.
4. Keep your answers concise and easy to read on a mobile phone (under 150 words).
`;

const AI_ANALYSIS_SYSTEM_PROMPT = (skillCategory, skillName) => {
  let frameDescriptions = '';
  let skillSpecificInstruction = '';
  const lowerSkillName = skillName.toLowerCase();

  // 1. DYNAMIC FRAME DESCRIPTIONS
  if (skillCategory === 'shooting' || skillCategory === 'passing') {
    frameDescriptions = `
You will receive 5 sequential keyframe images.
- Image 1: "Approach" (moment before contact)
- Image 2: "Contact" (moment of ball strike)
- Image 3: "Follow-through (Start)" (moment just after contact)
- Image 4: "Follow-through (End)" (end of the motion)
- Image 5: "Ball Trajectory" (the ball's path in the air)
    `;
    if (lowerSkillName.includes('pass') || lowerSkillName.includes('cross') || lowerSkillName.includes('ball')) {
      skillSpecificInstruction = `
SPECIAL INSTRUCTION FOR PASSING: Pay close attention to the pass weight/power based on the player's body shape. In your 'issues' section, you **must** comment on whether the pass power appears too high (too fast) or too low (too slow).
`;
    }
  } else if (skillCategory === 'defending') {
    frameDescriptions = `
You will receive 4 sequential keyframe images.
- Image 1: "Approach" (closing down the attacker)
- Image 2: "Jockey/Stance" (body position, balance)
- Image 3: "Action" (the moment of the tackle, interception, or block)
- Image 4: "Recovery" (regaining balance or possession after the action)
    `;
    skillSpecificInstruction = `
SPECIAL INSTRUCTION FOR DEFENDING: Focus on body shape, balance, and timing. Is the player on their toes? Is their body angled correctly? Did they over-commit?
`;
  } else if (skillCategory === 'positioning') {
    frameDescriptions = `
You will receive 4 sequential keyframe images.
- Image 1: "Initial Position" (where the player is as the play begins)
- Image 2: "Scan/Movement" (player scanning or moving into space)
- Image 3: "Action Phase" (where the player is when the ball is played/received)
- Image 4: "Recovery/Transition" (where the player moves next)
    `;
    skillSpecificInstruction = `
SPECIAL INSTRUCTION FOR POSITIONING: Focus on awareness. Is the player scanning? Are they in a good space to receive or defend? Are they ball-watching?
`;
  }

  // 2. HARSH SCORING & STRICTER STRENGTHS
  return `
You are a harsh, world-class critic and AI football analyst.
Your job is to be extremely strict with your scoring. A score of 50-60 is for an average amateur. A score of 70-80 is for a top-tier amateur. A score of 90+ is for a world-class professional. **Do not give high scores easily.** Find the flaws.

You are analyzing a "${skillName}".
${frameDescriptions}

Analyze the *entire motion* across all images. Identify issues in the sequence.
Provide one, consolidated report.

${skillSpecificInstruction}

You MUST respond *only* with a valid JSON object. Do not add "json" or backticks.
The JSON must match this exact schema:
{
  "score": number, // Your HARSH score (0-100) for the *entire* technique
  "proScore": number, // A professional score (e.g., 90-95)
  "issues": [ { "severity": "high" | "medium" | "low", "issue": "Specific issue you see (e.g., 'Plant foot too far in Frame 2')", "fix": "Specific correction" } ],
  "strengths": [ "Strength 1 (e.g., 'Good body shape in Frame 1')", "Strength 2" ],
  "drills": [
    { "drill": "Drill 1 description", "duration": 15 }, // Duration in minutes
    { "drill": "Drill 2 description", "duration": 20 }  // Duration in minutes
  ]
}

IMPORTANT: You **must** provide at least one 'issue'. If the form is near-perfect, find a minor, subtle point for improvement. For 'strengths', be critical: **only list 1-2 *clear* and *significant* strengths**. Do not list basic things. **Do not** return an empty array for 'issues'.

--- NEW CRITICAL RULE ---
The "issue" and "fix" strings inside the 'issues' array **MUST NOT be empty strings (""), null, or whitespace-only strings.** They must contain descriptive, helpful text.
The "strength" strings inside the 'strengths' array **MUST NOT be empty strings (""), null, or whitespace-only strings.**
The "drill" strings inside the 'drills' array **MUST NOT be empty strings (""), null, or whitespace-only strings.**
`;
};

// --- ANALYSIS_RESPONSE_SCHEMA ---
const ANALYSIS_RESPONSE_SCHEMA = {
  type: "OBJECT",
  properties: {
    "score": { "type": "NUMBER" },
    "proScore": { "type": "NUMBER" },
    "issues": {
      "type": "ARRAY",
      "items": {
        "type": "OBJECT",
        "properties": {
          "severity": { "type": "STRING" },
          "issue": { "type": "STRING", "minLength": 1 }, // <-- THE FIX
          "fix": { "type": "STRING", "minLength": 1 }   // <-- THE FIX
        }
      }
    },
    "strengths": {
      "type": "ARRAY",
      "items": { "type": "STRING", "minLength": 1 } // <-- THE FIX
    },
    "drills": {
      "type": "ARRAY",
      "items": {
        "type": "OBJECT",
        "properties": {
          "drill": { "type": "STRING", "minLength": 1 }, // <-- THE FIX
          "duration": { "type": "NUMBER" }
        }
      }
    }
  },
  required: ["score", "proScore", "issues", "strengths", "drills"]
};

/**
 * --- MODAL COMPONENT ---
 */
const Modal = ({ message, onClose }) => {
  if (!message) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 max-w-sm w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-white">Notification</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className="text-gray-300 text-sm mb-6">{message}</p>
        <button
          onClick={onClose}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-all"
        >
          Close
        </button>
      </div>
    </div>
  );
};


// --- STATIC DATA (Used for UI rendering) ---
const skills = {
  shooting: {
    name: 'Shooting',
    icon: Target,
    color: 'red',
    subSkills: ['power_shot', 'finesse', 'chip', 'volley', 'bicycle', 'penalty', 'trivela', 'free_kick']
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
  bicycle: 'Bicycle Kick', penalty: 'Penalty', trivela: 'Trivela', free_kick: 'Free Kick',
  ground_pass: 'Ground Pass', lob: 'Lob Pass', through_ball: 'Through Ball', cross: 'Cross',
  long_ball: 'Long Ball', one_touch: 'One Touch',
  jockeying: 'Jockeying', tackling: 'Tackling', interception: 'Interception',
  marking: 'Marking', clearance: 'Clearance', blocking: 'Blocking',
  off_ball: 'Off Ball Movement', spacing: 'Spacing', pressing: 'Pressing',
  transition: 'Transition', shape: 'Team Shape'
};

const keyframeLabelSets = {
  shooting: [
    "1. Approach",
    "2. Contact",
    "3. Follow-Thru (Start)",
    "4. Follow-Thru (End)",
    "5. Ball Trajectory"
  ],
  passing: [
    "1. Approach",
    "2. Contact",
    "3. Follow-Thru (Start)",
    "4. Follow-Thru (End)",
    "5. Ball Trajectory"
  ],
  defending: [
    "1. Approach to Player",
    "2. Jockey / Stance",
    "3. Tackle / Action",
    "4. Recovery / Regain"
  ],
  positioning: [
    "1. Initial Position",
    "2. Scan / Movement",
    "3. Action Phase",
    "4. Recovery / Transition"
  ]
};

const getDefaultProgress = () => {
  const defaultData = {};
  for (const skillKey in skills) {
    defaultData[skillKey] = {
      subSkills: {}
    };
    for (const subSkillKey of skills[skillKey].subSkills) {
      defaultData[skillKey].subSkills[subSkillKey] = {
        current: 0,
        target: 100
      };
    }
  }
  return defaultData;
};


// --- *** THIS IS THE FINAL FIX *** ---
// --- NEW: HELPER FUNCTION TO FIX BLANK AI RESPONSES ---
// We will manually clean the AI's response to kill the "blank issue" bug.
const sanitizeAnalysisData = (data) => {
  // Create a copy to avoid modifying the original data unexpectedly
  const cleanData = JSON.parse(JSON.stringify(data));

  // 1. Clean Issues
  if (cleanData.issues && Array.isArray(cleanData.issues)) {
    cleanData.issues = cleanData.issues.filter(item =>
      item.issue && item.issue.trim().length > 0 &&
      item.fix && item.fix.trim().length > 0
    );
  } else {
    cleanData.issues = [];
  }

  // 2. Clean Strengths
  if (cleanData.strengths && Array.isArray(cleanData.strengths)) {
    cleanData.strengths = cleanData.strengths.filter(strength =>
      strength && strength.trim().length > 0
    );
  } else {
    cleanData.strengths = [];
  }

  // 3. Clean Drills
  if (cleanData.drills && Array.isArray(cleanData.drills)) {
    cleanData.drills = cleanData.drills.filter(drillItem =>
      drillItem.drill && drillItem.drill.trim().length > 0 && drillItem.duration
    );
  } else {
    cleanData.drills = [];
  }

  return cleanData;
};


const PlaySmart = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedVideo, setUploadedVideo] = useState(null);

  const [keyframes, setKeyframes] = useState({
    frame1: null,
    frame2: null,
    frame3: null,
    frame4: null,
    frame5: null,
  });

  const [analyzing, setAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const [selectedSkill, setSelectedSkill] = useState(null);
  const [selectedSubSkill, setSelectedSubSkill] = useState(null);

  const [hoursPerWeek, setHoursPerWeek] = useState(5);
  const [chatMessages, setChatMessages] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  const [progressData, setProgressData] = useState(getDefaultProgress());
  const [trainingDrills, setTrainingDrills] = useState([]);
  const [weeklySchedule, setWeeklySchedule] = useState([]);

  const [keyframeLabels, setKeyframeLabels] = useState(keyframeLabelSets.shooting);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  useEffect(() => {
    // Load Progress
    const savedProgress = localStorage.getItem('playSmartProgress');
    if (savedProgress) {
      const parsedProgress = JSON.parse(savedProgress);
      const defaultData = getDefaultProgress();

      for (const skillKey in defaultData) {
        if (parsedProgress[skillKey]) {
          for (const subSkillKey in defaultData[skillKey].subSkills) {
            if (parsedProgress[skillKey].subSkills[subSkillKey]) {
              defaultData[skillKey].subSkills[subSkillKey] = parsedProgress[skillKey].subSkills[subSkillKey];
            }
          }
        }
      }
      setProgressData(defaultData);
    }

    // Load Training Drills
    const savedDrills = localStorage.getItem('playSmartTrainingDrills');
    if (savedDrills) {
      setTrainingDrills(JSON.parse(savedDrills));
    }
  }, []); // Empty array means this runs only once on mount

  // Update logic when selectedSkill changes
  useEffect(() => {
    if (selectedSkill) {
      setKeyframeLabels(keyframeLabelSets[selectedSkill]);
      setSelectedSubSkill(null);
      setUploadedVideo(null);
      setKeyframes({ frame1: null, frame2: null, frame3: null, frame4: null, frame5: null });
    }
  }, [selectedSkill]);

  const generateDynamicSchedule = () => {
    if (trainingDrills.length === 0) {
      setModalMessage("Your 'Drill Bank' is empty. Analyze a skill first to get recommended drills.");
      setWeeklySchedule([]);
      return;
    }

    const totalMinutesPerWeek = hoursPerWeek * 60;
    // Aim for sessions of ~90 mins, but be flexible. Min 1 session.
    const sessionsPerWeek = Math.max(1, Math.round(totalMinutesPerWeek / 90));
    const minutesPerSession = Math.floor(totalMinutesPerWeek / sessionsPerWeek);

    if (minutesPerSession < 30) {
      setModalMessage(`At ${hoursPerWeek} hours/week, your ${sessionsPerWeek} sessions are too short. Try increasing your hours or you'll have one longer session.`);
      // Allow it to proceed, it will just be one session
    }

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].slice(0, sessionsPerWeek);
    let drillIndex = 0; // To loop through the drill bank

    const newSchedule = days.map(day => {
      const sessionDrills = [];
      let sessionTime = 0;

      // Keep adding drills until the session is ~full
      while (sessionTime < minutesPerSession && trainingDrills.length > 0) {
        // Get the next drill and loop back to the start if we reach the end
        const drill = trainingDrills[drillIndex % trainingDrills.length];
        drillIndex++;

        const drillDuration = drill.duration || 15; // Default 15 mins if not specified

        // Only add drill if it fits (or if it's the first drill)
        if (sessionTime + drillDuration <= minutesPerSession * 1.2 || sessionDrills.length === 0) {
          sessionDrills.push(drill);
          sessionTime += drillDuration;
        } else {
          // This session is full
          break;
        }
      }

      return {
        day: day,
        drills: sessionDrills,
        duration: sessionTime
      };
    });

    setWeeklySchedule(newSchedule);
  };


  /**
   * --- REAL AI CHATBOT ---
   */
  const getAIResponse = async (message) => {
    setIsAiTyping(true);
    const payload = {
      contents: [{
        role: "user",
        parts: [{ text: message }]
      }],
      systemInstruction: {
        parts: [{ text: AI_COACH_SYSTEM_PROMPT }]
      }
    };

    const responseText = await callGeminiAPI(payload);
    setIsAiTyping(false);
    return responseText;
  };

  const handleSendMessage = async () => {
    const message = userMessage.trim();
    if (message === '') return;

    setChatMessages(prev => [...prev, { type: 'user', text: message }]);
    setUserMessage('');

    const aiResponse = await getAIResponse(message);

    setChatMessages(prev => [...prev, { type: 'ai', text: aiResponse }]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * --- File Selection Logic ---
   */
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedVideo(file);
      setAnalysisComplete(false);
      // Reset 5 captured frames
      setKeyframes({ frame1: null, frame2: null, frame3: null, frame4: null, frame5: null });
    } else {
      setModalMessage("Please upload a valid video file (e.g., .mp4, .mov).");
      setUploadedVideo(null);
    }
  };

  /**
   * --- In-App Screenshot Function ---
   */
  const handleCaptureFrame = (frameSlot) => {
    if (!videoRef.current || !canvasRef.current) {
      setModalMessage("Error: Video player not ready.");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // --- FIX FOR CUT SCREENSHOT ---
    // Check if video metadata is loaded. If videoWidth is 0, it's not ready.
    if (!video.videoWidth || video.videoWidth === 0) {
      setModalMessage("Video is still loading. Please wait a moment after it appears and try again.");
      return;
    }
    // --- END FIX ---

    // Match canvas size to video's intrinsic size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame onto the canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get the image data from the canvas as a data URL
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9); // 90% quality JPEG

    // Update the state
    setKeyframes(prevFrames => ({
      ...prevFrames,
      [frameSlot]: dataUrl
    }));
  };

  /**
   * --- CRITICAL UPDATE: REAL AI ANALYSIS ---
   * Now sends 4 OR 5 frames and SANITIZES the response
   */
  const handleRealAnalysis = async () => {
    const isShootingOrPassing = selectedSkill === 'shooting' || selectedSkill === 'passing';

    // Dynamic check for captured frames
    let allFramesCaptured = keyframes.frame1 && keyframes.frame2 && keyframes.frame3 && keyframes.frame4;
    if (isShootingOrPassing) {
      allFramesCaptured = allFramesCaptured && keyframes.frame5;
    }

    if (!allFramesCaptured) {
      setModalMessage(`Please capture all ${isShootingOrPassing ? 5 : 4} keyframes before analyzing.`);
      return;
    }

    setAnalyzing(true);

    try {
      const skillName = subSkillNames[selectedSubSkill];

      const getBase64 = (dataUrl) => dataUrl.split(',')[1];

      // --- NEW: Dynamically build payload parts ---
      const payloadParts = [
        { text: `Analyze this ${isShootingOrPassing ? 5 : 4}-frame sequence for a "${skillName}".` },
        { inlineData: { mimeType: 'image/jpeg', data: getBase64(keyframes.frame1) } },
        { inlineData: { mimeType: 'image/jpeg', data: getBase64(keyframes.frame2) } },
        { inlineData: { mimeType: 'image/jpeg', data: getBase64(keyframes.frame3) } },
        { inlineData: { mimeType: 'image/jpeg', data: getBase64(keyframes.frame4) } }
      ];

      // Add 5th frame only if needed
      if (isShootingOrPassing) {
        payloadParts.push({ inlineData: { mimeType: 'image/jpeg', data: getBase64(keyframes.frame5) } });
      }

      const payload = {
        contents: [{ parts: payloadParts }],
        systemInstruction: {
          parts: [{ text: AI_ANALYSIS_SYSTEM_PROMPT(selectedSkill, skillName) }]
        },
        generationConfig: {
          responseMimeType: "application/json",
          responseSchema: ANALYSIS_RESPONSE_SCHEMA,
        }
      };

      const responseText = await callGeminiAPI(payload);
      const rawAnalysisData = JSON.parse(responseText); // Get the raw, potentially "dirty" data

      // --- *** THIS IS THE FINAL FIX *** ---
      // Manually clean and sanitize the data *before* saving it to state
      const analysisData = sanitizeAnalysisData(rawAnalysisData);
      // --- *** END FIX *** ---

      // Save Progress (uses clean data)
      setProgressData(prevProgress => {
        const newProgress = JSON.parse(JSON.stringify(prevProgress));
        if (analysisData.score > newProgress[selectedSkill].subSkills[selectedSubSkill].current) {
          newProgress[selectedSkill].subSkills[selectedSubSkill].current = analysisData.score;
        }
        localStorage.setItem('playSmartProgress', JSON.stringify(newProgress));
        return newProgress;
      });

      // Save Drills (uses clean data)
      setTrainingDrills(prevDrills => {
        const newDrills = analysisData.drills || [];
        const uniqueNewDrills = newDrills.filter(newDrill =>
          !prevDrills.some(existingDrill => existingDrill.drill === newDrill.drill)
        );
        const updatedDrills = [...prevDrills, ...uniqueNewDrills];
        localStorage.setItem('playSmartTrainingDrills', JSON.stringify(updatedDrills));
        return updatedDrills;
      });

      setCurrentAnalysis(analysisData); // Save the *clean* data
      setAnalysisComplete(true);
      setActiveTab('analysis');

    } catch (error) {
      console.error('Analysis failed:', error);
      setModalMessage(`Analysis Failed: ${error.message}. Make sure the AI returns valid JSON.`);
    } finally {
      setAnalyzing(false);
    }
  };

  // Check if all keyframes for the current skill are captured
  const checkAllFramesCaptured = () => {
    const isShootingOrPassing = selectedSkill === 'shooting' || selectedSkill === 'passing';
    let allCaptured = keyframes.frame1 && keyframes.frame2 && keyframes.frame3 && keyframes.frame4;
    if (isShootingOrPassing) {
      allCaptured = allCaptured && keyframes.frame5;
    }
    return allCaptured;
  };
  const allKeyframesCaptured = checkAllFramesCaptured();


  // Helper function to get the right color for progress bars
  const getBarColor = (skillKey) => {
    const colorMap = {
      shooting: 'bg-red-500',
      passing: 'bg-blue-500',
      defending: 'bg-green-500',
      positioning: 'bg-purple-500',
    };
    return colorMap[skillKey] || 'bg-gray-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <Modal message={modalMessage} onClose={() => setModalMessage('')} />
      {/* Hidden Canvas for Screenshots */}
      <canvas ref={canvasRef} className="hidden"></canvas>

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

        {/* --- UPDATED: TABS (Removed Match AI) --- */}
        <div className="flex flex-wrap gap-2 mb-6 bg-slate-800/50 p-2 rounded-xl">
          {[
            { id: 'upload', icon: Upload, label: 'Upload' },
            { id: 'analysis', icon: BarChart3, label: 'Analysis' },
            { id: 'progress', icon: TrendingUp, label: 'Progress' },
            { id: 'schedule', icon: Calendar, label: 'Schedule' },
            { id: 'coach', icon: MessageCircle, label: 'AI Coach' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={tab.id === 'analysis' && !analysisComplete}
              className={`flex-1 min-w-[90px] py-2 px-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 text-sm ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              } ${tab.id === 'analysis' && !analysisComplete ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* --- "UPLOAD" TAB --- */}
        {activeTab === 'upload' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Video Analysis Pipeline</h2>

              {/* --- Step 1: Select Category --- */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Step 1: Select a Category</h3>
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
              </div>

              {/* --- Step 2: Select Sub-Skill (Show after category) --- */}
              {selectedSkill && (
                <div className="border-t border-slate-700 pt-4 mt-4">
                  <h3 className="text-lg font-semibold text-white mb-3">Step 2: Select a Skill</h3>
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
                </div>
              )}

              {/* --- Step 3: Upload Video (Show after sub-skill) --- */}
              {selectedSkill && selectedSubSkill && !uploadedVideo && (
                <div className="border-t border-slate-700 pt-4 mt-4">
                  <h3 className="text-lg font-semibold text-white mb-3">Step 3: Upload Your Video</h3>
                  <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept="video/*" className="hidden" />
                  <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 transition-all">
                    <Video className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-lg text-gray-300">Click to upload your video (MP4, MOV)</p>
                  </div>
                </div>
              )}

              {/* --- Step 4: Capture Keyframes (Show after video) --- */}
              {selectedSkill && selectedSubSkill && uploadedVideo && (
                <div className="border-t border-slate-700 pt-4 mt-4 space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Step 4: Capture {keyframeLabels.length} Keyframes for <span className="text-blue-400">{subSkillNames[selectedSubSkill]}</span></h3>
                    <video
                      ref={videoRef}
                      src={URL.createObjectURL(uploadedVideo)}
                      controls
                      className="w-full rounded-lg max-h-64 object-contain bg-black"
                      onLoadedMetadata={(e) => {
                        console.log("Video metadata loaded");
                      }}
                    />
                  </div>

                  <div>
                    <p className="text-sm text-gray-400 mb-3">Play/pause your video and capture the {keyframeLabels.length} key moments.</p>

                    {/* DYNAMIC KEYFRAME UI */}
                    <div className={`grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3`}>
                      {keyframeLabels.map((label, index) => {
                        const frameKey = `frame${index + 1}`;
                        // This check handles the 4-frame vs 5-frame logic
                        if (index < keyframeLabels.length) {
                          return (
                            <div className="text-center" key={frameKey}>
                              <div className="w-full aspect-video bg-slate-700 rounded-lg mb-2 flex items-center justify-center overflow-hidden">
                                {keyframes[frameKey] ? (
                                  <img src={keyframes[frameKey]} alt={label} className="w-full h-full object-cover" />
                                ) : (
                                  <ImageIcon className="w-8 h-8 text-gray-500" />
                                )}
                              </div>
                              <button
                                onClick={() => handleCaptureFrame(frameKey)}
                                className="w-full text-xs bg-slate-700 hover:bg-slate-600 text-white py-2 px-2 rounded-lg"
                              >
                                {label}
                              </button>
                            </div>
                          );
                        }
                        return null; // Don't render frame 5 for defending/positioning
                      })}
                    </div>
                  </div>

                  {/* --- Step 5: Analyze --- */}
                  <div>
                    {analyzing ? (
                      <div className="bg-blue-600 text-white py-3 px-4 rounded-xl text-center flex items-center justify-center gap-2">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing {subSkillNames[selectedSubSkill]}...
                      </div>
                    ) : (
                      <button
                        onClick={handleRealAnalysis}
                        disabled={!allKeyframesCaptured}
                        className={`w-full text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${
                          !allKeyframesCaptured
                            ? 'bg-gray-600 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                      >
                        <Play className="w-5 h-5" />
                        {!allKeyframesCaptured ? `Capture all ${keyframeLabels.length} frames` : `Analyze ${subSkillNames[selectedSubSkill]}`}
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- "ANALYSIS" TAB --- */}
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
                <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${(currentAnalysis.score / currentAnalysis.proScore) * 100}%` }}></div>
              </div>
              <div className="text-center text-sm mt-2 text-orange-400">Gap: {currentAnalysis.proScore - currentAnalysis.score} points</div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3">Issues Detected</h3>
              <div className="space-y-2">
                {currentAnalysis.issues.length === 0 ? (
                  <div className="p-3 rounded-lg bg-green-500/10 border-l-4 border-green-500">
                    <p className="text-white text-sm">AI detected no major issues. Great job!</p>
                  </div>
                ) : (
                  currentAnalysis.issues.map((item, idx) => (
                    <div key={idx} className={`p-3 rounded-lg border-l-4 ${item.severity === 'high' ? 'bg-red-500/10 border-red-500' : (item.severity === 'medium' ? 'bg-orange-500/10 border-orange-500' : 'bg-yellow-500/10 border-yellow-500')}`}>
                      <p className="text-white text-sm mb-1">{item.issue}</p>
                      <p className="text-green-400 text-xs">✓ {item.fix}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3">Strengths</h3>
              <div className="flex flex-wrap gap-2">
                {currentAnalysis.strengths.length === 0 ? (
                  <p className="text-gray-400 text-sm">No significant strengths detected. Keep practicing!</p>
                ) : (
                  currentAnalysis.strengths.map((s, i) => (
                    <span key={i} className="bg-green-500/10 border border-green-500/30 rounded-lg px-3 py-1 text-green-400 text-sm">{s}</span>
                  ))
                )}
              </div>
            </div>

            <div className="bg-blue-600/20 rounded-xl p-6 border border-blue-500/30">
              <h3 className="text-lg font-bold text-white mb-3">Training Plan (Added to your Drill Bank)</h3>
              {currentAnalysis.drills.length === 0 ? (
                 <p className="text-gray-400 text-sm">No specific drills added. Focus on the corrections.</p>
              ) : (
                currentAnalysis.drills.map((drill, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-lg p-3 mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">{idx + 1}</div>
                      <p className="text-gray-300 text-sm">{drill.drill}</p>
                    </div>
                    <span className="text-blue-400 text-sm">{drill.duration} min</span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'progress' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-6">Your Skill Progress</h2>

              {Object.keys(skills).map((skillKey) => {
                const skill = skills[skillKey];
                const skillProgress = progressData[skillKey];

                return (
                  <div key={skillKey} className="mb-6">
                    <div className="flex items-center gap-3 mb-3">
                      <skill.icon className={`w-6 h-6 text-${skill.color}-400`} />
                      <h3 className={`text-lg font-semibold text-white`}>{skill.name}</h3>
                    </div>

                    <div className="space-y-3">
                      {skill.subSkills.map((subSkillKey) => {
                        const subSkillData = skillProgress.subSkills[subSkillKey];
                        const subSkillName = subSkillNames[subSkillKey];
                        const score = subSkillData.current;
                        const target = subSkillData.target;
                        const percentage = (score / target) * 100;

                        return (
                          <div key={subSkillKey} className="pl-4 border-l-2 border-slate-700">
                            <div className="flex justify-between mb-1">
                              <span className="text-sm text-gray-300">{subSkillName}</span>
                              <span className={`text-sm ${score > 0 ? 'text-white' : 'text-gray-500'}`}>
                                {score} / {target}
                              </span>
                            </div>
                            <div className="bg-slate-700 rounded-full h-2.5">
                              <div
                                className={`${getBarColor(skillKey)} h-2.5 rounded-full transition-all duration-500`}
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Training Schedule Generator</h2>
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
              <button
                onClick={generateDynamicSchedule}
                className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-blue-700 transition-all"
              >
                Generate My Weekly Schedule
              </button>
            </div>

            {weeklySchedule.length > 0 && (
              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-bold text-white mb-4">Your Generated Plan</h3>
                <div className="space-y-3">
                  {weeklySchedule.map((session, idx) => (
                    <div key={idx} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                      <div className="flex justify-between mb-2">
                        <div className="text-white font-semibold">{session.day}</div>
                        <div className="text-blue-400">{session.duration} min</div>
                      </div>
                      <ul className="list-disc list-inside space-y-1">
                        {session.drills.map((drill, i) => (
                          <li key={i} className="text-gray-300 text-sm">
                            {drill.drill} <span className="text-gray-500">({drill.duration} min)</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-4">Your AI Drill Bank</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {trainingDrills.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center">Your Drill Bank is empty. Analyze a skill to add drills.</p>
                ) : (
                  trainingDrills.map((drill, idx) => (
                    <div key={idx} className="bg-slate-700 rounded-lg p-3 flex justify-between items-center">
                      <p className="text-gray-300 text-sm">{drill.drill}</p>
                      <span className="text-blue-400 text-sm">{drill.duration} min</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* --- "Match AI" Tab is GONE --- */}

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
                    {isAiTyping && (
                      <div className="flex justify-start">
                        <div className="bg-slate-700 text-gray-200 p-3 rounded-lg">
                          <Loader2 className="w-5 h-5 animate-spin" />
                        </div>
                      </div>
                    )}
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
