# PlaySmart AI Football Coach

This repository contains the source code for **PlaySmart AI Football Coach**, a **multimodal web application** built with **React** and **Tailwind CSS**.  
The app analyzes user-uploaded video keyframes to provide **expert biomechanical feedback**, **track skill progression**, and **generate personalized weekly training schedules** — all powered by the **Gemini API**.

---

## Key Features

### Multimodal Analysis
Upload a football training video and capture **3–5 keyframes** of a specific action (e.g., Shooting, Passing, Defending).  
These images are processed sequentially by the AI for detailed biomechanical analysis.

### Harsh Critique AI
The **Gemini API** acts as a **world-class, harsh football coach**, providing:
- A **score (0–100)** for each skill execution  
- Precise feedback on technical issues (e.g., _“Plant foot 5cm too far”_)  
- Specific correction advice

### Personalized Training
Detected issues are automatically mapped to **recommended drills** (e.g., “Drill 1 – 15 mins”)  
All drills are stored locally in a persistent **Drill Bank**.

### Dynamic Scheduling
The **Schedule Tab** generates a **weekly training plan** based on:
- The user’s available hours  
- The AI-identified weak points and related drills  

### progress Tracking
Scores for each sub-skill (e.g., *Power Shot*, *Finesse*) are saved locally, allowing players to **track progress** over time.

### AI Coach Chat
A built-in **AI Chat Coach** (Gemini API powered) answers natural language queries about:
- Training drills  
- Football rules  
- Technical improvements  

---

### Technical Stack

| Component | Technology |
|------------|-------------|
| **Frontend** | React (Functional Components + Hooks) |
| **Styling** | Tailwind CSS |
| **Bundler** | Vite |
| **AI Backend** | Google Gemini API *(gemini-2.5-flash-preview-09-2025)* |
| **Function** | Multimodal (Vision + Text) generation using structured JSON output |

---

### How It Works
1. Upload a video and select 3–5 keyframes of a football skill.  
2. The Gemini AI performs **sequential biomechanical analysis**.  
3. The system provides **scores**, **error detection**, and **drill recommendations**.  
4. Training schedules are **auto-generated** weekly based on user time input.  
5. Performance scores are **stored locally** for visual progress tracking.

---
### Implementation
1. Locate to the directory.
2. Run the command "npm run dev".
3. Open "localost:5173" in the browser


