import React, { useState, useRef, useEffect } from 'react';
// UPDATED: Removed 'Brain' icon
import { Upload, Video, TrendingUp, Target, Shield, Users, Play, CheckCircle, AlertCircle, Camera, BarChart3, Award, Calendar, Clock, Zap, MessageCircle, Send, Loader2, X, Image as ImageIcon } from 'lucide-react';

/**
 * --- GEMINI API CALLER ---
 * This function calls the Gemini API.
 * It includes an empty API key (Canvas will handle it), error handling, and exponential backoff for retries.
 */
const callGeminiAPI = async (payload, retries = 3, delay = 1000) => {
  const apiKey = "AIzaSyBDKQ-hkhWvCDlnj0p9VGK6bYpdYXYPZ8o"; // Bhai api key ko idhar paste kar dena.
  const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;

  // Retry loop for API call robustness
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
           let errorBodyText = await response.text();
           console.error("API Error Body:", errorBodyText);
           let specificError = `HTTP error! status: ${response.status}`;
           try {
               const errorJson = JSON.parse(errorBodyText);
               if (errorJson?.error?.message) {
                   specificError += `, message: ${errorJson.error.message}`;
               } else { specificError += `, message: ${errorBodyText.substring(0,200)}`; }
           } catch { specificError += `, message: ${errorBodyText.substring(0,200)}`; }
           throw new Error(specificError);
      }


      const result = await response.json();
      const candidate = result.candidates?.[0];

       // Check finish reason for safety or other issues
      if (candidate?.finishReason && candidate.finishReason !== "STOP" && candidate.finishReason !== "MAX_TOKENS") { // Allow MAX_TOKENS
          console.warn("API call finished with reason:", candidate.finishReason);
           if (candidate.finishReason === "SAFETY") {
               throw new Error("AI response blocked due to safety settings.");
           }
            // Handle other non-STOP reasons if necessary
            throw new Error(`AI processing stopped unexpectedly: ${candidate.finishReason}`);
      }

      // Check for actual text content
      if (candidate?.content?.parts?.[0]?.text) {
        return candidate.content.parts[0].text; // Success
      }
      // If no text, but finished, it's potentially an issue (e.g., asked for JSON but didn't get it)
      else if (candidate?.finishReason) {
           console.error('API finished but no text content found:', result);
           throw new Error(`API finished with reason ${candidate.finishReason} but returned no text.`);
      }
      // Otherwise, invalid structure
      else {
        console.error('Invalid response structure:', result);
        throw new Error('Invalid response structure from API.');
      }


    } catch (error) {
      console.error(`Attempt ${i + 1} failed:`, error);
      if (i === retries - 1) { // Last retry failed
        // Return a user-friendly error string instead of throwing
        let displayError = error.message;
        if (error.message.includes("safety settings")) { displayError = "Response blocked (safety)."; }
        else if (error.message.includes("Invalid response structure")) { displayError = "Unexpected response format."; }
        else if (error instanceof TypeError && error.message.includes('fetch')) { displayError = "Network error."; }
        else if (error.message.includes("returned no text")) { displayError = "AI returned empty response.";}
        return `Error: API Call Failed. ${displayError}`; // Return error string
      }
      // Wait longer before the next retry
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
   // Fallback error if loop finishes unexpectedly
   return "Error: API call failed after multiple retries.";
};


/**
 * --- HELPER FUNCTION: FILE TO BASE64 ---
 * Converts an image file into a base64 string to send to the API.
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

/**
 * --- AI COACH SYSTEM PROMPT ---
 * Instructions for the general AI chatbot.
 */
const AI_COACH_SYSTEM_PROMPT = `
You are "Coach AI," an expert football coach and tactician. Your personality is encouraging, clear, and professional.
Your mission is to help coaches, players, and fans understand football. You must provide safe, practical, and well-explained advice.
RULES:
1. NEVER give medical advice. If asked about an injury, your *only* response is to tell the user to consult a qualified medical professional.
2. Be specific. Don't just say "practice passing." Give a specific drill.
3. Format your answers clearly. Use headings, bullet points, and numbered lists.
4. Keep your answers concise and easy to read on a mobile phone (under 150 words).
`;

/**
 * --- AI ANALYSIS SYSTEM PROMPT ---
 * Dynamically generated instructions for the image analysis AI.
 */
const AI_ANALYSIS_SYSTEM_PROMPT = (skillCategory, skillName) => {
  let frameDescriptions = '';
  let skillSpecificInstruction = '';
  const lowerSkillName = skillName ? skillName.toLowerCase() : ''; // Add null check

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

You are analyzing a "${skillName || 'selected skill'}".
${frameDescriptions}

Analyze the *entire motion* across all images. Identify issues in the sequence.
Provide one, consolidated report.

${skillSpecificInstruction}

You MUST respond *only* with a valid JSON object adhering precisely to the schema provided. Do not add "json" markdown tags or backticks around the JSON. Do not add any text before or after the JSON object.
The JSON must match this exact schema:
{
  "type": "object",
  "properties": {
    "score": { "type": "number", "description": "Your HARSH score (0-100) for the *entire* technique" },
    "proScore": { "type": "number", "description": "A professional score (e.g., 90-95)" },
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "severity": { "type": "string", "enum": ["high", "medium", "low"] },
          "issue": { "type": "string", "minLength": 1, "description": "Specific issue you see (e.g., 'Plant foot too far in Frame 2')" },
          "fix": { "type": "string", "minLength": 1, "description": "Specific correction" }
        },
        "required": ["severity", "issue", "fix"]
      }
    },
    "strengths": {
      "type": "array",
      "items": { "type": "string", "minLength": 1, "description": "Strength (e.g., 'Good body shape in Frame 1')" }
    },
    "drills": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "drill": { "type": "string", "minLength": 1, "description": "Drill description" },
          "duration": { "type": "number", "description": "Duration in minutes" }
        },
        "required": ["drill", "duration"]
      }
    }
  },
  "required": ["score", "proScore", "issues", "strengths", "drills"]
}


