#!/usr/bin/env python3
"""
Exclusive Dating Forum - Event Manager & Interactive Platform
A standalone Python web app with ZERO external dependencies.
Runs with standard library: python3 app.py
"""

import http.server
import json
import os
import random
import socketserver
import urllib.parse
from http import HTTPStatus

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

DEFAULT_DATA = {
    "event": {
        "title": "Exclusive Dating Forum",
        "description": "An activity-driven, low-pressure curated social evening for 20 single friends (10 women and 10 men).",
        "target_date": "2026-09-18",
        "target_time": "18:30",
        "venue": "Private Studio / Outdoor Courts",
        "selected_activity": "Pickleball Social",
        "budget_per_person": 35
    },
    "guests": [
        {"id": "w1", "name": "Sarah J.", "gender": "female", "status": "confirmed", "notes": "Loves cooking, pickleball beginner"},
        {"id": "w2", "name": "Elena R.", "gender": "female", "status": "confirmed", "notes": "Outdoor enthusiast, foodie"},
        {"id": "w3", "name": "Maya P.", "gender": "female", "status": "confirmed", "notes": "Plays tennis, works in design"},
        {"id": "w4", "name": "Chloe T.", "gender": "female", "status": "confirmed", "notes": "Loves baking, friendly"},
        {"id": "w5", "name": "Jessica K.", "gender": "female", "status": "invited", "notes": "Tech PM, loves running"},
        {"id": "w6", "name": "Amina D.", "gender": "female", "status": "invited", "notes": "Coffee lover, creative"},
        {"id": "w7", "name": "Rachel B.", "gender": "female", "status": "invited", "notes": "Book club friend"},
        {"id": "w8", "name": "Hannah L.", "gender": "female", "status": "invited", "notes": "Dog mom, great conversationalist"},
        {"id": "w9", "name": "Tara M.", "gender": "female", "status": "invited", "notes": "Referred by Alex"},
        {"id": "w10", "name": "Nina W.", "gender": "female", "status": "invited", "notes": "Loves board games & wine"},
        {"id": "m1", "name": "David K.", "gender": "male", "status": "confirmed", "notes": "Software engineer, plays pickleball"},
        {"id": "m2", "name": "Alex M.", "gender": "male", "status": "confirmed", "notes": "Home chef, loves hosting"},
        {"id": "m3", "name": "Marcus C.", "gender": "male", "status": "confirmed", "notes": "Marathon runner, upbeat vibe"},
        {"id": "m4", "name": "Samir G.", "gender": "male", "status": "confirmed", "notes": "Product designer, cocktail enthusiast"},
        {"id": "m5", "name": "Liam H.", "gender": "male", "status": "invited", "notes": "Musician & consultant"},
        {"id": "m6", "name": "Julian B.", "gender": "male", "status": "invited", "notes": "College friend, easygoing"},
        {"id": "m7", "name": "Daniel F.", "gender": "male", "status": "invited", "notes": "Architect, travels often"},
        {"id": "m8", "name": "Rohan S.", "gender": "male", "status": "invited", "notes": "Climbing, tech founder"},
        {"id": "m9", "name": "Kevin Z.", "gender": "male", "status": "invited", "notes": "Loves trivia & cooking"},
        {"id": "m10", "name": "Ethan N.", "gender": "male", "status": "invited", "notes": "High school buddy, funny"}
    ],
    "interests": {}
}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Exclusive Dating Forum – Event Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .tab-active { border-bottom: 3px solid #6366f1; color: #6366f1; font-weight: 700; }
  </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen">
  
  <!-- Header -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <span class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-rose-500 flex items-center justify-center text-white text-xl shadow-md">✨</span>
        <div>
          <h1 class="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-600 to-rose-600 bg-clip-text text-transparent" id="appTitle">Exclusive Dating Forum</h1>
          <p class="text-xs text-slate-500">Curated 20-Person Social & Activity Matchmaker</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          10W + 10M Format
        </span>
        <button onclick="resetToDefaults()" class="px-3 py-1 text-xs text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition">Reset Sample Data</button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="max-w-6xl mx-auto px-4 flex gap-6 overflow-x-auto text-sm font-medium border-t border-slate-100">
      <button onclick="showTab('dashboard')" id="tab-dashboard" class="py-3 px-2 tab-active transition">📊 Event Overview</button>
      <button onclick="showTab('guests')" id="tab-guests" class="py-3 px-2 text-slate-500 hover:text-slate-800 transition">👥 Guest List (20)</button>
      <button onclick="showTab('activities')" id="tab-activities" class="py-3 px-2 text-slate-500 hover:text-slate-800 transition">🎾 Activity Rotations</button>
      <button onclick="showTab('matchmaker')" id="tab-matchmaker" class="py-3 px-2 text-slate-500 hover:text-slate-800 transition">🔒 Secret Matchmaker</button>
    </div>
  </header>

  <!-- Main Content Area -->
  <main class="max-w-6xl mx-auto px-4 py-8">

    <!-- 1. DASHBOARD TAB -->
    <section id="view-dashboard" class="space-y-6">
      
      <!-- Stats Banner -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-pink-100 text-pink-600 flex items-center justify-center text-xl font-bold">👩</div>
          <div>
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Women Confirmed</div>
            <div class="text-2xl font-bold text-slate-800" id="womenCount">0 / 10</div>
          </div>
        </div>
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center text-xl font-bold">👨</div>
          <div>
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Men Confirmed</div>
            <div class="text-2xl font-bold text-slate-800" id="menCount">0 / 10</div>
          </div>
        </div>
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center text-xl font-bold">🎯</div>
          <div>
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Selected Activity</div>
            <div class="text-base font-bold text-slate-800" id="statActivity">Pickleball Social</div>
          </div>
        </div>
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center text-xl font-bold">💵</div>
          <div>
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Est. Budget / Person</div>
            <div class="text-2xl font-bold text-slate-800" id="statBudget">$35</div>
          </div>
        </div>
      </div>

      <!-- Event Details Card -->
      <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-slate-800">Event Settings & Concept</h2>
          <button onclick="saveEventSettings()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">Save Details</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Event Title</label>
            <input type="text" id="eventTitle" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Primary Activity</label>
            <select id="eventActivity" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none">
              <option value="Pickleball Social">Pickleball Social (Rotating Doubles)</option>
              <option value="Make Pizza Together">Make Pizza Together (Kitchen Stations)</option>
              <option value="Cooking Competition">Cooking Competition (Team Cook-Off)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Target Date & Time</label>
            <input type="datetime-local" id="eventDate" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Target Venue / Location</label>
            <input type="text" id="eventVenue" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none">
          </div>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">Concept & Host Notes</label>
          <textarea id="eventDesc" rows="2" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"></textarea>
        </div>
      </div>

    </section>

    <!-- 2. GUEST LIST TAB -->
    <section id="view-guests" class="hidden space-y-6">
      <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Guest Tracker (10 Women / 10 Men)</h2>
          <p class="text-xs text-slate-500">Track invites, RSVPs, and personality notes for the 20 attendees.</p>
        </div>
        <button onclick="promptAddGuest('female')" class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">
          + Add Guest
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Women Column (10) -->
        <div class="bg-white p-5 rounded-2xl border border-pink-100 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-pink-500"></span>
              <h3 class="font-bold text-slate-800">Women (10 Slots)</h3>
            </div>
            <span id="womenBadge" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-pink-50 text-pink-700">0/10 Confirmed</span>
          </div>
          <div id="womenList" class="space-y-2.5"></div>
        </div>

        <!-- Men Column (10) -->
        <div class="bg-white p-5 rounded-2xl border border-blue-100 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 pb-3">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span>
              <h3 class="font-bold text-slate-800">Men (10 Slots)</h3>
            </div>
            <span id="menBadge" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">0/10 Confirmed</span>
          </div>
          <div id="menList" class="space-y-2.5"></div>
        </div>

      </div>
    </section>

    <!-- 3. ACTIVITY ROTATIONS TAB -->
    <section id="view-activities" class="hidden space-y-6">
      <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Interactive Activity Rotation Engine</h2>
          <p class="text-xs text-slate-500">Auto-generate mixed pairs and group rotations so all 20 friends get to interact.</p>
        </div>
        <div class="flex gap-2">
          <button onclick="generatePickleball()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">
            🎾 Pickleball Bracket
          </button>
          <button onclick="generateStations('Pizza Making Stations')" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">
            🍕 Pizza Stations
          </button>
          <button onclick="generateStations('Cooking Cook-Off Teams')" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">
            🍳 Cook-Off Teams
          </button>
        </div>
      </div>

      <div id="rotationOutput" class="space-y-6"></div>
    </section>

    <!-- 4. SECRET MATCHMAKER TAB -->
    <section id="view-matchmaker" class="hidden space-y-6">
      <div class="bg-gradient-to-r from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-lg space-y-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">🔒</span>
          <div>
            <h2 class="text-lg font-bold">Double-Blind Mutual Matchmaker</h2>
            <p class="text-xs text-slate-300">Guests privately select who they'd like to see again. Mutual matches are automatically revealed only to the host!</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Submit Interest Form -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 class="font-bold text-slate-800 text-sm">Guest Interest Submission</h3>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Select Guest</label>
            <select id="matchGuestSelect" onchange="loadGuestPicks()" class="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500">
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-2">Check the people they'd like to see again:</label>
            <div id="targetPicksList" class="max-h-60 overflow-y-auto space-y-1.5 p-2 bg-slate-50 rounded-xl border border-slate-100 text-sm"></div>
          </div>
          <button onclick="savePicks()" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition">
            Save Private Picks
          </button>
        </div>

        <!-- Mutual Matches Reveal (Organizer View) -->
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-800 text-sm">🎉 Calculated Mutual Matches</h3>
            <span class="text-xs px-2 py-1 bg-emerald-100 text-emerald-800 rounded-lg font-semibold" id="matchCountBadge">0 Matches</span>
          </div>
          <div id="mutualMatchesList" class="space-y-3"></div>
        </div>

      </div>
    </section>

  </main>

  <script>
    let appData = {};

    async function fetchData() {
      const res = await fetch('/api/data');
      appData = await res.json();
      renderAll();
    }

    function renderAll() {
      document.getElementById('appTitle').innerText = appData.event.title || 'Exclusive Dating Forum';
      document.getElementById('eventTitle').value = appData.event.title || '';
      document.getElementById('eventActivity').value = appData.event.selected_activity || 'Pickleball Social';
      document.getElementById('statActivity').innerText = appData.event.selected_activity || 'Pickleball Social';
      document.getElementById('eventVenue').value = appData.event.venue || '';
      document.getElementById('eventDesc').value = appData.event.description || '';
      document.getElementById('statBudget').innerText = '$' + (appData.event.budget_per_person || 35);
      
      if (appData.event.target_date) {
        document.getElementById('eventDate').value = `${appData.event.target_date}T${appData.event.target_time || '18:30'}`;
      }

      const women = appData.guests.filter(g => g.gender === 'female');
      const men = appData.guests.filter(g => g.gender === 'male');
      const womenConfirmed = women.filter(g => g.status === 'confirmed').length;
      const menConfirmed = men.filter(g => g.status === 'confirmed').length;

      document.getElementById('womenCount').innerText = `${womenConfirmed} / 10`;
      document.getElementById('menCount').innerText = `${menConfirmed} / 10`;
      document.getElementById('womenBadge').innerText = `${womenConfirmed}/10 Confirmed`;
      document.getElementById('menBadge').innerText = `${menConfirmed}/10 Confirmed`;

      renderGuestColumn('womenList', women, 'female');
      renderGuestColumn('menList', men, 'male');
      renderMatchmakerOptions();
      calculateMatches();
    }

    function renderGuestColumn(containerId, list, gender) {
      const container = document.getElementById(containerId);
      container.innerHTML = '';
      
      for (let i = 0; i < 10; i++) {
        const guest = list[i];
        const card = document.createElement('div');
        card.className = `p-3 rounded-xl border transition flex items-center justify-between gap-3 ${
          guest ? (guest.status === 'confirmed' ? 'bg-white border-slate-200' : 'bg-slate-50 border-dashed border-slate-200') : 'bg-slate-50 border-dashed border-slate-200 opacity-60'
        }`;

        if (guest) {
          card.innerHTML = `
            <div class="flex items-center gap-3">
              <span class="text-xs font-bold text-slate-400 w-5">#${i+1}</span>
              <div>
                <div class="text-sm font-semibold text-slate-800">${guest.name}</div>
                <div class="text-xs text-slate-500">${guest.notes || 'No notes'}</div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <select onchange="updateGuestStatus('${guest.id}', this.value)" class="text-xs font-semibold rounded-lg px-2 py-1 border border-slate-200 focus:outline-none ${
                guest.status === 'confirmed' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
              }">
                <option value="confirmed" ${guest.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                <option value="invited" ${guest.status === 'invited' ? 'selected' : ''}>Invited</option>
                <option value="declined" ${guest.status === 'declined' ? 'selected' : ''}>Declined</option>
              </select>
            </div>
          `;
        } else {
          card.innerHTML = `
            <div class="flex items-center gap-3">
              <span class="text-xs font-bold text-slate-300 w-5">#${i+1}</span>
              <span class="text-xs text-slate-400 italic">[Empty Slot ${i+1}]</span>
            </div>
            <button onclick="promptAddGuest('${gender}')" class="text-xs text-indigo-600 font-semibold hover:underline">+ Add</button>
          `;
        }
        container.appendChild(card);
      }
    }

    async function updateGuestStatus(id, newStatus) {
      const g = appData.guests.find(x => x.id === id);
      if (g) {
        g.status = newStatus;
        await fetch('/api/data', { method: 'POST', body: JSON.stringify(appData) });
        renderAll();
      }
    }

    function promptAddGuest(gender) {
      const name = prompt(`Enter name for new ${gender} guest:`);
      if (name) {
        const notes = prompt("Enter brief notes or interests:") || "";
        appData.guests.push({
          id: 'g_' + Date.now(),
          name: name,
          gender: gender,
          status: 'invited',
          notes: notes
        });
        saveAndRefresh();
      }
    }

    async function saveEventSettings() {
      appData.event.title = document.getElementById('eventTitle').value;
      appData.event.selected_activity = document.getElementById('eventActivity').value;
      appData.event.venue = document.getElementById('eventVenue').value;
      appData.event.description = document.getElementById('eventDesc').value;
      const dt = document.getElementById('eventDate').value;
      if (dt) {
        appData.event.target_date = dt.split('T')[0];
        appData.event.target_time = dt.split('T')[1];
      }
      await saveAndRefresh();
      alert("Event details saved!");
    }

    async function saveAndRefresh() {
      await fetch('/api/data', { method: 'POST', body: JSON.stringify(appData) });
      renderAll();
    }

    function showTab(tabName) {
      ['dashboard', 'guests', 'activities', 'matchmaker'].forEach(t => {
        document.getElementById(`view-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).classList.remove('tab-active');
        document.getElementById(`tab-${t}`).classList.add('text-slate-500');
      });
      document.getElementById(`view-${tabName}`).classList.remove('hidden');
      document.getElementById(`tab-${tabName}`).classList.add('tab-active');
      document.getElementById(`tab-${tabName}`).classList.remove('text-slate-500');

      if (tabName === 'activities' && !document.getElementById('rotationOutput').innerHTML) {
        generatePickleball();
      }
    }

    function generatePickleball() {
      const women = appData.guests.filter(g => g.gender === 'female').map(g => g.name);
      const men = appData.guests.filter(g => g.gender === 'male').map(g => g.name);

      let html = `
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div class="flex justify-between items-center border-b pb-4">
            <div>
              <h3 class="font-bold text-slate-800 text-lg">🎾 Pickleball Mixed Doubles Round-Robin</h3>
              <p class="text-xs text-slate-500">3 Courts • 4 Rounds of 12-min games • Guaranteed mixed rotations</p>
            </div>
            <button onclick="generatePickleball()" class="text-xs font-semibold px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg">Re-Shuffle</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      `;

      for (let round = 1; round <= 3; round++) {
        const shuffledW = [...women].sort(() => Math.random() - 0.5);
        const shuffledM = [...men].sort(() => Math.random() - 0.5);

        html += `
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <div class="flex justify-between items-center font-bold text-xs text-indigo-600 uppercase tracking-wider">
              <span>Round ${round}</span>
              <span class="text-slate-400 font-normal">15 Minutes</span>
            </div>
            <div class="space-y-2 text-xs">
              <div class="p-2.5 rounded-lg bg-white border border-slate-200 flex justify-between items-center">
                <span class="font-semibold text-emerald-700">Court 1:</span>
                <span>${shuffledW[0] || 'W1'} & ${shuffledM[0] || 'M1'} <b class="text-slate-400">VS</b> ${shuffledW[1] || 'W2'} & ${shuffledM[1] || 'M2'}</span>
              </div>
              <div class="p-2.5 rounded-lg bg-white border border-slate-200 flex justify-between items-center">
                <span class="font-semibold text-emerald-700">Court 2:</span>
                <span>${shuffledW[2] || 'W3'} & ${shuffledM[2] || 'M3'} <b class="text-slate-400">VS</b> ${shuffledW[3] || 'W4'} & ${shuffledM[3] || 'M4'}</span>
              </div>
              <div class="p-2.5 rounded-lg bg-white border border-slate-200 flex justify-between items-center">
                <span class="font-semibold text-emerald-700">Court 3:</span>
                <span>${shuffledW[4] || 'W5'} & ${shuffledM[4] || 'M5'} <b class="text-slate-400">VS</b> ${shuffledW[5] || 'W6'} & ${shuffledM[5] || 'M6'}</span>
              </div>
              <div class="p-2 rounded-lg bg-amber-50 text-amber-800 border border-amber-100 flex items-center justify-between text-[11px]">
                <span class="font-semibold">☕ Social Lounge:</span>
                <span>${(shuffledW.slice(6,8).concat(shuffledM.slice(6,8))).join(', ') || 'Resting players'}</span>
              </div>
            </div>
          </div>
        `;
      }

      html += `</div></div>`;
      document.getElementById('rotationOutput').innerHTML = html;
    }

    function generateStations(title) {
      const women = appData.guests.filter(g => g.gender === 'female').map(g => g.name);
      const men = appData.guests.filter(g => g.gender === 'male').map(g => g.name);

      const shuffledW = [...women].sort(() => Math.random() - 0.5);
      const shuffledM = [...men].sort(() => Math.random() - 0.5);

      let html = `
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div class="flex justify-between items-center border-b pb-4">
            <div>
              <h3 class="font-bold text-slate-800 text-lg">🍽️ ${title}</h3>
              <p class="text-xs text-slate-500">4 Balanced Groups (5 Guests per Station: 2-3 Men + 2-3 Women)</p>
            </div>
            <button onclick="generateStations('${title}')" class="text-xs font-semibold px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg">Re-Shuffle Teams</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      `;

      for (let s = 1; s <= 4; s++) {
        const teamMembers = [
          shuffledW[(s-1)*2] || `W${(s-1)*2+1}`,
          shuffledW[(s-1)*2+1] || `W${(s-1)*2+2}`,
          shuffledM[(s-1)*2] || `M${(s-1)*2+1}`,
          shuffledM[(s-1)*2+1] || `M${(s-1)*2+2}`,
          (s <= 2 ? shuffledW[8 + (s-1)] : shuffledM[8 + (s-3)]) || `Guest 5`
        ];

        html += `
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
            <h4 class="font-bold text-xs text-indigo-600 uppercase tracking-wider">Station / Team ${s}</h4>
            <ul class="space-y-1.5 text-xs text-slate-700">
              ${teamMembers.map(m => `<li class="flex items-center gap-2 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200 font-medium"><span>👤</span> ${m}</li>`).join('')}
            </ul>
          </div>
        `;
      }

      html += `</div></div>`;
      document.getElementById('rotationOutput').innerHTML = html;
    }

    function renderMatchmakerOptions() {
      const select = document.getElementById('matchGuestSelect');
      select.innerHTML = '<option value="">-- Choose a guest --</option>';
      appData.guests.forEach(g => {
        const opt = document.createElement('option');
        opt.value = g.id;
        opt.innerText = `${g.name} (${g.gender === 'female' ? 'Woman' : 'Man'})`;
        select.appendChild(opt);
      });
    }

    function loadGuestPicks() {
      const currentGuestId = document.getElementById('matchGuestSelect').value;
      const targetContainer = document.getElementById('targetPicksList');
      targetContainer.innerHTML = '';
      if (!currentGuestId) return;

      const currentGuest = appData.guests.find(g => g.id === currentGuestId);
      const oppositeGender = currentGuest.gender === 'female' ? 'male' : 'female';
      const potentialMatches = appData.guests.filter(g => g.gender === oppositeGender);
      const existingPicks = appData.interests[currentGuestId] || [];

      potentialMatches.forEach(target => {
        const isChecked = existingPicks.includes(target.id);
        const label = document.createElement('label');
        label.className = "flex items-center gap-2 p-1.5 hover:bg-white rounded cursor-pointer";
        label.innerHTML = `
          <input type="checkbox" value="${target.id}" ${isChecked ? 'checked' : ''} class="rounded text-indigo-600 match-checkbox">
          <span class="text-xs font-medium text-slate-700">${target.name} (${target.notes || 'No notes'})</span>
        `;
        targetContainer.appendChild(label);
      });
    }

    async function savePicks() {
      const currentGuestId = document.getElementById('matchGuestSelect').value;
      if (!currentGuestId) {
        alert("Please select a guest first.");
        return;
      }
      const checkboxes = document.querySelectorAll('.match-checkbox:checked');
      const selectedIds = Array.from(checkboxes).map(cb => cb.value);
      if (!appData.interests) appData.interests = {};
      appData.interests[currentGuestId] = selectedIds;
      await saveAndRefresh();
      alert("Picks saved privately!");
    }

    function calculateMatches() {
      const listContainer = document.getElementById('mutualMatchesList');
      listContainer.innerHTML = '';
      const interests = appData.interests || {};
      const matches = [];

      const guestMap = {};
      appData.guests.forEach(g => guestMap[g.id] = g);

      Object.keys(interests).forEach(personAId => {
        const picksA = interests[personAId] || [];
        picksA.forEach(personBId => {
          const picksB = interests[personBId] || [];
          if (picksB.includes(personAId) && personAId < personBId) {
            matches.push([guestMap[personAId], guestMap[personBId]]);
          }
        });
      });

      document.getElementById('matchCountBadge').innerText = `${matches.length} Matches Found`;

      if (matches.length === 0) {
        listContainer.innerHTML = `<p class="text-xs text-slate-400 italic">No mutual matches calculated yet. Submit picks above to reveal mutual connections.</p>`;
        return;
      }

      matches.forEach(([p1, p2]) => {
        if (p1 && p2) {
          const div = document.createElement('div');
          div.className = "p-3.5 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl flex items-center justify-between";
          div.innerHTML = `
            <div class="flex items-center gap-3">
              <span class="text-xl">💘</span>
              <div>
                <div class="text-sm font-bold text-emerald-900">${p1.name} & ${p2.name}</div>
                <div class="text-xs text-emerald-700">Mutual match! Both selected each other.</div>
              </div>
            </div>
            <span class="text-xs px-2 py-1 bg-emerald-200 text-emerald-800 rounded-md font-bold">Mutual Match</span>
          `;
          listContainer.appendChild(div);
        }
      });
    }

    async function resetToDefaults() {
      if (confirm("Reset to default 20 guest template?")) {
        await fetch('/api/reset', { method: 'POST' });
        fetchData();
      }
    }

    fetchData();
  </script>
</body>
</html>
"""


class ForumRequestHandler(http.server.BaseHTTPRequestHandler):

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
        elif parsed.path == "/api/data":
            data = load_data()
            self._set_headers("application/json")
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b"{}"

        if parsed.path == "/api/data":
            try:
                new_data = json.loads(post_data.decode("utf-8"))
                save_data(new_data)
                self._set_headers("application/json")
                self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            except Exception as e:
                self.send_error(HTTPStatus.BAD_REQUEST, str(e))

        elif parsed.path == "/api/reset":
            save_data(DEFAULT_DATA)
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"status": "reset"}).encode("utf-8"))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ForumRequestHandler) as httpd:
        print("=" * 60)
        print(f"🎉 Exclusive Dating Forum Web App running at:")
        print(f"👉 http://localhost:{PORT}")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
