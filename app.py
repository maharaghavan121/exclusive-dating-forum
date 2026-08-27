#!/usr/bin/env python3
"""
Kindred - Exclusive Dating Forum & Anti-Swiping Platform
Clean landing page + interactive questionnaire matching the exact design aesthetic.
Zero dependencies: python3 app.py
"""

import http.server
import json
import os
import random
import socketserver
import time
import urllib.parse
from http import HTTPStatus

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions.json")


def load_submissions():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_submissions(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>kindred — Dating is broken. Let's fix the conversation.</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@1,600;1,700;1,800&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: #FAF7F2;
      color: #191817;
    }
    .font-serif-italic {
      font-family: 'Playfair Display', Georgia, serif;
      font-style: italic;
      color: #C85A32;
    }
    .card-shadow {
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .quiz-option:hover {
      border-color: #C85A32;
      background-color: #FDF9F5;
    }
    .quiz-option.selected {
      border-color: #C85A32;
      background-color: #FDF3EC;
    }
    .fade-in {
      animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col justify-between selection:bg-[#F3D7C8] selection:text-[#933718]">

  <!-- Top Navigation -->
  <header class="w-full max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
    <div class="flex items-center gap-2 cursor-pointer" onclick="goToHome()">
      <span class="text-[#C85A32] text-xl font-bold">✦</span>
      <span class="text-xl font-extrabold tracking-tight text-[#191817]">kindred</span>
      <span class="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full bg-[#ECE7DE] text-[#6B655B]">BETA</span>
    </div>

    <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-[#6B655B]">
      <a href="javascript:void(0)" onclick="openModal('manifesto')" class="hover:text-[#191817] transition">Manifesto</a>
      <a href="javascript:void(0)" onclick="openModal('forumPeek')" class="hover:text-[#191817] transition">Forum Peek</a>
      <a href="javascript:void(0)" onclick="openModal('faq')" class="hover:text-[#191817] transition">FAQ</a>
    </nav>

    <div class="flex items-center gap-3">
      <button id="soundToggle" onclick="toggleSound()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-[#ECE7DE] text-[#554F45] hover:bg-[#E3DDD2] transition">
        <span id="soundIcon">🔊</span>
        <span>Sound: <span id="soundStatus">On</span></span>
      </button>
      <button onclick="startQuiz()" class="px-5 py-2 rounded-full text-xs font-bold bg-[#191817] text-white hover:bg-black transition shadow-sm">
        Take the Quiz
      </button>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main id="mainContainer" class="w-full max-w-4xl mx-auto px-6 py-10 flex-1 flex flex-col justify-center">

    <!-- VIEW 1: HERO LANDING PAGE -->
    <div id="landingView" class="text-center space-y-8 fade-in">
      
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-[#E8E2D8] text-xs font-medium shadow-sm">
        <span class="text-[#C85A32]">✦</span>
        <span class="text-[#191817] font-semibold">The Anti-Swiping Movement</span>
        <span class="text-[#999]">•</span>
        <span class="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
        <span class="text-emerald-700 font-bold">2,480+ Founding Members Joined</span>
      </div>

      <div class="space-y-1">
        <h1 class="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-[#191817]">
          Dating is broken.
        </h1>
        <div class="text-4xl sm:text-5xl md:text-6xl font-serif-italic font-bold tracking-tight">
          Let's fix the conversation.
        </div>
      </div>

      <p class="max-w-2xl mx-auto text-[#666055] text-base sm:text-lg leading-relaxed">
        Endless matching without substance is exhausting. Kindred is a private, curated forum & community built for intentional singles who value candid banter, real debates, and genuine chemistry over photo galleries.
      </p>

      <div class="pt-2 space-y-3">
        <button onclick="startQuiz()" class="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-[#191817] hover:bg-black text-white text-base font-bold shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5">
          <span>Discover Your Connection Archetype</span>
          <span>→</span>
        </button>

        <div class="flex flex-wrap items-center justify-center gap-3 text-xs text-[#8A8478] pt-2">
          <span>⏱ 90-second vibe audit</span>
          <span>•</span>
          <span>🎟 Unlocks Founding Pass #</span>
          <span>•</span>
          <span class="inline-flex items-center gap-1 bg-[#ECE7DE] px-2 py-0.5 rounded text-[11px] font-mono text-[#554F45]">Press <b class="font-sans font-bold">Enter ↵</b></span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 pt-10 text-left">
        
        <div class="bg-white p-7 rounded-2xl border border-[#ECE7DE] card-shadow space-y-3 hover:border-[#D9CFBF] transition">
          <div class="w-9 h-9 rounded-xl bg-[#FAF7F2] text-xl flex items-center justify-center">💬</div>
          <h3 class="font-bold text-base text-[#191817]">Conversations First</h3>
          <p class="text-xs text-[#6B655B] leading-relaxed">
            Spark connections through spicy debates, anonymous confessions, and shared humor before faces.
          </p>
        </div>

        <div class="bg-white p-7 rounded-2xl border border-[#ECE7DE] card-shadow space-y-3 hover:border-[#D9CFBF] transition">
          <div class="w-9 h-9 rounded-xl bg-[#FAF7F2] text-xl flex items-center justify-center">🛡️</div>
          <h3 class="font-bold text-base text-[#191817]">Zero Creep Tolerance</h3>
          <p class="text-xs text-[#6B655B] leading-relaxed">
            Peer-vetted membership, mutual opt-in DMs, and high-trust community standards.
          </p>
        </div>

        <div class="bg-white p-7 rounded-2xl border border-[#ECE7DE] card-shadow space-y-3 hover:border-[#D9CFBF] transition">
          <div class="w-9 h-9 rounded-xl bg-[#FAF7F2] text-xl flex items-center justify-center">✨</div>
          <h3 class="font-bold text-base text-[#191817]">Archetype Matching</h3>
          <p class="text-xs text-[#6B655B] leading-relaxed">
            Our algorithm pairs you with individuals who match your emotional depth and conversational rhythm.
          </p>
        </div>

      </div>

    </div>

    <!-- VIEW 2: INTERACTIVE QUESTIONNAIRE -->
    <div id="quizView" class="hidden max-w-2xl mx-auto w-full space-y-8 fade-in">
      <div class="space-y-2">
        <div class="flex justify-between text-xs font-semibold text-[#8A8478]">
          <span id="quizStepIndicator">Question 1 of 5</span>
          <span id="quizPercent">20% Completed</span>
        </div>
        <div class="w-full h-1.5 bg-[#E8E2D8] rounded-full overflow-hidden">
          <div id="quizProgressBar" class="h-full bg-[#C85A32] rounded-full transition-all duration-300 w-1/5"></div>
        </div>
      </div>

      <div id="questionContainer" class="bg-white p-8 sm:p-10 rounded-3xl border border-[#ECE7DE] card-shadow space-y-6">
      </div>
    </div>

    <!-- VIEW 3: FOUNDING PASS REVEAL -->
    <div id="resultView" class="hidden max-w-lg mx-auto w-full space-y-6 fade-in text-center">
      <div class="bg-white p-8 sm:p-10 rounded-3xl border-2 border-[#C85A32] card-shadow space-y-6 relative overflow-hidden">
        <div class="absolute -right-8 -top-8 text-9xl text-[#FDF3EC] font-serif select-none pointer-events-none">✦</div>
        
        <div class="space-y-2">
          <span class="px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider bg-[#FDF3EC] text-[#C85A32]">
            Vibe Audit Verified
          </span>
          <h2 class="text-3xl font-extrabold text-[#191817]" id="resultArchetype">The Witty Strategist</h2>
          <p class="text-xs text-[#6B655B]" id="resultDesc">You thrive in dynamic environments with high banter, playful debate, and authentic chemistry.</p>
        </div>

        <div class="p-6 rounded-2xl bg-[#191817] text-white text-left space-y-4 relative shadow-lg">
          <div class="flex justify-between items-start border-b border-neutral-800 pb-3">
            <div>
              <div class="text-[10px] font-mono tracking-widest text-[#C85A32] uppercase font-bold">KINDRED FOUNDING PASS</div>
              <div class="text-xl font-bold tracking-tight text-white" id="passHolderName">Alex M.</div>
            </div>
            <span class="text-2xl text-[#C85A32]">✦</span>
          </div>
          
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-neutral-400 block text-[10px] uppercase">Cohort Format</span>
              <span class="font-bold text-white">20-Friend Forum</span>
            </div>
            <div>
              <span class="text-neutral-400 block text-[10px] uppercase">Preferred Activity</span>
              <span class="font-bold text-white" id="passActivity">Pickleball Social</span>
            </div>
            <div>
              <span class="text-neutral-400 block text-[10px] uppercase">Pass Number</span>
              <span class="font-mono font-bold text-emerald-400" id="passNumber">#02489</span>
            </div>
            <div>
              <span class="text-neutral-400 block text-[10px] uppercase">Status</span>
              <span class="font-bold text-amber-400">VIP Priority RSVP</span>
            </div>
          </div>
        </div>

        <div class="space-y-2 pt-2">
          <button onclick="goToHome()" class="w-full py-3.5 rounded-full bg-[#C85A32] hover:bg-[#B34C27] text-white text-sm font-bold shadow-md transition">
            Back to Kindred Home
          </button>
          <p class="text-[11px] text-[#8A8478]">Check your inbox for your private calendar invite and cohort details.</p>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer class="w-full max-w-6xl mx-auto px-6 py-6 border-t border-[#ECE7DE] text-xs text-[#8A8478] flex flex-col sm:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-2">
      <span class="text-[#C85A32]">✦</span>
      <span class="font-bold text-[#191817]">kindred</span>
      <span>• The 20-Person Intentional Dating Forum</span>
    </div>
    <div class="flex items-center gap-4">
      <a href="javascript:void(0)" onclick="openModal('submissions')" class="hover:text-[#191817] font-semibold underline">Host Dashboard (View RSVPs)</a>
      <span>© 2026 Kindred Club</span>
    </div>
  </footer>

  <!-- Modals -->
  <div id="modalOverlay" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4" onclick="closeModal()">
    <div id="modalContent" class="bg-white rounded-3xl max-w-lg w-full p-8 space-y-5 card-shadow border border-[#ECE7DE] relative max-h-[85vh] overflow-y-auto" onclick="event.stopPropagation()">
      <button onclick="closeModal()" class="absolute top-5 right-5 text-lg text-[#8A8478] hover:text-black">✕</button>
      <div id="modalBody"></div>
    </div>
  </div>

  <script>
    let soundEnabled = true;
    let currentStep = 0;
    let quizResponses = {};

    const questions = [
      {
        id: "grievance",
        tag: "THE PROBLEM",
        title: "What is your biggest grievance with modern dating apps?",
        subtitle: "Pick the one that makes you want to delete your apps the most.",
        options: [
          { key: "A", text: "Endless superficial small talk that never leads to a real date." },
          { key: "B", text: "Judging someone entirely on 5 curated photos and a 2-line bio." },
          { key: "C", text: "Ghosting, flake culture, and zero accountability." },
          { key: "D", text: "Awkward high-pressure 1-on-1 first dates across a table." }
        ]
      },
      {
        id: "activity",
        tag: "ACTIVITY PREFERENCE",
        title: "Which group activity would you most look forward to at a 20-person forum?",
        subtitle: "Shared experiences spark natural chemistry without forced small talk.",
        options: [
          { key: "A", text: "🎾 Pickleball Social: High-energy mixed doubles with rotating partners." },
          { key: "B", text: "🍕 Pizza Making Night: Hands-on cooking stations with paired prep." },
          { key: "C", text: "🍳 Cooking Cook-Off: Fun team challenge with mystery ingredients." },
          { key: "D", text: "🍷 Speakeasy Lounge: Deep conversational prompts & cocktails." }
        ]
      },
      {
        id: "energy",
        tag: "VIBE CHECK",
        title: "How do your closest friends describe your energy in social groups?",
        subtitle: "Helps us balance conversational archetypes across the 10 men and 10 women.",
        options: [
          { key: "A", text: "The Witty Sparkplug: Fast banter, storytelling, and high laughs." },
          { key: "B", text: "The Deep Explorer: Thoughtful questions, sincere curiosity, great listener." },
          { key: "C", text: "The Warm Harmonizer: Welcoming, inclusive, makes everyone comfortable." },
          { key: "D", text: "The Playful Instigator: Loves friendly competition, debates, and banter." }
        ]
      },
      {
        id: "gender",
        tag: "COHORT SELECTION",
        title: "Which 10-person cohort are you applying to join?",
        subtitle: "We maintain an exact 10 Women / 10 Men ratio for every gathering.",
        options: [
          { key: "A", text: "👩 Woman Cohort (Seeking Men)" },
          { key: "B", text: "👨 Man Cohort (Seeking Women)" },
          { key: "C", text: "✨ Other / Open Cohort" }
        ]
      },
      {
        id: "contact",
        tag: "FINAL STEP",
        title: "Where should we send your Connection Archetype & Pass?",
        subtitle: "You'll unlock your private pass number and founding membership audit.",
        isForm: true
      }
    ];

    function playBeep(freq = 440, type = 'sine', duration = 0.08) {
      if (!soundEnabled) return;
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      } catch (e) {}
    }

    function toggleSound() {
      soundEnabled = !soundEnabled;
      document.getElementById('soundStatus').innerText = soundEnabled ? 'On' : 'Off';
      document.getElementById('soundIcon').innerText = soundEnabled ? '🔊' : '🔇';
      if (soundEnabled) playBeep(580);
    }

    function startQuiz() {
      playBeep(520);
      document.getElementById('landingView').classList.add('hidden');
      document.getElementById('resultView').classList.add('hidden');
      document.getElementById('quizView').classList.remove('hidden');
      currentStep = 0;
      renderQuestion();
    }

    function goToHome() {
      document.getElementById('quizView').classList.add('hidden');
      document.getElementById('resultView').classList.add('hidden');
      document.getElementById('landingView').classList.remove('hidden');
    }

    function renderQuestion() {
      const q = questions[currentStep];
      const total = questions.length;
      
      document.getElementById('quizStepIndicator').innerText = `Question ${currentStep + 1} of ${total}`;
      document.getElementById('quizPercent').innerText = `${Math.round(((currentStep + 1) / total) * 100)}% Completed`;
      document.getElementById('quizProgressBar').style.width = `${((currentStep + 1) / total) * 100}%`;

      const container = document.getElementById('questionContainer');

      if (!q.isForm) {
        container.innerHTML = `
          <div class="space-y-2">
            <span class="text-[11px] font-extrabold uppercase tracking-widest text-[#C85A32] font-mono">${q.tag}</span>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-[#191817] leading-snug">${q.title}</h2>
            <p class="text-xs text-[#6B655B]">${q.subtitle}</p>
          </div>

          <div class="space-y-3 pt-2">
            ${q.options.map((opt, i) => `
              <button onclick="selectOption('${q.id}', '${opt.key}', '${opt.text.replace(/'/g, "\\'")}')" class="quiz-option w-full p-4 sm:p-5 rounded-2xl border border-[#E8E2D8] bg-white text-left flex items-center justify-between gap-4 transition group">
                <div class="flex items-center gap-3">
                  <span class="w-7 h-7 rounded-lg bg-[#FAF7F2] border border-[#E8E2D8] text-xs font-bold text-[#554F45] flex items-center justify-center group-hover:border-[#C85A32] group-hover:text-[#C85A32]">${opt.key}</span>
                  <span class="text-xs sm:text-sm font-semibold text-[#191817]">${opt.text}</span>
                </div>
                <span class="text-xs text-[#C85A32] font-bold opacity-0 group-hover:opacity-100 transition">Select →</span>
              </button>
            `).join('')}
          </div>
        `;
      } else {
        container.innerHTML = `
          <div class="space-y-2">
            <span class="text-[11px] font-extrabold uppercase tracking-widest text-[#C85A32] font-mono">${q.tag}</span>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-[#191817] leading-snug">${q.title}</h2>
            <p class="text-xs text-[#6B655B]">${q.subtitle}</p>
          </div>

          <form onsubmit="submitForm(event)" class="space-y-4 pt-2">
            <div>
              <label class="block text-xs font-bold text-[#191817] mb-1">Your Full Name</label>
              <input type="text" id="formName" required placeholder="e.g., Alex Miller" class="w-full px-4 py-3 rounded-xl border border-[#E8E2D8] bg-[#FAF7F2] text-sm focus:outline-none focus:ring-2 focus:ring-[#C85A32] focus:bg-white">
            </div>
            <div>
              <label class="block text-xs font-bold text-[#191817] mb-1">Email Address (for Invite Pass)</label>
              <input type="email" id="formEmail" required placeholder="alex@example.com" class="w-full px-4 py-3 rounded-xl border border-[#E8E2D8] bg-[#FAF7F2] text-sm focus:outline-none focus:ring-2 focus:ring-[#C85A32] focus:bg-white">
            </div>
            <div>
              <label class="block text-xs font-bold text-[#191817] mb-1">Instagram or LinkedIn (Optional / for Vetting)</label>
              <input type="text" id="formHandle" placeholder="@alex_miller" class="w-full px-4 py-3 rounded-xl border border-[#E8E2D8] bg-[#FAF7F2] text-sm focus:outline-none focus:ring-2 focus:ring-[#C85A32] focus:bg-white">
            </div>
            <button type="submit" class="w-full py-4 rounded-full bg-[#191817] hover:bg-black text-white text-sm font-bold shadow-md transition">
              Reveal My Archetype & Founding Pass →
            </button>
          </form>
        `;
      }
    }

    function selectOption(questionId, key, text) {
      playBeep(650);
      quizResponses[questionId] = { key, text };
      if (currentStep < questions.length - 1) {
        currentStep++;
        renderQuestion();
      }
    }

    async function submitForm(e) {
      e.preventDefault();
      playBeep(880, 'triangle', 0.2);

      const name = document.getElementById('formName').value;
      const email = document.getElementById('formEmail').value;
      const handle = document.getElementById('formHandle').value;

      quizResponses.name = name;
      quizResponses.email = email;
      quizResponses.handle = handle;
      quizResponses.timestamp = new Date().toISOString();

      const archetypes = [
        { name: "The Witty Strategist", desc: "You thrive on playful banter, high-energy games, and lively debates." },
        { name: "The Sincere Alchemist", desc: "You bring warmth and deep curiosity, creating comfortable spaces for real conversation." },
        { name: "The Playful Instigator", desc: "You love friendly competition and dynamic challenges like pickleball or cooking cook-offs." },
        { name: "The Cultural Epicurean", desc: "You connect through hands-on creative crafts, culinary tasting, and shared stories." }
      ];
      const chosen = archetypes[Math.floor(Math.random() * archetypes.length)];
      quizResponses.archetype = chosen.name;
      quizResponses.passNumber = "#" + (2480 + Math.floor(Math.random() * 100));

      await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(quizResponses)
      });

      document.getElementById('quizView').classList.add('hidden');
      document.getElementById('resultView').classList.remove('hidden');

      document.getElementById('resultArchetype').innerText = chosen.name;
      document.getElementById('resultDesc').innerText = chosen.desc;
      document.getElementById('passHolderName').innerText = name;
      document.getElementById('passNumber').innerText = quizResponses.passNumber;

      const actText = quizResponses.activity ? quizResponses.activity.text.split(':')[0] : 'Pickleball Social';
      document.getElementById('passActivity').innerText = actText;
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !document.getElementById('landingView').classList.contains('hidden')) {
        startQuiz();
      }
    });

    function openModal(type) {
      playBeep(480);
      const modal = document.getElementById('modalOverlay');
      const body = document.getElementById('modalBody');
      modal.classList.remove('hidden');

      if (type === 'manifesto') {
        body.innerHTML = `
          <div class="space-y-4">
            <span class="text-xs font-extrabold uppercase tracking-widest text-[#C85A32] font-mono">OUR MANIFESTO</span>
            <h2 class="text-2xl font-extrabold text-[#191817]">Death to the Endless Swipe.</h2>
            <p class="text-xs text-[#6B655B] leading-relaxed">
              We believe romance cannot be reduced to algorithmic casino slot machines. When you meet people through shared activities—making pizza, playing pickleball, or debating big ideas—the pressure dissolves and genuine chemistry takes over.
            </p>
            <p class="text-xs text-[#6B655B] leading-relaxed">
              Kindred curates balanced 20-person cohorts (10 women, 10 men) from trusted friend circles so every event is safe, intentional, and unforgettable.
            </p>
          </div>
        `;
      } else if (type === 'forumPeek') {
        body.innerHTML = `
          <div class="space-y-4">
            <span class="text-xs font-extrabold uppercase tracking-widest text-[#C85A32] font-mono">FORUM PEEK</span>
            <h2 class="text-2xl font-extrabold text-[#191817]">How the 20-Person Forum Works</h2>
            <div class="space-y-3 text-xs text-[#6B655B]">
              <div class="p-3 bg-[#FAF7F2] rounded-xl border border-[#E8E2D8]">
                <b class="text-[#191817]">1. Curated 10W / 10M Ratios:</b> Equal gender balance from mutual friend networks.
              </div>
              <div class="p-3 bg-[#FAF7F2] rounded-xl border border-[#E8E2D8]">
                <b class="text-[#191817]">2. Interactive Rotations:</b> Mini-games and station rotations so you naturally interact with everyone.
              </div>
              <div class="p-3 bg-[#FAF7F2] rounded-xl border border-[#E8E2D8]">
                <b class="text-[#191817]">3. Double-Blind Matchmaking:</b> Privately tell the host who you'd like to see again; mutual matches connect post-event with zero awkwardness.
              </div>
            </div>
          </div>
        `;
      } else if (type === 'faq') {
        body.innerHTML = `
          <div class="space-y-4">
            <span class="text-xs font-extrabold uppercase tracking-widest text-[#C85A32] font-mono">FAQ</span>
            <h2 class="text-2xl font-extrabold text-[#191817]">Frequently Asked Questions</h2>
            <div class="space-y-3 text-xs text-[#6B655B]">
              <div>
                <b class="text-[#191817]">How are attendees vetted?</b>
                <p>Every attendee is either a direct friend or nominated by an existing member to ensure high trust and zero creeps.</p>
              </div>
              <div>
                <b class="text-[#191817]">What is the cost?</b>
                <p>Events average $25–$40 per person to cover court rentals, pizza ingredients, and drinks.</p>
              </div>
              <div>
                <b class="text-[#191817]">Do I have to be good at sports or cooking?</b>
                <p>Not at all! Everything is geared towards casual fun and laughs rather than intense competition.</p>
              </div>
            </div>
          </div>
        `;
      } else if (type === 'submissions') {
        fetchSubmissions(body);
      }
    }

    async function fetchSubmissions(body) {
      const res = await fetch('/api/submissions');
      const data = await res.json();
      body.innerHTML = `
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-extrabold text-[#191817]">Host RSVP Tracker (${data.length})</h2>
            <span class="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">Live Submissions</span>
          </div>
          <div class="max-h-80 overflow-y-auto space-y-2 text-xs">
            ${data.length === 0 ? '<p class="text-slate-400 italic">No quiz submissions yet.</p>' : data.map((sub, i) => `
              <div class="p-3 bg-[#FAF7F2] rounded-xl border border-[#E8E2D8] space-y-1">
                <div class="flex justify-between font-bold text-[#191817]">
                  <span>${sub.name || 'Anonymous'} (${sub.gender ? sub.gender.key : '?'})</span>
                  <span class="font-mono text-[#C85A32]">${sub.passNumber || '#----'}</span>
                </div>
                <div class="text-[11px] text-[#6B655B]">${sub.email || ''} • Archetype: <b class="text-[#191817]">${sub.archetype || 'Pending'}</b></div>
                <div class="text-[10px] text-[#8A8478]">Activity: ${sub.activity ? sub.activity.text.slice(0, 40) : 'None'}...</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    function closeModal() {
      document.getElementById('modalOverlay').classList.add('hidden');
    }
  </script>
</body>
</html>
"""


class KindredRequestHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def _set_headers(self, content_type="text/html"):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._set_headers("text/html; charset=utf-8")
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/submissions":
            subs = load_submissions()
            self._set_headers("application/json")
            self.wfile.write(json.dumps(subs).encode("utf-8"))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b"{}"

        if parsed.path == "/api/submit":
            try:
                new_sub = json.loads(post_data.decode("utf-8"))
                subs = load_submissions()
                subs.append(new_sub)
                save_submissions(subs)
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"status": "saved"}).encode("utf-8"))
            except Exception as e:
                self.send_error(HTTPStatus.BAD_REQUEST, str(e))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), KindredRequestHandler) as httpd:
        print("=" * 60)
        print(f"✨ Kindred Anti-Swiping Platform running at:")
        print(f"👉 http://localhost:\{PORT\}")
        print("\=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