IMPORTANT RULES FOR YOUR RESPONSE:
1.  **Strict JSON:** Output *only* the JSON object defined above. No extra text, explanations, or formatting.
2.  **At least one issue:** You **must** provide at least one item in the 'issues' array. Find a flaw, even a minor one.
3.  **Limited Strengths:** Only list 1-2 *clear* and *significant* strengths in the 'strengths' array. Be critical.
4.  **No Empty Strings:** All strings ("issue", "fix", "strength", "drill") **must** contain meaningful text. Do not return empty strings ("") or whitespace-only strings.
`;
};

/**
 * --- AI ANALYSIS JSON SCHEMA ---
 * Defines the expected structure for the AI's analysis response.
 */
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
          "severity": { "type": "STRING", "enum": ["high", "medium", "low"] }, // Added enum validation
          "issue": { "type": "STRING", "minLength": 1 },
          "fix": { "type": "STRING", "minLength": 1 }
        },
        "required": ["severity", "issue", "fix"]
      }
    },
    "strengths": {
      "type": "ARRAY",
      "items": { "type": "STRING", "minLength": 1 }
    },
    "drills": {
      "type": "ARRAY",
      "items": {
        "type": "OBJECT",
        "properties": {
          "drill": { "type": "STRING", "minLength": 1 },
          "duration": { "type": "NUMBER" }
        },
        "required": ["drill", "duration"]
      }
    }
  },
  required: ["score", "proScore", "issues", "strengths", "drills"]
};

/**
 * --- MODAL COMPONENT ---
 * A simple popup modal for showing errors or notifications.
 */
const Modal = ({ message, onClose }) => {
  if (!message) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity duration-200 opacity-100"> {/* Default visible */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 max-w-sm w-full shadow-xl transform transition-transform duration-200 scale-100"> {/* Default visible */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-white">Notification</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className="text-gray-300 text-sm mb-6">{message}</p>
        <button
          onClick={onClose}
          className="w-full bg-blue-600 text-white py-2.5 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800 transition-all duration-150"
        >
          Close
        </button>
      </div>
    </div>
  );
};


// --- STATIC DATA (Used for UI rendering) ---

// Skill categories, sub-skills, icons, and colors
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

// Maps sub-skill keys to human-readable names
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

// Maps skill categories to their specific keyframe labels (4 or 5)
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

// Creates the default, empty structure for the progress tracker
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


/**
 * --- SANITIZER FUNCTION ---
 * Manually cleans the AI's response to prevent errors from blank/invalid data.
 */
const sanitizeAnalysisData = (data) => {
    try {
        if (typeof data !== 'object' || data === null) {
            console.error("Invalid data object passed to sanitizeAnalysisData:", data);
            return { score: 0, proScore: 90, issues: [], strengths: [], drills: [] };
        }
        const cleanData = {
            score: typeof data.score === 'number' ? Math.max(0, Math.min(100, data.score)) : 0, // Clamp score
            proScore: typeof data.proScore === 'number' ? data.proScore : 90,
            issues: [], strengths: [], drills: [],
        };

        if (Array.isArray(data.issues)) {
            cleanData.issues = data.issues.filter(item =>
                item && typeof item === 'object' &&
                typeof item.issue === 'string' && item.issue.trim().length > 0 &&
                typeof item.fix === 'string' && item.fix.trim().length > 0 &&
                typeof item.severity === 'string' && ['high', 'medium', 'low'].includes(item.severity.toLowerCase())
            );
        }
        if (Array.isArray(data.strengths)) {
            cleanData.strengths = data.strengths.filter(strength =>
                typeof strength === 'string' && strength.trim().length > 0
            );
        }
        if (Array.isArray(data.drills)) {
            cleanData.drills = data.drills.filter(drillItem =>
                drillItem && typeof drillItem === 'object' &&
                typeof drillItem.drill === 'string' && drillItem.drill.trim().length > 0 &&
                typeof drillItem.duration === 'number' && drillItem.duration > 0
            );
        }
        // No longer adding placeholder issue here, let the UI handle empty display
        return cleanData;
    } catch (sanitizeError) {
        console.error("Error during sanitization:", sanitizeError, "Original data:", data);
        return { score: 0, proScore: 90, issues: [], strengths: [], drills: [] }; // Return default on error
    }
};


/**
 * --- MAIN APP COMPONENT ---
 * This is the core of the application.
 */
const PlaySmart = () => {
  // --- STATE MANAGEMENT ---
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [keyframes, setKeyframes] = useState({ frame1: null, frame2: null, frame3: null, frame4: null, frame5: null });
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
  const [weeklySchedule, setWeeklySchedule] = useState([]); // Use setWeeklySchedule to update
  const [keyframeLabels, setKeyframeLabels] = useState(keyframeLabelSets.shooting);

  // --- REFS ---
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const chatEndRef = useRef(null);

  // --- EFFECTS ---

  // Auto-scroll chat
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  // Load data from localStorage on mount
  useEffect(() => {
    try {
        const savedProgress = localStorage.getItem('playSmartProgress');
        if (savedProgress) {
            const parsed = JSON.parse(savedProgress);
            if (typeof parsed === 'object' && parsed !== null) {
                // Safely merge with default structure
                const defaultProg = getDefaultProgress();
                for (const skillKey in defaultProg) {
                    if (parsed[skillKey]?.subSkills) {
                        for (const subSkillKey in defaultProg[skillKey].subSkills) {
                            if (parsed[skillKey].subSkills[subSkillKey]?.current !== undefined) {
                                defaultProg[skillKey].subSkills[subSkillKey] = parsed[skillKey].subSkills[subSkillKey];
                            }
                        }
                    }
                }
                setProgressData(defaultProg);
            } else { localStorage.removeItem('playSmartProgress'); }
        }
    } catch (e) { console.error("Error loading progress:", e); localStorage.removeItem('playSmartProgress'); }

    try {
        const savedDrills = localStorage.getItem('playSmartTrainingDrills');
        if (savedDrills) {
            const parsed = JSON.parse(savedDrills);
            if (Array.isArray(parsed)) {
                setTrainingDrills(parsed.filter(d => d && d.drill && d.duration)); // Basic validation
            } else { localStorage.removeItem('playSmartTrainingDrills'); }
        }
    } catch(e) { console.error("Error loading drills:", e); localStorage.removeItem('playSmartTrainingDrills'); }
  }, []);

  // Reset UI elements when skill category changes
  useEffect(() => {
    if (selectedSkill && keyframeLabelSets[selectedSkill]) { // Check key exists
      setKeyframeLabels(keyframeLabelSets[selectedSkill]);
      setSelectedSubSkill(null);
      setUploadedVideo(null);
      setAnalysisComplete(false); // Reset analysis status
      setCurrentAnalysis(null); // Clear previous analysis data
      setKeyframes({ frame1: null, frame2: null, frame3: null, frame4: null, frame5: null });
    }
  }, [selectedSkill]);

  // --- DYNAMIC SCHEDULE GENERATOR ---
  const generateDynamicSchedule = () => {
    if (!Array.isArray(trainingDrills) || trainingDrills.length === 0) {
      setModalMessage("Drill Bank empty. Analyze skills first.");
      setWeeklySchedule([]); return; // Use setter function
    }
    const totalMinutes = hoursPerWeek * 60;
    const sessions = Math.max(1, Math.round(totalMinutes / 90));
    const minPerSession = Math.floor(totalMinutes / sessions);
    if (minPerSession < 15) { setModalMessage(`Sessions too short (${minPerSession}m). Increase hours.`); setWeeklySchedule([]); return; } // Use setter
    if (minPerSession < 30 && sessions > 1) { setModalMessage(`Note: Sessions short (${minPerSession}m).`); }

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].slice(0, sessions);
    const shuffled = [...trainingDrills].sort(() => Math.random() - 0.5);
    let drillIdx = 0;
    const newSched = days.map(day => {
      let sessionDrills = []; let sessionTime = 0; let added = new Set();
      let attempts = 0; const maxAttempts = shuffled.length * 3;
      while (sessionTime < minPerSession && attempts < maxAttempts && shuffled.length > 0) {
        attempts++;
        const currentIdx = drillIdx % shuffled.length;
        const drill = shuffled[currentIdx]; drillIdx++;
        if (!drill || typeof drill.duration !== 'number' || typeof drill.drill !== 'string') continue; // Skip invalid drills
        const duration = drill.duration || 15;
        if (!added.has(drill.drill) && (sessionTime + duration <= minPerSession * 1.15 || sessionDrills.length === 0)) { // Allow 15% overrun
          sessionDrills.push(drill); sessionTime += duration; added.add(drill.drill);
        }
        if (attempts >= shuffled.length && sessionTime < minPerSession * 0.5) break; // Break early if not filling
      }
      if (sessionTime < 15 && shuffled.length > 0) console.warn(`${day} session short (${sessionTime}m)`);
      return { day, drills: sessionDrills, duration: sessionTime };
    }).filter(s => s.duration > 0); // Remove empty sessions

    if (newSched.length < sessions && trainingDrills.length > 0) setModalMessage(`Generated ${newSched.length} sessions. Some may have been too short.`);
    else if (newSched.length === 0 && trainingDrills.length > 0) setModalMessage(`Could not generate schedule. Drills too long for sessions (${minPerSession}m)?`);

    setWeeklySchedule(newSched); // Use setter function
  };

  // --- AI COACH CHATBOT FUNCTIONS ---
  const getAIResponse = async (message) => {
    setIsAiTyping(true); // Set typing indicator ON
     try {
        const payload = { contents: [{ role: "user", parts: [{ text: message }] }], systemInstruction: { parts: [{ text: AI_COACH_SYSTEM_PROMPT }] } };
        const responseText = await callGeminiAPI(payload);
        return responseText; // Return potentially successful or error string from callGeminiAPI
     } catch (error) { // Catch unexpected errors during the process
         console.error("Unexpected error in getAIResponse:", error);
         return "Sorry, an unexpected error occurred.";
     } finally {
        setIsAiTyping(false); // Set typing indicator OFF
     }
  };

  const handleSendMessage = async () => {
    const message = userMessage.trim();
    if (message === '' || isAiTyping) return; // Prevent sending empty or while typing

    setChatMessages(prev => [...prev, { type: 'user', text: message }]);
    setUserMessage('');

    const aiResponse = await getAIResponse(message); // handles typing indicator
    setChatMessages(prev => [...prev, { type: 'ai', text: aiResponse }]);Canvas
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); }
  };

  // --- VIDEO ANALYSIS FUNCTIONS ---

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
     if (!file) return; // Handle no file selected
    const maxSize = 100 * 1024 * 1024; // 100 MB
    if (file.size > maxSize) { showModal(`Video too large (max 100MB).`); setUploadedVideo(null); if (fileInputRef.current) fileInputRef.current.value = ""; return; }
    if (file.type.startsWith('video/')) {
        setUploadedVideo(file);
        setAnalysisComplete(false); // Reset analysis state
        setCurrentAnalysis(null); // Clear previous analysis
        setKeyframes({ frame1: null, frame2: null, frame3: null, frame4: null, frame5: null }); // Reset frames
    } else {
        showModal("Please upload a valid video file.");
        setUploadedVideo(null);
        if (fileInputRef.current) fileInputRef.current.value = ""; // Clear input if invalid
    }
  };


  const handleCaptureFrame = (frameSlot) => {
    if (!videoRef.current) { showModal("Video player not ready."); console.error("videoRef missing"); return; }
    if (!canvasRef.current) { showModal("Canvas element missing."); console.error("canvasRef missing"); return; }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // Use readyState > 0 (HAVE_METADATA) as a more reliable check
    if (video.readyState < 1 || !video.videoWidth || video.videoWidth === 0) {
      setModalMessage("Video is still loading metadata. Please wait.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
     if (!ctx) { showModal("Could not get canvas context."); console.error("Canvas context failed"); return; }

    try {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9); // Use JPEG
        setKeyframes(prevFrames => ({ ...prevFrames, [frameSlot]: dataUrl }));
    } catch (error) {
        console.error("Frame capture error:", error);
        showModal("Error capturing frame.");
    }
  };

  // --- THE CORE AI ANALYSIS FUNCTION ---
  const handleRealAnalysis = async () => {
    if (!selectedSkill || !selectedSubSkill) { showModal("Please select skills first."); return; }

    const requiredFramesCount = (keyframeLabelSets[selectedSkill] || []).length; // Use current labels
    let allCaptured = true;
    for (let i = 1; i <= requiredFramesCount; i++) { if (!keyframes[`frame${i}`]) allCaptured = false; }
    if (!allCaptured) { showModal(`Capture all ${requiredFramesCount} frames first.`); return; }

    setAnalyzing(true);
    setCurrentAnalysis(null); // Clear previous analysis immediately
    setAnalysisComplete(false);

    try {
      const skillName = subSkillNames[selectedSubSkill];
      const getBase64 = (dataUrl) => dataUrl ? dataUrl.split(',')[1] : null;
      const payloadParts = [{ text: `Analyze this ${requiredFramesCount}-frame sequence for a "${skillName}".` }];
      for (let i = 1; i <= requiredFramesCount; i++) {
          const frameData = getBase64(keyframes[`frame${i}`]);
          if (!frameData) throw new Error(`Frame ${i} invalid.`);
          payloadParts.push({ inlineData: { mimeType: 'image/jpeg', data: frameData } }); // Sending JPEG
      }

      const payload = {
          contents: [{ parts: payloadParts }],
          systemInstruction: { parts: [{ text: AI_ANALYSIS_SYSTEM_PROMPT(selectedSkill, skillName) }] },
          generationConfig: { responseMimeType: "application/json", responseSchema: ANALYSIS_RESPONSE_SCHEMA }
      };

      console.log("Sending payload to API:", JSON.stringify(payload, null, 2)); // Debug log

      const responseText = await callGeminiAPI(payload);
       // Check if callGeminiAPI returned an error string
      if (typeof responseText === 'string' && responseText.startsWith('Error:')) {
          throw new Error(responseText.substring(7)); // Throw the specific error message
      }

      console.log("Raw API response text:", responseText); // Debug log

      let rawData;
      try { rawData = JSON.parse(responseText); }
      catch (e) {
          console.error("Invalid JSON received:", responseText);
          throw new Error(`AI returned invalid JSON data. Check console.`); // More specific error
      }
      console.log("Parsed raw analysis data:", rawData); // Debug log

      const analysisData = sanitizeAnalysisData(rawData);
      console.log("Sanitized analysis data:", analysisData); // Debug log

       // Add extra validation after sanitization
      if (typeof analysisData.score !== 'number' || typeof analysisData.proScore !== 'number' || !Array.isArray(analysisData.issues) || !Array.isArray(analysisData.strengths) || !Array.isArray(analysisData.drills) ) {
           console.error("Sanitized data structure is invalid:", analysisData);
           throw new Error("Processed analysis data is invalid.");
      }


      // Save Progress
      setProgressData(prevProgress => {
         // Defensive check for structure
         if (!prevProgress || !prevProgress[selectedSkill]?.subSkills?.[selectedSubSkill]) {
             console.error("Progress data structure missing for saving:", selectedSkill, selectedSubSkill);
             return prevProgress; // Return unchanged state
         }
          const newProgress = JSON.parse(JSON.stringify(prevProgress));
          const currentScore = newProgress[selectedSkill].subSkills[selectedSubSkill].current || 0;
          if (analysisData.score > currentScore) {
            newProgress[selectedSkill].subSkills[selectedSubSkill].current = analysisData.score;
            try {
               localStorage.setItem('playSmartProgress', JSON.stringify(newProgress));
            } catch (e) { console.error("Error saving progress:", e); showModal("Error saving progress."); }
          }
          return newProgress;
      });


      // Save Drills
       setTrainingDrills(prevDrills => {
           const currentDrillsData = Array.isArray(prevDrills) ? prevDrills : []; // Ensure it's an array
           const newDrills = analysisData.drills || [];
           const uniqueNewDrills = newDrills.filter(nd => nd && nd.drill && !currentDrillsData.some(ed => ed && ed.drill === nd.drill));
           const updatedDrills = [...currentDrillsData, ...uniqueNewDrills];
           try {
               localStorage.setItem('playSmartTrainingDrills', JSON.stringify(updatedDrills));
           } catch (e) { console.error("Error saving drills:", e); showModal("Error saving drills."); }
           return updatedDrills;
       });


      setCurrentAnalysis(analysisData);
      setAnalysisComplete(true);
      setActiveTab('analysis');

    } catch (error) {
      console.error('Analysis failed:', error);
      setModalMessage(`Analysis Failed: ${error.message}.`); // Show specific error
      setAnalysisComplete(false);
      setCurrentAnalysis(null);
    } finally {
      setAnalyzing(false);
    }
  };


  // Helper boolean to check if all frames are ready (Memoized for performance)
  const allKeyframesCaptured = React.useMemo(() => {
    if (!selectedSkill) return false;
    const requiredFramesCount = (keyframeLabelSets[selectedSkill] || []).length;
    if (requiredFramesCount === 0) return false;
    for (let i = 1; i <= requiredFramesCount; i++) {
        if (!keyframes[`frame${i}`]) return false;
    }
    return true;
  }, [keyframes, selectedSkill]);


  // Helper function to get the right color for progress bars
  const getBarColor = (skillKey) => {
    const colorMap = { shooting: 'bg-red-500', passing: 'bg-blue-500', defending: 'bg-green-500', positioning: 'bg-purple-500', };
    return colorMap[skillKey] || 'bg-gray-500';
  };

  // --- RENDER FUNCTION (JSX) ---
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white font-sans"> {/* Added font */}
      {/* Modal for all notifications */}
      <Modal message={modalMessage} onClose={() => setModalMessage('')} />
      {/* Hidden Canvas for Screenshots */}
      <canvas ref={canvasRef} className="hidden"></canvas>

      <div className="max-w-7xl mx-auto p-4 md:p-6">
        {/* Header */}
        <header className="text-center mb-6 md:mb-8"> {/* Increased margin */}
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg"> {/* Added shadow */}
              <Zap className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">PlaySmart</h1> {/* Adjusted size/tracking */}
          </div>
          <p className="text-gray-400 text-sm md:text-base">AI-Powered Football Training Platform</p> {/* Adjusted size */}
        </header>

        {/* TABS Navigation */}
        <nav className="flex flex-wrap gap-2 mb-6 md:mb-8 bg-slate-800/60 p-2 rounded-xl backdrop-blur-sm shadow-md"> {/* Added blur/shadow */}
          {[
            { id: 'upload', icon: Upload, label: 'Upload & Analyze' }, // Renamed
            { id: 'analysis', icon: BarChart3, label: 'Analysis Results' }, // Renamed
            { id: 'progress', icon: TrendingUp, label: 'Progress' },
            { id: 'schedule', icon: Calendar, label: 'Schedule' },
            { id: 'coach', icon: MessageCircle, label: 'AI Coach' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={(tab.id === 'analysis' && (!analysisComplete || analyzing)) || (tab.id !== 'upload' && analyzing)} // Prevent tab switching during analysis
              className={`flex-1 min-w-[100px] py-2.5 px-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 text-xs sm:text-sm shadow-sm ${ // Adjusted padding/size
                activeTab === tab.id
                 ? 'bg-blue-600 text-white ring-2 ring-blue-400 ring-offset-2 ring-offset-slate-900' // Added ring effect
                 : 'text-gray-300 hover:text-white hover:bg-slate-700/50' // Improved hover
              } ${((tab.id === 'analysis' && !analysisComplete) || analyzing) ? 'opacity-50 cursor-not-allowed' : ''}`} // Consistent disabled style
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>

        {/* --- Main Content Area --- */}
        <main>
            {/* --- TAB CONTENT: "UPLOAD" --- */}
            {activeTab === 'upload' && (
              <section className="space-y-6"> {/* Increased spacing */}
                {/* Main Card */}
                <div className="bg-slate-800/60 rounded-xl p-5 md:p-8 border border-slate-700 shadow-xl backdrop-blur-sm"> {/* Increased padding/shadow */}
                  <h2 className="text-xl md:text-2xl font-bold text-white mb-6">Video Analysis Pipeline</h2> {/* Increased size/margin */}

                  {/* Step 1: Select Category */}
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">1</span> Select Category</h3> {/* Styled step number */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3"> {/* Increased gap */}
                      {Object.entries(skills).map(([key, skill]) => (
                        <button
                          key={key}
                          onClick={() => setSelectedSkill(key)}
                          // Visual feedback on selection
                          className={`p-4 rounded-lg border-2 transition-all duration-200 transform hover:scale-105 ${
                            selectedSkill === key
                             ? 'border-blue-500 bg-blue-500/20 shadow-md'
                             : 'border-slate-600 bg-slate-700/40 hover:border-slate-500'
                          }`}
                        >
                          <skill.icon className={`w-7 h-7 mx-auto mb-2 ${selectedSkill === key ? 'text-blue-400' : 'text-gray-400'}`} /> {/* Increased size/margin */}
                          <p className={`text-sm font-medium ${selectedSkill === key ? 'text-white' : 'text-gray-300'}`}>{skill.name}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Step 2: Select Sub-Skill (Conditional Render) */}
                  {selectedSkill && (
                    <div className="border-t border-slate-700 pt-6 mt-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">2</span> Select Skill to Analyze</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2"> {/* Responsive grid */}
                        {(skills[selectedSkill]?.subSkills || []).map(sub => ( // Added fallback for safety
                          <button
                            key={sub}
                            onClick={() => setSelectedSubSkill(sub)}
                            className={`p-2.5 rounded-md text-xs sm:text-sm transition-colors duration-150 ${ // Adjusted padding/size
                              selectedSubSkill === sub
                               ? 'bg-blue-600 text-white font-semibold shadow'
                               : 'bg-slate-600/50 text-gray-300 hover:bg-slate-500/50'
                            }`}
                          >
                            {subSkillNames[sub] || sub}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Step 3: Upload Video (Conditional Render) */}
                  {selectedSkill && selectedSubSkill && !uploadedVideo && (
                    <div className="border-t border-slate-700 pt-6 mt-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">3</span> Upload Your Video</h3>
                      <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept="video/*" className="hidden" />
                      <div onClick={() => fileInputRef.current?.click()} className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 transition-colors duration-200 bg-slate-700/20">
                        <Video className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                        <p className="text-base md:text-lg text-gray-300">Click to upload video (MP4, MOV)</p> {/* Adjusted size */}
                        <p className="text-xs text-gray-500 mt-1">(Max 100MB)</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Step 4 & 5: Capture & Analyze (Conditional Render) */}
                  {selectedSkill && selectedSubSkill && uploadedVideo && (
                    <div className="border-t border-slate-700 pt-6 mt-6 space-y-6">
                      {/* Video Player */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                            <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">4</span> Capture Keyframes: <span className="text-blue-400 font-medium">{subSkillNames[selectedSubSkill] || selectedSubSkill}</span>
                        </h3>
                        <div className="relative rounded-lg overflow-hidden shadow-lg border border-slate-700"> {/* Added styling */}
                             <video
                              ref={videoRef}
                              src={URL.createObjectURL(uploadedVideo)}
                              controls
                              className="w-full max-h-72 object-contain bg-black" // Increased max-height
                              onLoadedMetadata={(e) => {
                                console.log("Video metadata loaded");
                                // Ensure canvas size matches video on load
                                if (canvasRef.current && videoRef.current) {
                                    canvasRef.current.width = videoRef.current.videoWidth;
                                    canvasRef.current.height = videoRef.current.videoHeight;
                                }
                              }}
                              onError={(e) => {
                                  console.error("Video loading error:", e);
                                  setModalMessage("Error loading video. Please try a different file.");
                                  setUploadedVideo(null); // Reset video state
                              }}
                            />
                        </div>

                      </div>

                      {/* Keyframe Capture Area */}
                      <div>
                        <p className="text-sm text-gray-400 mb-4">Play/pause your video at the right moments and click the buttons below to capture the {keyframeLabels.length} keyframes.</p>

                        <div className={`grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4`} key={selectedSkill}> {/* Increased gap */}
                          {(keyframeLabels || []).map((label, index) => { // Added fallback
                            const frameKey = `frame${index + 1}`;
                            return (
                                <div className="text-center" key={frameKey}>
                                  {/* Preview Box */}
                                  <div className={`w-full aspect-video bg-slate-700 rounded-lg mb-2 flex items-center justify-center overflow-hidden border-2 ${keyframes[frameKey] ? 'border-green-500' : 'border-slate-600'}`}> {/* Border indication */}
                                    {keyframes[frameKey] ? (
                                      <img src={keyframes[frameKey]} alt={label} className="w-full h-full object-cover" />
                                    ) : (
                                      <ImageIcon className="w-6 h-6 sm:w-8 sm:h-8 text-gray-500" />
                                    )}
                                  </div>
                                  {/* Capture Button */}
                                  <button
                                    onClick={() => handleCaptureFrame(frameKey)}
                                    className="w-full text-xs bg-slate-600 hover:bg-slate-500 text-white py-2 px-2 rounded-lg transition-colors duration-150 shadow-sm"
                                  >
                                    {label}
                                  </button>
                                </div>
                              );
                          })}
                        </div>
                      </div>

                      {/* Step 5: Analyze Button */}
                      <div className="pt-4">
                       <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2"><span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">5</span> Analyze</h3>
                        {analyzing ? (
                          <div className="bg-blue-600/80 text-white py-3 px-4 rounded-xl text-center flex items-center justify-center gap-2 shadow"> {/* Adjusted style */}
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Analyzing {subSkillNames[selectedSubSkill] || selectedSubSkill}... Please wait.
                          </div>
                        ) : (
                          <button
                            onClick={handleRealAnalysis}
                            disabled={!allKeyframesCaptured}
                            className={`w-full text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all duration-200 transform hover:scale-105 shadow-lg ${ // Added effects
                              !allKeyframesCaptured
                                ? 'bg-gray-600 cursor-not-allowed opacity-70' // Clearer disabled state
                                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700' // Gradient
                            }`}
                          >
                            <Play className="w-5 h-5" />
                            {!allKeyframesCaptured ? `Capture all ${keyframeLabels.length} frames` : `Analyze ${subSkillNames[selectedSubSkill] || selectedSubSkill}`}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* --- TAB CONTENT: "ANALYSIS" --- */}
            {activeTab === 'analysis' && ( // Simplified conditional rendering
                <section className="space-y-6">
                    {/* Show only if analysis is complete and data exists */}
                    {analysisComplete && currentAnalysis ? (
                        <>
                            {/* Score Card */}
                            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700 shadow-xl backdrop-blur-sm">
                              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                                <div>
                                  <h2 className="text-2xl md:text-3xl font-bold text-white">{subSkillNames[selectedSubSkill] || selectedSubSkill}</h2>
                                  <p className="text-gray-400 text-sm">Analysis vs Professional Benchmark</p>
                                </div>
                                <div className="text-left sm:text-right mt-2 sm:mt-0">
                                  <div className="text-4xl font-bold text-blue-400">{currentAnalysis.score} <span className="text-2xl text-gray-400">/ 100</span></div>
                                  <div className="text-xs text-green-400 mt-1">Pro Benchmark: {currentAnalysis.proScore}</div>
                                </div>
                              </div>
                              {/* Progress Bar */}
                              <div className="w-full bg-slate-700 rounded-full h-3 relative overflow-hidden">
                                 {/* Background benchmark line */}
                                 <div className="absolute top-0 left-0 h-full bg-green-500/30 rounded-full" style={{ width: `${currentAnalysis.proScore > 0 ? (currentAnalysis.proScore / 100) * 100 : 0}%` }}></div>
                                 {/* Actual score bar */}
                                <div className="absolute top-0 left-0 bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-500 ease-out" style={{ width: `${currentAnalysis.score > 0 ? (currentAnalysis.score / 100) * 100 : 0}%` }}></div> {/* Use 100 as max */}
                              </div>
                              {/* Gap Text */}
                               {typeof currentAnalysis.score === 'number' && typeof currentAnalysis.proScore === 'number' && currentAnalysis.score < currentAnalysis.proScore && (
                                   <div className="text-center text-sm mt-3 text-orange-400">Improvement Gap: {Math.max(0, currentAnalysis.proScore - currentAnalysis.score)} points to Pro</div>
                               )}
                                {typeof currentAnalysis.score === 'number' && typeof currentAnalysis.proScore === 'number' && currentAnalysis.score >= currentAnalysis.proScore && (
                                   <div className="text-center text-sm mt-3 text-green-400">Excellent! You've met or exceeded the Pro benchmark.</div>
                               )}
                            </div>

                            {/* Issues Detected Card */}
                            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700 shadow-xl backdrop-blur-sm">
                              <h3 className="text-xl font-bold text-white mb-4">Areas for Improvement</h3>
                              <div className="space-y-3">
                                {currentAnalysis.issues.length === 0 ? (
                                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                                    <p className="text-white text-sm font-medium">No major issues detected by the AI. Great technique!</p>
                                  </div>
                                ) : (
                                  currentAnalysis.issues.map((item, idx) => (
                                    <div key={`issue-${idx}`} className={`p-4 rounded-lg border-l-4 ${item.severity === 'high' ? 'bg-red-500/10 border-red-500' : (item.severity === 'medium' ? 'bg-orange-500/10 border-orange-500' : 'bg-yellow-500/10 border-yellow-500')}`}>
                                      <p className="text-white text-sm font-semibold mb-1">{item.issue || 'N/A'}</p>
                                      <p className="text-green-400 text-xs flex items-center gap-1"> <CheckCircle className="w-3 h-3 inline-block"/> Fix: {item.fix || 'N/A'}</p>
                                    </div>
                                  ))
                                )}
                              </div>
                            </div>

                            {/* Strengths Card */}
                            <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700 shadow-xl backdrop-blur-sm">
                              <h3 className="text-xl font-bold text-white mb-4">Key Strengths</h3>
                              <div className="flex flex-wrap gap-3">
                                {currentAnalysis.strengths.length === 0 ? (
                                  <p className="text-gray-400 text-sm italic">Focus on addressing the areas for improvement.</p>
                                ) : (
                                  currentAnalysis.strengths.map((s, i) => (
                                    <span key={`strength-${i}`} className="bg-green-500/15 border border-green-500/40 rounded-full px-4 py-1.5 text-green-300 text-sm font-medium shadow-sm">{s}</span> // Pill style
                                  ))
                                )}
                              </div>
                            </div>

                            {/* Training Plan Card */}
                            <div className="bg-gradient-to-br from-blue-700/20 to-indigo-700/20 rounded-xl p-6 border border-blue-500/40 shadow-xl backdrop-blur-sm">
                              <h3 className="text-xl font-bold text-white mb-4">Recommended Drills (Added to Drill Bank)</h3>
                              {currentAnalysis.drills.length === 0 ? (
                                 <p className="text-gray-300 text-sm italic">No specific drills recommended for now. Focus on the suggested corrections.</p>
                              ) : (
                                <ul className="space-y-3"> {/* Use list for semantics */}
                                  {currentAnalysis.drills.map((drill, idx) => (
                                    <li key={`drill-${idx}`} className="bg-slate-800/70 rounded-lg p-3 flex items-center justify-between shadow">
                                      <div className="flex items-center gap-3">
                                        <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-xs font-bold">{idx + 1}</div>
                                        <p className="text-gray-200 text-sm">{drill.drill || 'N/A'}</p>
                                      </div>
                                      <span className="text-blue-300 text-sm font-medium bg-slate-700 px-2 py-0.5 rounded">{drill.duration || '?'} min</span>
                                    </li>
                                  ))}
                                  </ul>
                              )}
                            </div>
                        </>
                    ) : (
                         // Message when analysis hasn't been run or data is missing
                        <div className="text-center py-12 px-6 bg-slate-800/60 rounded-xl border border-slate-700 shadow-xl backdrop-blur-sm">
                            <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-white mb-2">Analysis Results Appear Here</h3>
                            <p className="text-gray-400">
                                {analyzing
                                 ? "Analysis is currently in progress..."
                                 : "Go to the 'Upload & Analyze' tab, select a skill, upload a video, capture the keyframes, and click 'Analyze' to see your results."}
                             </p>
                        </div>
                    )}
                </section>
            )}


            {/* --- TAB CONTENT: "PROGRESS" --- */}
            {activeTab === 'progress' && (
              <section className="space-y-6">
                <div className="bg-slate-800/60 rounded-xl p-6 md:p-8 border border-slate-700 shadow-xl backdrop-blur-sm">
                  <h2 className="text-xl md:text-2xl font-bold text-white mb-6">Your Skill Progress Tracker</h2>

                  {Object.keys(skills).map((skillKey) => {
                    const skill = skills[skillKey];
                    // Check if progressData for this skill exists
                    const skillProgress = progressData[skillKey];
                     if (!skillProgress || !skillProgress.subSkills) return null; // Skip rendering if data is missing


                    return (
                      <div key={skillKey} className="mb-8 last:mb-0"> {/* Add margin bottom */}
                        {/* Category Header */}
                        <div className="flex items-center gap-3 mb-4 pb-2 border-b border-slate-600">
                          <skill.icon className={`w-6 h-6 text-${skill.color}-400`} />
                          <h3 className={`text-lg font-semibold text-white`}>{skill.name}</h3>
                        </div>

                        {/* Sub-skill bars */}
                        <div className="space-y-4">
                          {skill.subSkills.map((subSkillKey) => {
                             // Check if subSkillData exists
                            const subSkillData = skillProgress.subSkills[subSkillKey];
                            if (!subSkillData) return null; // Skip if missing

                            const subSkillName = subSkillNames[subSkillKey] || subSkillKey;
                            const score = subSkillData.current || 0; // Default to 0
                            const target = subSkillData.target || 100; // Default to 100
                             // Prevent division by zero
                            const percentage = target > 0 ? (score / target) * 100 : 0;

                            return (
                              <div key={subSkillKey} className="pl-2"> {/* Reduced padding */}
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-sm text-gray-300">{subSkillName}</span>
                                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${score > 0 ? 'bg-slate-600 text-white' : 'bg-slate-700 text-gray-400'}`}>
                                    {score} / {target}
                                  </span>
                                </div>
                                {/* Progress bar with transition */}
                                <div className="bg-slate-700 rounded-full h-2.5 overflow-hidden">
                                  <div
                                    className={`${getBarColor(skillKey)} h-2.5 rounded-full transition-all duration-700 ease-out`} // Longer transition
                                    // Ensure percentage is within bounds
                                    style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }}
                                  ></div>
                                </div>
                              </div>
                            );
                          })}
                           {/* Add message if no subskills have progress */}
                           {skill.subSkills.every(sub => !skillProgress.subSkills[sub] || skillProgress.subSkills[sub].current === 0) && (
                               <p className="text-sm text-gray-500 italic pl-2">No progress recorded for {skill.name} skills yet.</p>
                           )}
                        </div>
                      </div>
                    );
                  })}
                   {/* Add message if no progress overall */}
                   {Object.keys(progressData).length === 0 || Object.values(progressData).every(cat => Object.values(cat.subSkills).every(sub => sub.current === 0)) && (
                       <div className="text-center py-8 text-gray-500">
                           <TrendingUp className="w-12 h-12 mx-auto mb-3" />
                           <p>Your progress will appear here after you analyze some skills.</p>
                       </div>
                   )}
                </div>
              </section>
            )}

            {/* --- TAB CONTENT: "SCHEDULE" --- */}
            {activeTab === 'schedule' && (
              <section className="space-y-6">
                {/* Controls Card */}
                <div className="bg-slate-800/60 rounded-xl p-6 md:p-8 border border-slate-700 shadow-xl backdrop-blur-sm">
                  <h2 className="text-xl md:text-2xl font-bold text-white mb-6">Training Schedule Generator</h2>
                  <div className="mb-6">
                    <label htmlFor="hoursRange" className="text-gray-300 mb-2 block font-medium">Available Training Hours Per Week: <span className="text-blue-400 font-bold">{hoursPerWeek}h</span></label>
                    <input
                      id="hoursRange" // Corrected ID
                      type="range"
                      min="1" // Start from 1 hour
                      max="20" // Increased max
                      step="1" // Increment by 1
                      value={hoursPerWeek}
                      onChange={(e) => setHoursPerWeek(parseInt(e.target.value))}
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500" // Styled range input
                    />
                  </div>
                  <button
                    onClick={generateDynamicSchedule}
                    disabled={trainingDrills.length === 0} // Disable if no drills
                    className={`w-full text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all duration-200 transform hover:scale-105 shadow-lg ${
                        trainingDrills.length === 0
                        ? 'bg-gray-600 cursor-not-allowed opacity-70'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                    }`}
                  >
                     <Calendar className="w-5 h-5"/>
                    {trainingDrills.length === 0 ? 'Analyze Skills to Generate' : 'Generate My Weekly Schedule'}
                  </button>
                </div>

                {/* Generated Plan Card (Conditional Render) */}
                {weeklySchedule.length > 0 && (
                  <div className="bg-slate-800/60 rounded-xl p-6 md:p-8 border border-slate-700 shadow-xl backdrop-blur-sm">
                    <h3 className="text-xl font-bold text-white mb-5">Your Generated Weekly Plan</h3>
                    <div className="space-y-4">
                      {weeklySchedule.map((session, idx) => (
                        <div key={`session-${idx}`} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 shadow-sm">
                          <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-600">
                            <div className="text-white font-semibold text-lg">{session.day}</div>
                            <div className="text-blue-300 bg-slate-700 px-2.5 py-1 rounded-full text-xs font-medium">{session.duration} min Session</div>
                          </div>
                          {session.drills.length > 0 ? (
                              <ul className="space-y-2">
                                {session.drills.map((drill, i) => (
                                  <li key={`session-${idx}-drill-${i}`} className="text-gray-300 text-sm flex items-center gap-2">
                                     <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0"/>
                                     <span>{drill.drill || 'N/A'} <span className="text-gray-500">({drill.duration || '?'} min)</span></span>
                                  </li>
                                ))}
                              </ul>
                          ) : (
                              <p className="text-sm text-gray-500 italic">Rest day or session too short for assigned drills.</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Drill Bank Card */}
                <div className="bg-slate-800/60 rounded-xl p-6 md:p-8 border border-slate-700 shadow-xl backdrop-blur-sm">
                  <h3 className="text-xl font-bold text-white mb-4">Your AI Drill Bank</h3>
                  <div className="space-y-2 max-h-60 overflow-y-auto pr-2 border border-slate-700 rounded-lg p-3 bg-slate-900/30 custom-scrollbar"> {/* Added styles */}
                    {trainingDrills.length === 0 ? (
                      <p className="text-gray-500 text-sm text-center py-4">Your Drill Bank is empty. Analyze a skill to add drills recommended by the AI.</p>
                    ) : (
                      trainingDrills.map((drill, idx) => (
                         // Added validation
                        drill && drill.drill && drill.duration ? (
                            <div key={`bank-drill-${idx}`} className="bg-slate-700/50 hover:bg-slate-600/50 rounded-lg p-3 flex justify-between items-center transition-colors duration-150">
                              <p className="text-gray-200 text-sm mr-2">{drill.drill}</p>
                              <span className="text-blue-300 text-sm font-medium flex-shrink-0 bg-slate-600 px-2 py-0.5 rounded">{drill.duration} min</span>
                            </div>
                        ) : null
                      ))
                    )}
                  </div>
                </div>
              </section>
            )}

            {/* --- TAB CONTENT: "AI COACH" --- */}
            {activeTab === 'coach' && (
              <section className="space-y-6">
                <div className="bg-slate-800/60 rounded-xl border border-slate-700 shadow-xl backdrop-blur-sm h-[70vh] flex flex-col overflow-hidden"> {/* Adjusted height */}
                  {/* Coach Header */}
                  <header className="flex items-center gap-3 p-4 border-b border-slate-700 flex-shrink-0">
                    <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center shadow">
                      <MessageCircle className="w-5 h-5 md:w-6 md:h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-lg md:text-xl font-bold text-white">AI Football Coach</h2>
                      <p className="text-gray-400 text-xs md:text-sm">Ask anything about techniques & training</p>
                    </div>
                  </header>

                  {/* Chat Window */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar"> {/* Added scrollbar style */}
                    {chatMessages.length === 0 ? (
                      // Empty state
                      <div className="text-center pt-12 pb-8">
                        <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4 opacity-50" />
                        <p className="text-gray-400 mb-5 text-sm">Ask me how to improve...</p>
                        <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
                          {['Power shots', 'Finesse technique', 'Defending', 'Passing', 'Weak foot', 'Fitness'].map((topic, i) => (
                            <button
                              key={i}
                              onClick={() => {
                                  const question = `How to improve ${topic.toLowerCase()}?`;
                                  setUserMessage(question); // Set the input field
                                  // Send message after a tiny delay to allow input field to update visually
                                  setTimeout(() => handleSendMessage(), 50);
                              }}
                              className="bg-slate-700 hover:bg-slate-600 text-gray-300 text-xs sm:text-sm py-2.5 px-3 rounded-lg transition-colors duration-150 shadow-sm"
                            >
                              {topic}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      // Chat history
                      <>
                        {chatMessages.map((msg, idx) => (
                          <div key={`chat-${idx}`} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] sm:max-w-[75%] p-3 rounded-lg shadow-md ${msg.type === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-700 text-gray-200 rounded-bl-none'}`}> {/* Bubble style */}
                              {/* Render newlines correctly */}
                              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                            </div>
                          </div>
                        ))}
                        {/* Typing indicator */}
                        {isAiTyping && (
                          <div className="flex justify-start">
                             <div className="bg-slate-700 text-gray-200 p-3 rounded-lg inline-flex items-center space-x-1.5 shadow-md rounded-bl-none"> {/* Bubble style + spacing */}
                              <div className="w-1.5 h-1.5 bg-blue-400 rounded-full bounce1"></div>
                              <div className="w-1.5 h-1.5 bg-blue-400 rounded-full bounce2"></div>
                              <div className="w-1.5 h-1.5 bg-blue-400 rounded-full bounce3"></div>
                            </div>
                          </div>
                        )}
                        {/* Scroll anchor */}
                        <div ref={chatEndRef} />
                      </>
                    )}
                  </div>

                  {/* Chat Input */}
                  <footer className="flex gap-2 p-4 border-t border-slate-700 flex-shrink-0 bg-slate-800/50">
                    <input
                      type="text"
                      value={userMessage}
                      onChange={(e) => setUserMessage(e.target.value)} // Corrected e.taget -> e.target
                      onKeyPress={handleKeyPress}
                      placeholder="Ask the AI coach..."
                       // Improved styling
                      className="flex-1 bg-slate-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400 text-sm shadow-inner"
                    />
                     {/* Improved styling and disabled state */}
                    <button
                      onClick={handleSendMessage}
                      disabled={isAiTyping || userMessage.trim() === ''}
                      className={`bg-blue-600 text-white px-4 sm:px-5 py-3 rounded-lg transition-colors duration-200 flex items-center justify-center shadow-md ${isAiTyping || userMessage.trim() === '' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
                    >
                      <Send className="w-4 h-4 sm:w-5 sm:h-5" /> {/* Adjusted size */}
                    </button>
                  </footer>
                </div>
              </section>
            )}
        </main>

      </div>
    </div>
  );
};

export default PlaySmart;

