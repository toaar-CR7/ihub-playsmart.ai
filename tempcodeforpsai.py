import React, { useState, useRef } from 'react';
import { Upload, Video, TrendingUp, Target, Shield, Users, Play, CheckCircle, AlertCircle, Camera, BarChart3, Award, Calendar, Brain, Clock, Zap, Move } from 'lucide-react';

const PlaySmart = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState('shooting');
  const [selectedSubSkill, setSelectedSubSkill] = useState('power_shot');
  const [hoursPerWeek, setHoursPerWeek] = useState(5);
  const fileInputRef = useRef(null);

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
      { time: '23:45', situation: 'One-on-one with defender', action: 'Hesitated on dribble choice' },
      { time: '67:12', situation: 'Penalty box positioning', action: 'Lost marker awareness' }
    ],
    confusedPoints: [
      { time: '34:21', situation: 'Team transition', action: 'Unsure whether to press or drop' },
      { time: '56:43', situation: 'Overlap vs stay wide', action: 'Delayed movement decision' }
    ],
    positioningErrors: [
      { time: '15:20', error: 'Too narrow - lost width', correction: 'Stay wider to stretch defense' },
      { time: '45:10', error: 'Ball-watching during attack', correction: 'Scan and move into space' },
      { time: '72:30', error: 'Too high in transition', correction: 'Drop deeper for defensive balance' }
    ]
  };

  const generateSchedule = (hours) => {
    const sessionsPerWeek = Math.floor(hours / 1.5);
    const drills = {
      shooting: ['Power shot practice (15 mins)', 'Finesse technique (10 mins)', 'Volley training (10 mins)'],
      passing: ['Ground pass accuracy (10 mins)', 'Lob pass control (10 mins)', 'Through ball timing (10 mins)'],
      defending: ['Jockeying drills (15 mins)', 'Positioning work (10 mins)', 'Recovery runs (10 mins)'],
      positioning: ['Off-ball movement (15 mins)', 'Scanning practice (10 mins)', 'Transition work (10 mins)']
    };
    
    return Array.from({ length: sessionsPerWeek }, (_, i) => ({
      day: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i % 7],
      focus: Object.keys(skills)[i % 4],
      drills: drills[Object.keys(skills)[i % 4]],
      duration: 90
    }));
  };

  const schedule = generateSchedule(hoursPerWeek);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedVideo(URL.createObjectURL(file));
      setAnalysisComplete(false);
    }
  };

  const getAnalysisData = () => {
    const analyses = {
      // SHOOTING SUB-SKILLS
      power_shot: {
        score: 58,
        proScore: 92,
        issues: [
          { severity: 'high', issue: 'Plant foot 18cm too far from ball (Pro avg: 11cm)', fix: 'Position 10-12cm beside ball, toes pointing at target' },
          { severity: 'high', issue: 'Body leaning backward 12° at contact (Pro: 5° forward)', fix: 'Keep chest over ball, head down' },
          { severity: 'medium', issue: 'Follow-through 45cm vs Pro 85cm average', fix: 'Let leg swing fully through toward goal' },
          { severity: 'medium', issue: 'Contact point inconsistent - 60% accuracy (Pro: 95%)', fix: 'Focus on laces contact every time' }
        ],
        strengths: ['Ankle remains locked during strike (matches pro level)', 'Approach angle consistent at 30-35° (optimal range)', 'Non-kicking foot lands at same time as ball contact (good timing)'],
        drills: ['Plant foot placement drill - 20 reps', 'Body balance over ball - 15 mins', 'Full follow-through practice - 10 shots']
      },
      finesse: {
        score: 51,
        proScore: 88,
        issues: [
          { severity: 'high', issue: 'Ankle opening only 22° vs Pro standard 40-50°', fix: 'Open ankle wider, use inside of foot' },
          { severity: 'high', issue: 'Contact point too low - hitting bottom third vs center', fix: 'Strike ball at center or slightly above center' },
          { severity: 'high', issue: 'Body curve minimal - 8° rotation vs Pro 25-30°', fix: 'Rotate hips and shoulders through the shot' },
          { severity: 'medium', issue: 'Follow-through stops at 30cm (Pro: 60cm+)', fix: 'Follow through with leg wrapping across your body' }
        ],
        strengths: ['Body shape opens correctly before strike', 'Head stays down throughout motion', 'Plant foot positioning 12cm from ball (ideal range)'],
        drills: ['Inside foot technique - 25 reps', 'Ball contact point drill', 'Curl practice around obstacles - 15 mins']
      },
      chip: {
        score: 43,
        proScore: 85,
        issues: [
          { severity: 'high', issue: 'Toe angle only 35° down vs Pro 55-65°', fix: 'Point toe down sharply, use underneath of foot' },
          { severity: 'high', issue: 'Body weight forward - wrong for chips (Pro leans back 10°)', fix: 'Lean slightly back to get under the ball' },
          { severity: 'high', issue: 'Backswing 60cm vs Pro 20-30cm for chips', fix: 'Short, sharp contact - less backswing' },
          { severity: 'medium', issue: 'Contact duration 0.18s vs Pro 0.08s (too long)', fix: 'Quick stab under ball, not a push' }
        ],
        strengths: ['Good decision making on when to chip', 'Eyes track ball well until contact'],
        drills: ['Toe-down technique - 20 reps', 'Short backswing practice', 'Chip over goalkeeper drill - 10 mins']
      },
      volley: {
        score: 39,
        proScore: 82,
        issues: [
          { severity: 'high', issue: 'Eyes lose ball tracking 0.3s before contact (Pro: watch until contact)', fix: 'Watch ball onto your foot completely' },
          { severity: 'high', issue: 'Single-leg balance time only 0.8s vs Pro 2s+', fix: 'Strengthen core, practice balance drills' },
          { severity: 'high', issue: 'Arms down at sides vs Pro arms spread wide', fix: 'Spread arms wide like wings for stability' },
          { severity: 'medium', issue: 'Striking foot speed 8m/s vs Pro 12-15m/s', fix: 'Generate more leg whip through contact' }
        ],
        strengths: ['Attempts to get body behind ball', 'Willing to attack difficult balls'],
        drills: ['Ball tracking exercise - 15 mins', 'Single-leg balance training', 'Volley practice with service - 20 reps']
      },
      bicycle: {
        score: 28,
        proScore: 75,
        issues: [
          { severity: 'high', issue: 'Backward arch only 25° vs Pro 45-50° minimum', fix: 'Arch back more, trust the fall' },
          { severity: 'high', issue: 'Kick initiated 0.4s early - ball not overhead yet', fix: 'Wait for ball to be directly above your head' },
          { severity: 'high', issue: 'Landing on side/hip (unsafe) vs Pro back/shoulder landing', fix: 'Land on back/shoulders, not neck - use crash mat' },
          { severity: 'high', issue: 'Core tension weak - visible wobble in air', fix: 'Engage core throughout entire motion' }
        ],
        strengths: ['Shows courage to attempt technique', 'Jump height adequate at 45cm'],
        drills: ['Backward fall practice on mat - 10 reps', 'Timing drill with suspended ball', 'Safe landing technique - crucial!']
      },
      penalty: {
        score: 72,
        proScore: 94,
        issues: [
          { severity: 'medium', issue: 'Eyes glance at target 0.5s before kick (Pro: eyes on ball)', fix: 'Look at ball, decide direction earlier' },
          { severity: 'medium', issue: 'Run-up 7 steps vs Pro optimal 3-4 steps', fix: 'Shorter run-up = more control and accuracy' },
          { severity: 'low', issue: 'Ball placement variance 8cm between penalties', fix: 'Consistent ball placement ritual' }
        ],
        strengths: ['Excellent composure under pressure', 'Shot placement 85% in corners (Pro: 88%)', 'Consistent power at 75-80 km/h', 'Strike technique fundamentally sound'],
        drills: ['Deception practice - eyes neutral', 'Short run-up accuracy - 15 penalties', 'Pressure simulation']
      },
      trivela: {
        score: 35,
        proScore: 80,
        issues: [
          { severity: 'high', issue: 'Outside foot wrap only 15° vs Pro 35-45°', fix: 'Wrap outside of foot around ball more' },
          { severity: 'high', issue: 'Body facing 20° wrong direction (Pro faces away from target)', fix: 'Body should face opposite of target initially' },
          { severity: 'high', issue: 'Ankle flexes during contact vs Pro locked position', fix: 'Lock ankle firm, use outside edge of foot' },
          { severity: 'medium', issue: 'Ball spin only 4 rps vs Pro 7-9 rps', fix: 'More aggressive foot wrap for spin' }
        ],
        strengths: ['Understands the concept and when to use it', 'Follow-through direction correct'],
        drills: ['Outside foot technique - 30 reps', 'Body positioning for trivela', 'Curve around wall drill - 20 shots']
      },

      // PASSING SUB-SKILLS
      ground_pass: {
        score: 68,
        proScore: 95,
        issues: [
          { severity: 'medium', issue: 'Pass weight varies ±15% (Pro: ±5% consistency)', fix: 'Focus on weight of pass, not power' },
          { severity: 'medium', issue: 'Plant foot angle off by 12° in 40% of passes', fix: 'Always point plant foot where you want ball to go' },
          { severity: 'low', issue: 'Contact point shifts 3cm between passes (Pro: 1cm)', fix: 'More consistent striking spot on ball' }
        ],
        strengths: ['Accuracy within 1m of target 78% of time', 'Inside-foot technique fundamentally correct', 'Good pace on passes under 15m'],
        drills: ['Pass weight control - gates drill', 'Target passing to moving player', 'One-touch accuracy - 15 mins']
      },
      lob: {
        score: 48,
        proScore: 82,
        issues: [
          { severity: 'high', issue: 'Foot angle only 25° under ball vs Pro 40-45°', fix: 'Lower your body, get foot deeper under ball' },
          { severity: 'high', issue: 'Power:Lift ratio wrong - 70:30 vs Pro 40:60', fix: 'Focus on lift first, distance second' },
          { severity: 'medium', issue: 'Contact point varies 6cm (Pro: 2cm variance)', fix: 'Hit consistent spot - bottom half of ball with laces' },
          { severity: 'medium', issue: 'Backspin only 3 rps vs Pro 6-8 rps', fix: 'Strike through and under with more speed' }
        ],
        strengths: ['Vision for lob opportunities good', 'Recognizes when to use technique'],
        drills: ['Lob technique over defender - 20 reps', 'Distance control drill', 'Lob to chest of teammate']
      },
      through_ball: {
        score: 56,
        proScore: 89,
        issues: [
          { severity: 'high', issue: 'Pass weight 25% too heavy in 60% of attempts', fix: 'Account for teammate speed, pass softer' },
          { severity: 'high', issue: 'Release timing 0.4s late (Pro releases as runner starts)', fix: 'Release ball when runner starts accelerating' },
          { severity: 'medium', issue: 'Body telegraph visible 0.6s before pass', fix: 'Use disguised body shape' },
          { severity: 'low', issue: 'Accuracy only 65% vs Pro 85%+', fix: 'More practice on weight and placement' }
        ],
        strengths: ['Vision excellent - spots runs early', 'Understands passing lanes concept', 'Attempts creative passes'],
        drills: ['Through ball timing with runner - 15 reps', 'Weight control to space', 'No-look pass practice']
      },
      cross: {
        score: 52,
        proScore: 86,
        issues: [
          { severity: 'high', issue: 'Cross height only 3m vs Pro 5-7m optimal', fix: 'Get under ball more, create higher arc' },
          { severity: 'high', issue: 'Head up only 0.3s before cross (Pro: 1-2s scanning)', fix: 'Scan and locate teammates earlier' },
          { severity: 'medium', issue: 'Plant foot 15cm from ball vs Pro 8-10cm', fix: 'Plant foot closer to ball for better control' },
          { severity: 'medium', issue: 'Target area accuracy 55% (Pro: 80%+)', fix: 'Aim for specific zones consistently' }
        ],
        strengths: ['Delivery area selection improving', 'Ball reaches penalty area 70% of time'],
        drills: ['Lofted cross technique - 20 reps', 'Scanning before crossing drill', 'Target area accuracy']
      },
      long_ball: {
        score: 44,
        proScore: 84,
        issues: [
          { severity: 'high', issue: 'Accuracy drops to 35% beyond 30m (Pro: 75%)', fix: 'Focus on technique over power at distance' },
          { severity: 'high', issue: 'Backspin minimal - only 2 rps vs Pro 8-10 rps', fix: 'Strike through bottom half cleanly with laces' },
          { severity: 'high', issue: 'Body leans back 8° vs Pro leans forward 5°', fix: 'Lean forward during strike for control' },
          { severity: 'medium', issue: 'Follow-through only 50cm vs Pro 90cm+', fix: 'Full extension through ball' }
        ],
        strengths: ['Power generation adequate at 70 km/h', 'Attempts long passes when appropriate'],
        drills: ['Long passing accuracy - 25 passes', 'Backspin technique drill', 'Target zones at distance']
      },
      one_touch: {
        score: 61,
        proScore: 91,
        issues: [
          { severity: 'high', issue: 'Decision time 0.8s vs Pro 0.3s (too slow)', fix: 'Decide next pass before receiving ball' },
          { severity: 'medium', issue: 'Body position wrong in 45% of touches', fix: 'Open body to receive, scan before ball arrives' },
          { severity: 'medium', issue: 'First touch accuracy 70% vs Pro 92%', fix: 'More reps, focus on contact quality' },
          { severity: 'low', issue: 'Sometimes rushing causes mishits', fix: 'Stay calm, controlled one-touch still accurate' }
        ],
        strengths: ['Decision making improving', 'Understands one-touch concept', 'Willing to play quick combinations'],
        drills: ['Triangle one-touch passing', 'Pressure one-touch drill', 'Quick combination play - 15 mins']
      },

      // DEFENDING SUB-SKILLS
      jockeying: {
        score: 53,
        proScore: 88,
        issues: [
          { severity: 'high', issue: 'Body angle 85° square vs Pro 45° side-on optimal', fix: 'Position at 45° angle, show them to weaker side' },
          { severity: 'high', issue: 'Stance width only 40cm vs Pro 60-70cm', fix: 'Wider stance for better balance and reaction' },
          { severity: 'high', issue: 'Distance to attacker 0.5m vs Pro 1.5-2m', fix: 'Maintain safe distance, be patient' },
          { severity: 'medium', issue: 'Weight on heels 60% of time (should be on balls of feet)', fix: 'Stay light, ready to move any direction' }
        ],
        strengths: ['Stays on feet well - doesn\'t dive in unnecessarily', 'Shows persistence in 1v1s'],
        drills: ['1v1 jockey positioning - 15 reps', 'Side-on stance practice', 'Patient defending drill']
      },
      tackling: {
        score: 47,
        proScore: 85,
        issues: [
          { severity: 'high', issue: 'Tackle timing 0.4s too early in 55% of attempts', fix: 'Wait for ball to be 30cm+ away from attacker body' },
          { severity: 'high', issue: 'Ankle flexes on contact (should be locked)', fix: 'Lock ankle firm, use inside of foot as solid surface' },
          { severity: 'high', issue: 'Body weight commitment only 60% (Pro: 100%)', fix: 'Commit fully when tackling, don\'t half-tackle' },
          { severity: 'medium', issue: 'Success rate 45% vs Pro 75%+', fix: 'Improve timing and technique' }
        ],
        strengths: ['Shows bravery to engage', 'Recovery positioning after tackle decent'],
        drills: ['Timing tackle drill - 20 reps', 'Block tackle technique', 'Recovery after failed tackle']
      },
      interception: {
        score: 62,
        proScore: 89,
        issues: [
          { severity: 'medium', issue: 'Pass reading 0.5s slower than Pro defenders', fix: 'Watch passer hips and foot, not just ball' },
          { severity: 'medium', issue: 'Ball-watching 40% of time (lose track of player)', fix: 'Track player AND ball simultaneously' },
          { severity: 'medium', issue: 'Interception success rate 58% vs Pro 78%', fix: 'Better anticipation and positioning' },
          { severity: 'low', issue: '50-50 ball commitment 65% vs Pro 90%+', fix: 'More aggressive on 50-50 balls' }
        ],
        strengths: ['Positioning sense developing well', 'Quick reactions when reading pass correctly', 'Good anticipation improving each session'],
        drills: ['Pass reading drill', 'Interception angles practice', '50-50 commitment training']
      },
      marking: {
        score: 51,
        proScore: 87,
        issues: [
          { severity: 'high', issue: 'Too tight marking - within 0.5m vs Pro 1-2m optimal', fix: 'Position between man and ball, see both' },
          { severity: 'high', issue: 'Reaction to movement 0.6s late (Pro: 0.2s)', fix: 'Stay on balls of feet, ready to move' },
          { severity: 'medium', issue: 'Allows goal-side position 35% of time', fix: 'Always stay between attacker and goal' },
          { severity: 'medium', issue: 'Loses sight of runner during transitions', fix: 'Check shoulder every 2-3 seconds' }
        ],
        strengths: ['Physical presence good when competing', 'Understanding of marking principles developing'],
        drills: ['Man-marking position drill', 'Shadow marking exercise', 'Denying goal-side runs - 15 mins']
      },
      clearance: {
        score: 59,
        proScore: 84,
        issues: [
          { severity: 'high', issue: 'Average clearance distance 18m vs Pro 30m+', fix: 'Full power, get distance first, direction second' },
          { severity: 'medium', issue: 'Clears to central areas 30% of time (dangerous)', fix: 'Clear wide or long, never central' },
          { severity: 'medium', issue: 'Technique inconsistent under pressure', fix: 'Practice clearances with pressure simulation' },
          { severity: 'low', issue: 'Contact point varies - sometimes toe, sometimes laces', fix: 'Consistent laces contact for distance' }
        ],
        strengths: ['Shows bravery under pressure', 'Decision to clear usually correct', 'Clearance success rate 82% (ball away from danger)'],
        drills: ['Clearance distance drill', 'Direction awareness practice', 'Pressure clearance simulation']
      },
      blocking: {
        score: 55,
        proScore: 86,
        issues: [
          { severity: 'high', issue: 'Body front-on 65% of blocks vs Pro side-on positioning', fix: 'Turn side-on, protect yourself and make bigger barrier' },
          { severity: 'high', issue: 'Jumps on 40% of blocks (should stay grounded)', fix: 'Stay low and grounded, react to shot direction' },
          { severity: 'medium', issue: 'Arms away from body in 35% of blocks', fix: 'Keep arms behind back or tight to body' },
          { severity: 'medium', issue: 'Block success rate 62% vs Pro 85%', fix: 'Better positioning and technique' }
        ],
        strengths: ['Brave to put body in way', 'Quick reactions to shots', 'Commitment level high'],
        drills: ['Block positioning drill', 'Shot-blocking technique', 'Staying grounded practice']
      },      // POSITIONING SUB-SKILLS
      off_ball: {
        score: 58,
        proScore: 90,
        issues: [
          { severity: 'high', issue: 'Movement timing 0.8s too early in 50% of runs', fix: 'Time runs with passer looking up, not before' },
          { severity: 'medium', issue: 'Run angles too straight - 85° vs Pro 45-60° diagonal', fix: 'Move at diagonals, not straight lines' },
          { severity: 'medium', issue: 'Static for 4-6s when teammate has ball', fix: 'Always provide passing option, constant movement' },
          { severity: 'low', issue: 'Checking away frequency low - 2 per min vs Pro 5-6', fix: 'Check to ball more often' }
        ],
        strengths: ['Instinct for space developing', 'Understands when to make runs', 'Willingness to move without ball'],
        drills: ['Third man runs practice', 'Angled movement drill', 'Creating passing angles - 15 mins']
      },
      spacing: {
        score: 54,
        proScore: 88,
        issues: [
          { severity: 'high', issue: 'Distance to teammates only 8m vs Pro 12-15m optimal', fix: 'Maintain 12-15m spacing to stretch defense' },
          { severity: 'high', issue: 'Bunching centrally in 60% of attacking phases', fix: 'Stay wide, use full width of pitch (68m)' },
          { severity: 'medium', issue: 'Doesn\'t adjust when teammate drops - creates cluster', fix: 'Move into vacated space immediately' },
          { severity: 'medium', issue: 'Width utilization only 45m vs Pro 60m+', fix: 'Push wider to create space' }
        ],
        strengths: ['Understanding shape concept improving', 'Recognizes when spacing is wrong'],
        drills: ['Spacing awareness drill with cones', 'Rondo with spacing focus', 'Position swapping exercise']
      },
      pressing: {
        score: 49,
        proScore: 86,
        issues: [
          { severity: 'high', issue: 'Solo pressing 55% of time (team not supporting)', fix: 'Only press when teammates supporting behind' },
          { severity: 'high', issue: 'Approach angle straight vs Pro curved run to block lane', fix: 'Curve run to block passing lane to nearest player' },
          { severity: 'high', issue: 'Wrong trigger recognition - presses when opponent comfortable', fix: 'Press when opponent has bad touch or facing away' },
          { severity: 'medium', issue: 'Press distance closes to 0.5m vs Pro 1-1.5m optimal', fix: 'Don\'t get too close, force mistake' }
        ],
        strengths: ['High energy and intensity', 'Willing to press aggressively'],
        drills: ['Team pressing coordination', 'Pressing triggers recognition', 'Curved pressing runs - 15 reps']
      },
      transition: {
        score: 56,
        proScore: 89,
        issues: [
          { severity: 'high', issue: 'Reaction time to turnover 1.2s vs Pro 0.4s', fix: 'Immediate pressure on ball within 5 seconds of losing it' },
          { severity: 'medium', issue: 'Position 8m too high when attacking (risky)', fix: 'Drop 5m deeper for defensive balance' },
          { severity: 'medium', issue: 'Counter-attack sprint speed 75% max vs Pro 95%+ max', fix: 'Explode forward at full speed in attacking transition' },
          { severity: 'low', issue: 'Decision making in transition 65% correct', fix: 'Faster recognition of press vs drop back' }
        ],
        strengths: ['Awareness of transitions improving', 'Recovery speed adequate at 7.2m/s', 'Understanding of counter-attacks'],
        drills: ['Transition scenarios - attack to defense', '5-second press after loss', 'Counter-attack sprints']
      },
      shape: {
        score: 63,
        proScore: 91,
        issues: [
          { severity: 'medium', issue: 'Leaves position to follow ball 40% of time', fix: 'Trust teammates, hold your position in formation' },
          { severity: 'medium', issue: 'Formation recognition time 3s vs Pro instant', fix: 'Faster recognition of 4-4-2 vs 4-3-3 etc' },
          { severity: 'low', issue: 'Adaptation to formation change takes 8-12s', fix: 'Communicate and adapt shape quicker (target: 3-5s)' }
        ],
        strengths: ['Good tactical understanding for age/level', 'Disciplined when focused', 'Follows instructions well', 'Improving game intelligence'],
        drills: ['Shape maintenance drill', 'Shadow play without ball', 'Positional awareness game']
      }
    };

    return analyses[selectedSubSkill] || analyses.power_shot;
  };

  const [currentAnalysis, setCurrentAnalysis] = useState(null);

  const simulateAnalysis = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      setAnalysisComplete(true);
      setCurrentAnalysis(getAnalysisData());
      setActiveTab('analysis');
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto p-4 md:p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-xl flex items-center justify-center">
              <Zap className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">PlaySmart</h1>
          </div>
          <p className="text-gray-400">AI-Powered Football Training Platform</p>
        </div>

        {/* Navigation */}
        <div className="flex flex-wrap gap-2 mb-6 bg-slate-800/50 p-2 rounded-xl">
          {[
            { id: 'upload', icon: Upload, label: 'Upload' },
            { id: 'analysis', icon: BarChart3, label: 'Analysis' },
            { id: 'progress', icon: TrendingUp, label: 'Progress' },
            { id: 'schedule', icon: Calendar, label: 'Schedule' },
            { id: 'match', icon: Brain, label: 'Match AI' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={tab.id === 'analysis' && !analysisComplete}
              className={`flex-1 min-w-[100px] py-2 px-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 text-sm ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Camera className="w-6 h-6 text-blue-400" />
                Upload Footage
              </h2>
              
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
                        <p className={`text-sm font-medium ${selectedSkill === key ? 'text-white' : 'text-gray-400'}`}>{skill.name}</p>
                      </button>
                    ))}
                  </div>

                  <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                    {skills[selectedSkill].subSkills.map(sub => (
                      <button
                        key={sub}
                        onClick={() => setSelectedSubSkill(sub)}
                        className={`p-2 rounded-lg text-xs font-medium transition-all ${
                          selectedSubSkill === sub ? 'bg-blue-600 text-white' : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                        }`}
                      >
                        {subSkillNames[sub]}
                      </button>
                    ))}
                  </div>

                  {analyzing ? (
                    <div className="bg-blue-600 text-white py-3 px-4 rounded-xl text-center">
                      <div className="animate-pulse flex items-center justify-center gap-2">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span className="font-medium">Analyzing {subSkillNames[selectedSubSkill]}...</span>
                      </div>
                    </div>
                  ) : (
                    <button onClick={simulateAnalysis} className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white py-3 px-4 rounded-xl font-semibold flex items-center justify-center gap-2">
                      <Play className="w-5 h-5" />
                      Analyze {subSkillNames[selectedSubSkill]}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && analysisComplete && currentAnalysis && (
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-white">{subSkillNames[selectedSubSkill]} Analysis</h2>
                <div className="text-right">
                  <div className="text-4xl font-bold text-blue-400">{currentAnalysis.score}</div>
                  <div className="text-gray-400 text-sm">Score</div>
                </div>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3">
                <div className="bg-gradient-to-r from-blue-600 to-blue-400 h-3 rounded-full" style={{ width: `${currentAnalysis.score}%` }}></div>
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-400" />
                Issues Detected
              </h3>
              <div className="space-y-2">
                {currentAnalysis.issues.map((item, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border-l-4 ${
                    item.severity === 'high' ? 'bg-red-500/10 border-red-500' : 
                    item.severity === 'medium' ? 'bg-orange-500/10 border-orange-500' : 
                    'bg-yellow-500/10 border-yellow-500'
                  }`}>
                    <div className="flex items-start gap-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        item.severity === 'high' ? 'bg-red-500 text-white' :
                        item.severity === 'medium' ? 'bg-orange-500 text-white' :
                        'bg-yellow-500 text-black'
                      }`}>
                        {item.severity.toUpperCase()}
                      </span>
                      <p className="text-white text-sm font-medium flex-1">{item.issue}</p>
                    </div>
                    <p className="text-green-400 text-xs ml-2">✓ {item.fix}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Strengths
              </h3>
              <div className="flex flex-wrap gap-2">
                {currentAnalysis.strengths.map((s, i) => (
                  <span key={i} className="bg-green-500/10 border border-green-500/30 rounded-lg px-3 py-1 text-green-400 text-sm">{s}</span>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-xl p-6 border border-blue-500/30">
              <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                <Award className="w-6 h-6 text-blue-400" />
                Personalized Training Plan
              </h3>
              <div className="space-y-2">
                {currentAnalysis.drills.map((drill, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex items-center gap-3">
                    <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {idx + 1}
                    </div>
                    <p className="text-gray-300 text-sm flex-1">{drill}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Progress Tab */}
        {activeTab === 'progress' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Improvement Tracker</h2>
              {Object.entries(progressData).map(([key, data]) => {
                const remaining = ((data.target - data.current) / (data.target - (data.current - data.improved))) * 100;
                const progress = (data.improved / (data.target - (data.current - data.improved))) * 100;
                return (
                  <div key={key} className="mb-4 last:mb-0">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-medium capitalize">{skills[key].name}</span>
                      <div className="text-right">
                        <span className="text-2xl font-bold text-white">{data.current}</span>
                        <span className="text-gray-400 text-sm"> / {data.target}</span>
                      </div>
                    </div>
                    <div className="flex gap-2 items-center mb-1">
                      <div className="flex-1 bg-slate-700 rounded-full h-3">
                        <div className={`bg-${skills[key].color}-500 h-3 rounded-full`} style={{ width: `${(data.current / data.target) * 100}%` }}></div>
                      </div>
                      <span className="text-xs font-medium text-gray-400">{Math.round((data.current / data.target) * 100)}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-green-400">+{data.improved} improved</span>
                      <span className="text-orange-400">{data.target - data.current} to target</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 border border-green-500/30 rounded-xl p-4">
                <TrendingUp className="w-8 h-8 text-green-400 mb-2" />
                <div className="text-2xl font-bold text-white">35</div>
                <div className="text-gray-400 text-sm">Total Points Gained</div>
              </div>
              <div className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 border border-blue-500/30 rounded-xl p-4">
                <Video className="w-8 h-8 text-blue-400 mb-2" />
                <div className="text-2xl font-bold text-white">12</div>
                <div className="text-gray-400 text-sm">Videos Analyzed</div>
              </div>
              <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 border border-purple-500/30 rounded-xl p-4">
                <Award className="w-8 h-8 text-purple-400 mb-2" />
                <div className="text-2xl font-bold text-white">21</div>
                <div className="text-gray-400 text-sm">Days Training</div>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Tab */}
        {activeTab === 'schedule' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Clock className="w-6 h-6 text-blue-400" />
                Your Training Schedule
              </h2>
              
              <div className="mb-4">
                <label className="text-gray-300 text-sm mb-2 block">Hours available per week: {hoursPerWeek}h</label>
                <input
                  type="range"
                  min="2"
                  max="15"
                  value={hoursPerWeek}
                  onChange={(e) => setHoursPerWeek(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div className="space-y-3">
                {schedule.map((session, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 bg-${skills[session.focus].color}-500 rounded-lg flex items-center justify-center`}>
                          {React.createElement(skills[session.focus].icon, { className: 'w-5 h-5 text-white' })}
                        </div>
                        <div>
                          <div className="text-white font-semibold">{session.day}</div>
                          <div className="text-gray-400 text-sm capitalize">{skills[session.focus].name} Focus</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-blue-400 font-semibold">{session.duration} min</div>
                      </div>
                    </div>
                    <div className="space-y-1">
                      {session.drills.map((drill, i) => (
                        <div key={i} className="text-gray-300 text-sm flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                          {drill}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Match Analysis Tab */}
        {activeTab === 'match' && (
          <div className="space-y-4">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Brain className="w-6 h-6 text-purple-400" />
                Match Intelligence Analysis
              </h2>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-red-400 mb-2">Nervous Moments</h3>
                  {matchAnalysis.nervousPoints.map((point, idx) => (
                    <div key={idx} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-2">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-white font-medium">{point.situation}</span>
                        <span className="text-red-400 text-sm">{point.time}</span>
                      </div>
                      <p className="text-gray-400 text-sm">{point.action}</p>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-orange-400 mb-2">Confusion Points</h3>
                  {matchAnalysis.confusedPoints.map((point, idx) => (
                    <div key={idx} className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-2">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-white font-medium">{point.situation}</span>
                        <span className="text-orange-400 text-sm">{point.time}</span>
                      </div>
                      <p className="text-gray-400 text-sm">{point.action}</p>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-blue-400 mb-2">Positioning Errors</h3>
                  {matchAnalysis.positioningErrors.map((point, idx) => (
                    <div key={idx} className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-2">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-white font-medium">{point.error}</span>
                        <span className="text-blue-400 text-sm">{point.time}</span>
                      </div>
                      <p className="text-green-400 text-sm">✓ {point.correction}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaySmart;
