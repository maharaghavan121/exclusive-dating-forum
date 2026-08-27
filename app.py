#!/usr/bin/env python3
"""
Exclusive Dating Forum – Interactive Planning & Brainstorming Platform
Renders the complete 7-section document layout with interactive tables,
checklists, and live editing.
Zero dependencies: python3 app.py
"""

import http.server
import json
import os
import socketserver
import urllib.parse
from http import HTTPStatus

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

DEFAULT_DATA = {
    "organizer": "Mahalakshmi",
    "target_timeline": "September 2026",
    "status": "Brainstorming & Planning",
    "cohort_size": "20 Guests (10 Women, 10 Men)",
    "overview": {
        "premise": "An intentionally curated, private dating forum bringing together 20 friends (10 women and 10 men) in interactive, low-pressure group settings.",
        "philosophy": "Foster organic connections through shared activities and natural conversation facilitation rather than high-pressure traditional dating setups.",
        "format": "A curated event built around engaging group activities where participants collaborate, compete, and interact in varying group dynamics."
    },
    "guest_list": [
        {"id": "W1", "name": "Sarah J.", "gender": "Female", "connection": "College Friend", "notes": "Foodie, loves cooking, beginner pickleball", "rsvp": "Confirmed"},
        {"id": "W2", "name": "Elena R.", "gender": "Female", "connection": "Work Colleague", "notes": "Outdoor enthusiast, adventurous", "rsvp": "Confirmed"},
        {"id": "W3", "name": "Maya P.", "gender": "Female", "connection": "Mutual Friend (Alex)", "notes": "Product designer, plays tennis", "rsvp": "Confirmed"},
        {"id": "W4", "name": "Chloe T.", "gender": "Female", "connection": "High School Friend", "notes": "Bakes sourdough, super outgoing", "rsvp": "Confirmed"},
        {"id": "W5", "name": "Jessica K.", "gender": "Female", "connection": "Running Club", "notes": "Marathoner, tech PM", "rsvp": "Invited"},
        {"id": "W6", "name": "Amina D.", "gender": "Female", "connection": "Book Club", "notes": "Creative writer, coffee lover", "rsvp": "Invited"},
        {"id": "W7", "name": "Rachel B.", "gender": "Female", "connection": "Mutual Friend (Samir)", "notes": "Architect, loves live music", "rsvp": "Invited"},
        {"id": "W8", "name": "Hannah L.", "gender": "Female", "connection": "Gym Friend", "notes": "Dog mom, great conversationalist", "rsvp": "Invited"},
        {"id": "W9", "name": "Tara M.", "gender": "Female", "connection": "Referred by David", "notes": "Consultant, travels often", "rsvp": "Invited"},
        {"id": "W10", "name": "Nina W.", "gender": "Female", "connection": "College Friend", "notes": "Loves board games & wine nights", "rsvp": "Invited"},
        {"id": "M1", "name": "David K.", "gender": "Male", "connection": "High School Friend", "notes": "Software eng, plays pickleball regularly", "rsvp": "Confirmed"},
        {"id": "M2", "name": "Alex M.", "gender": "Male", "connection": "College Friend", "notes": "Passionate home cook, pizza enthusiast", "rsvp": "Confirmed"},
        {"id": "M3", "name": "Marcus C.", "gender": "Male", "connection": "Gym Buddy", "notes": "Upbeat energy, marathon runner", "rsvp": "Confirmed"},
        {"id": "M4", "name": "Samir G.", "gender": "Male", "connection": "Work Colleague", "notes": "Design director, cocktail enthusiast", "rsvp": "Confirmed"},
        {"id": "M5", "name": "Liam H.", "gender": "Male", "connection": "Music Circle", "notes": "Guitarist & tech consultant", "rsvp": "Invited"},
        {"id": "M6", "name": "Julian B.", "gender": "Male", "connection": "Mutual Friend (Elena)", "notes": "Easygoing, loves hiking & dining out", "rsvp": "Invited"},
        {"id": "M7", "name": "Daniel F.", "gender": "Male", "connection": "Architecture Friend", "notes": "Art & design lover, foodie", "rsvp": "Invited"},
        {"id": "M8", "name": "Rohan S.", "gender": "Male", "connection": "Climbing Gym", "notes": "Startup founder, loves trivia", "rsvp": "Invited"},
        {"id": "M9", "name": "Kevin Z.", "gender": "Male", "connection": "Referred by Marcus", "notes": "Competitive cook, funny vibe", "rsvp": "Invited"},
        {"id": "M10", "name": "Ethan N.", "gender": "Male", "connection": "College Friend", "notes": "Data scientist, craft beer fan", "rsvp": "Invited"}
    ],
    "activities": [
        {
            "name": "Pickleball Social & Tournament",
            "venue": "Local courts / indoor racquet club",
            "structure": "Rotating mixed doubles pairs (1M + 1W)",
            "cost": "$15 – $25 / person",
            "pros": "High energy, fast icebreaker, effortless partner rotations",
            "cons": "Athletic ability differences, weather dependent (if outdoors)"
        },
        {
            "name": "Pizza Making Night",
            "venue": "Home kitchen with outdoor oven / rented culinary studio",
            "structure": "4 prep stations (5 people per station: 2-3M / 2-3W)",
            "cost": "$25 – $35 / person",
            "pros": "Relaxed collaborative cooking, shared family-style meal",
            "cons": "Requires sufficient oven and counter prep space"
        },
        {
            "name": "Cooking Competition (Cook-Off)",
            "venue": "Rented commercial kitchen / large private residence",
            "structure": "4 teams of 5 with mystery ingredient challenge",
            "cost": "$30 – $45 / person",
            "pros": "High team bonding, fun friendly judging and tasting",
            "cons": "More ingredient prep and cleanup coordination"
        }
    ],
    "checklist": [
        {"text": "Event Format Decision: Confirm inaugural activity (Pickleball vs. Pizza vs. Cook-off)", "checked": False},
        {"text": "Date & Venue: Finalize target date, time, and reserve space", "checked": False},
        {"text": "Target Guest List: Send private invites to the 10 women & 10 men + have 2 alternates each", "checked": False},
        {"text": "Budget & Expenses: Determine cost split method (host-covered vs. per-person ticket)", "checked": False},
        {"text": "Post-Event Matchmaking: Decide between double-blind mutual match check-in or shared group directory", "checked": False}
    ]
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
  <title>Exclusive Dating Forum – Planning & Brainstorming</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .doc-container { max-width: 900px; }
  </style>
</head>
<body class="bg-[#f8f9fa] text-slate-800 antialiased min-h-screen py-10 px-4">

  <!-- Main Document Container -->
  <div class="doc-container mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-8 sm:p-14 space-y-10">

    <!-- Header / Title Block -->
    <div class="border-b border-slate-100 pb-8 space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <span class="px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-100">
          Planning & Brainstorming Framework
        </span>
        <button onclick="saveAll()" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition flex items-center gap-2">
          <span>💾 Save All Changes</span>
        </button>
      </div>

      <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
        Exclusive Dating Forum – Planning & Brainstorming
      </h1>

      <!-- Metadata Line -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2 text-xs text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-100">
        <div>
          <span class="font-bold text-slate-400 block uppercase text-[10px]">Organizer</span>
          <input type="text" id="metaOrganizer" class="bg-transparent font-semibold text-slate-800 focus:outline-none w-full">
        </div>
        <div>
          <span class="font-bold text-slate-400 block uppercase text-[10px]">Target Timeline</span>
          <input type="text" id="metaTimeline" class="bg-transparent font-semibold text-slate-800 focus:outline-none w-full">
        </div>
        <div>
          <span class="font-bold text-slate-400 block uppercase text-[10px]">Status</span>
          <span class="font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">Brainstorming</span>
        </div>
        <div>
          <span class="font-bold text-slate-400 block uppercase text-[10px]">Cohort Size</span>
          <span class="font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">20 (10W / 10M)</span>
        </div>
      </div>
    </div>

    <!-- 1. OVERVIEW & CORE CONCEPT -->
    <section class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">1</span>
        <h2 class="text-xl font-bold text-slate-900">Overview & Core Concept</h2>
      </div>
      
      <div class="bg-indigo-50/50 border border-indigo-100 rounded-xl p-5 space-y-3 text-sm text-slate-700 leading-relaxed">
        <p><strong>• Premise:</strong> An intentionally curated, private dating forum bringing together 20 friends (10 women and 10 men) in interactive, low-pressure group settings.</p>
        <p><strong>• Core Philosophy:</strong> Foster organic connections through shared activities and natural conversation facilitation rather than high-pressure traditional dating setups.</p>
        <p><strong>• Format:</strong> A curated event (or series of events) built around engaging group activities where participants collaborate, compete, and interact in varying group dynamics.</p>
      </div>
    </section>

    <!-- 2. GUEST LIST & COHORT SELECTION -->
    <section class="space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">2</span>
          <h2 class="text-xl font-bold text-slate-900">Guest List Tracker (10 Women / 10 Men)</h2>
        </div>
        <div class="flex gap-2">
          <span id="womenCountBadge" class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-pink-50 text-pink-700 border border-pink-100">0/10 Women</span>
          <span id="menCountBadge" class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-100">0/10 Men</span>
        </div>
      </div>

      <div class="overflow-x-auto border border-slate-200 rounded-xl shadow-sm">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <th class="py-3 px-3 w-10 text-center">#</th>
              <th class="py-3 px-3">Guest Name</th>
              <th class="py-3 px-3 w-20">Gender</th>
              <th class="py-3 px-3">Mutual Connection / Referrer</th>
              <th class="py-3 px-3">Notes & Interests</th>
              <th class="py-3 px-3 w-28">RSVP Status</th>
            </tr>
          </thead>
          <tbody id="guestTableBody" class="divide-y divide-slate-100 text-slate-700">
          </tbody>
        </table>
      </div>
    </section>

    <!-- 3. EVENT SERIES & ACTIVITY FORMATS -->
    <section class="space-y-6">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">3</span>
        <h2 class="text-xl font-bold text-slate-900">Event Series & Activity Formats</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-5 rounded-xl border border-emerald-100 bg-emerald-50/40 space-y-2">
          <div class="text-emerald-700 font-bold text-sm flex items-center gap-2">
            <span>🎾</span> Option A: Pickleball Social
          </div>
          <p class="text-xs text-slate-600"><strong>Format:</strong> Round-robin doubles with partner rotations across rounds.</p>
          <p class="text-xs text-slate-600"><strong>Dynamic:</strong> Fast-paced, high energy, natural icebreaker.</p>
        </div>

        <div class="p-5 rounded-xl border border-amber-100 bg-amber-50/40 space-y-2">
          <div class="text-amber-700 font-bold text-sm flex items-center gap-2">
            <span>🍕</span> Option B: Pizza Making Night
          </div>
          <p class="text-xs text-slate-600"><strong>Format:</strong> Small teams/pairs working together at prep stations making custom pizzas.</p>
          <p class="text-xs text-slate-600"><strong>Dynamic:</strong> Creative, collaborative, hands-on conversation.</p>
        </div>

        <div class="p-5 rounded-xl border border-rose-100 bg-rose-50/40 space-y-2">
          <div class="text-rose-700 font-bold text-sm flex items-center gap-2">
            <span>🍳</span> Option C: Cooking Cook-Off
          </div>
          <p class="text-xs text-slate-600"><strong>Format:</strong> Timed cook-off in teams with mystery ingredients & judging.</p>
          <p class="text-xs text-slate-600"><strong>Dynamic:</strong> High team bonding, friendly competition & tasting.</p>
        </div>
      </div>

      <!-- Activity Comparison Matrix -->
      <div class="overflow-x-auto border border-slate-200 rounded-xl shadow-sm">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <th class="py-3 px-3">Activity Option</th>
              <th class="py-3 px-3">Target Venue Type</th>
              <th class="py-3 px-3">Team Structure</th>
              <th class="py-3 px-3">Est. Cost</th>
              <th class="py-3 px-3">Pros</th>
              <th class="py-3 px-3">Cons / Challenges</th>
            </tr>
          </thead>
          <tbody id="activityTableBody" class="divide-y divide-slate-100 text-slate-700">
          </tbody>
        </table>
      </div>
    </section>

    <!-- 4. CONVERSATION FACILITATION & EVENT FLOW -->
    <section class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">4</span>
        <h2 class="text-xl font-bold text-slate-900">Conversation Facilitation & Event Flow</h2>
      </div>

      <div class="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <th class="py-3 px-3 w-28">Time Window</th>
              <th class="py-3 px-3 w-40">Segment</th>
              <th class="py-3 px-3">Objective & Activity</th>
              <th class="py-3 px-3">Facilitation Notes</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-slate-700">
            <tr>
              <td class="py-3 px-3 font-bold text-indigo-600">0:00 – 0:30</td>
              <td class="py-3 px-3 font-semibold">Welcome & Mingling</td>
              <td class="py-3 px-3">Casual drinks, name tags, arrivals</td>
              <td class="py-3 px-3 text-slate-500">Host welcome speech & setting expectations</td>
            </tr>
            <tr>
              <td class="py-3 px-3 font-bold text-indigo-600">0:30 – 1:30</td>
              <td class="py-3 px-3 font-semibold">Main Activity (Part 1)</td>
              <td class="py-3 px-3">Structured activity / first set of rotations</td>
              <td class="py-3 px-3 text-slate-500">Keep rounds timed and partner transitions smooth</td>
            </tr>
            <tr>
              <td class="py-3 px-3 font-bold text-indigo-600">1:30 – 2:00</td>
              <td class="py-3 px-3 font-semibold">Half-Time / Break</td>
              <td class="py-3 px-3">Food, snacks, casual regrouping</td>
              <td class="py-3 px-3 text-slate-500">Natural conversation pause and drink refill</td>
            </tr>
            <tr>
              <td class="py-3 px-3 font-bold text-indigo-600">2:00 – 3:00</td>
              <td class="py-3 px-3 font-semibold">Main Activity (Part 2)</td>
              <td class="py-3 px-3">Second round / finals / tasting & judging</td>
              <td class="py-3 px-3 text-slate-500">Re-shuffle groups for brand new interactions</td>
            </tr>
            <tr>
              <td class="py-3 px-3 font-bold text-indigo-600">3:00 – End</td>
              <td class="py-3 px-3 font-semibold">Wrap-Up & Open Hangout</td>
              <td class="py-3 px-3">Dessert, drinks, unstructured mingling</td>
              <td class="py-3 px-3 text-slate-500">Zero pressure, voluntary stay</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 5. OPERATIONS & LOGISTICS -->
    <section class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">5</span>
        <h2 class="text-xl font-bold text-slate-900">Operations & Logistics</h2>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-700">
        <div class="bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-2">
          <h3 class="font-bold text-slate-900 text-sm">📍 Venue Planning</h3>
          <p>• <strong>Options:</strong> Private home, rented studio, community court, culinary space.</p>
          <p>• <strong>Capacity:</strong> Comfortable seating for 20, kitchen facilities, sound system, parking.</p>
        </div>
        <div class="bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-2">
          <h3 class="font-bold text-slate-900 text-sm">💵 Budget & Expenses (Est. $400 – $850)</h3>
          <p>• <strong>Venue Rental:</strong> $100 – $300</p>
          <p>• <strong>Food & Drinks:</strong> $250 – $450 ($20 – $40 / person)</p>
          <p>• <strong>Cost Model:</strong> Split evenly or host-subsidized.</p>
        </div>
      </div>
    </section>

    <!-- 6. POST-EVENT FACILITATION -->
    <section class="space-y-4">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">6</span>
        <h2 class="text-xl font-bold text-slate-900">Post-Event Connection Facilitation</h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
          <h4 class="font-bold text-slate-900">Option 1: Double-Blind Mutual Match</h4>
          <p class="text-slate-600">Guests privately text the host the names of people they'd like to see again. Host connects mutual matches.</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
          <h4 class="font-bold text-slate-900">Option 2: Open Group Chat</h4>
          <p class="text-slate-600">Shared group chat / IG directory for everyone to follow up and plan organic meetups.</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
          <h4 class="font-bold text-slate-900">Option 3: Host 1-on-1 Check-In</h4>
          <p class="text-slate-600">Host chats with attendees individually post-event for feedback and warm introductions.</p>
        </div>
      </div>
    </section>

    <!-- 7. BRAINSTORMING SCRATCHPAD & DECISIONS -->
    <section class="space-y-4 border-t border-slate-100 pt-8">
      <div class="flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">7</span>
        <h2 class="text-xl font-bold text-slate-900">Brainstorming Scratchpad & Open Decisions</h2>
      </div>

      <div id="checklistContainer" class="space-y-2 bg-slate-50 p-5 rounded-xl border border-slate-200 text-xs">
      </div>
    </section>

    <!-- Footer -->
    <div class="text-center pt-8 border-t border-slate-100 text-xs text-slate-400">
      Exclusive Dating Forum • 20-Person Planning Framework
    </div>

  </div>

  <script>
    let appData = {};

    async function loadData() {
      const res = await fetch('/api/data');
      appData = await res.json();
      renderPage();
    }

    function renderPage() {
      document.getElementById('metaOrganizer').value = appData.organizer || 'Mahalakshmi';
      document.getElementById('metaTimeline').value = appData.target_timeline || 'September 2026';

      const tbody = document.getElementById('guestTableBody');
      tbody.innerHTML = '';
      let womenConf = 0, menConf = 0;

      appData.guest_list.forEach((g, idx) => {
        if (g.gender === 'Female' && g.rsvp === 'Confirmed') womenConf++;
        if (g.gender === 'Male' && g.rsvp === 'Confirmed') menConf++;

        const tr = document.createElement('tr');
        tr.className = idx % 2 === 0 ? 'bg-white hover:bg-slate-50/80' : 'bg-slate-50/40 hover:bg-slate-50';
        tr.innerHTML = `
          <td class="py-2.5 px-3 text-center font-bold text-slate-400">${g.id}</td>
          <td class="py-2.5 px-3">
            <input type="text" value="${g.name}" onchange="updateGuest(${idx}, 'name', this.value)" class="w-full bg-transparent font-medium text-slate-900 focus:bg-white focus:ring-1 focus:ring-indigo-500 rounded px-1">
          </td>
          <td class="py-2.5 px-3 font-semibold ${g.gender === 'Female' ? 'text-pink-600' : 'text-blue-600'}">${g.gender}</td>
          <td class="py-2.5 px-3">
            <input type="text" value="${g.connection || ''}" onchange="updateGuest(${idx}, 'connection', this.value)" class="w-full bg-transparent text-slate-600 focus:bg-white focus:ring-1 focus:ring-indigo-500 rounded px-1">
          </td>
          <td class="py-2.5 px-3">
            <input type="text" value="${g.notes || ''}" onchange="updateGuest(${idx}, 'notes', this.value)" class="w-full bg-transparent text-slate-500 focus:bg-white focus:ring-1 focus:ring-indigo-500 rounded px-1">
          </td>
          <td class="py-2.5 px-3">
            <select onchange="updateGuest(${idx}, 'rsvp', this.value)" class="text-xs font-semibold rounded-lg px-2 py-1 border border-slate-200 focus:outline-none ${
              g.rsvp === 'Confirmed' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
            }">
              <option value="Confirmed" ${g.rsvp === 'Confirmed' ? 'selected' : ''}>Confirmed</option>
              <option value="Invited" ${g.rsvp === 'Invited' ? 'selected' : ''}>Invited</option>
              <option value="Declined" ${g.rsvp === 'Declined' ? 'selected' : ''}>Declined</option>
            </select>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('womenCountBadge').innerText = `${womenConf}/10 Confirmed Women`;
      document.getElementById('menCountBadge').innerText = `${menConf}/10 Confirmed Men`;

      const actBody = document.getElementById('activityTableBody');
      actBody.innerHTML = '';
      appData.activities.forEach((act, idx) => {
        const tr = document.createElement('tr');
        tr.className = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/40';
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-slate-900">${act.name}</td>
          <td class="py-2.5 px-3 text-slate-600">${act.venue}</td>
          <td class="py-2.5 px-3 text-slate-600">${act.structure}</td>
          <td class="py-2.5 px-3 font-semibold text-emerald-700">${act.cost}</td>
          <td class="py-2.5 px-3 text-emerald-600">${act.pros}</td>
          <td class="py-2.5 px-3 text-rose-600">${act.cons}</td>
        `;
        actBody.appendChild(tr);
      });

      const checkContainer = document.getElementById('checklistContainer');
      checkContainer.innerHTML = '';
      appData.checklist.forEach((item, idx) => {
        const div = document.createElement('label');
        div.className = "flex items-start gap-2.5 cursor-pointer hover:bg-white p-2 rounded-lg transition";
        div.innerHTML = `
          <input type="checkbox" ${item.checked ? 'checked' : ''} onchange="toggleChecklist(${idx}, this.checked)" class="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500">
          <span class="${item.checked ? 'line-through text-slate-400' : 'text-slate-700 font-medium'}">${item.text}</span>
        `;
        checkContainer.appendChild(div);
      });
    }

    function updateGuest(idx, field, val) {
      appData.guest_list[idx][field] = val;
    }

    function toggleChecklist(idx, checked) {
      appData.checklist[idx].checked = checked;
      renderPage();
    }

    async function saveAll() {
      appData.organizer = document.getElementById('metaOrganizer').value;
      appData.target_timeline = document.getElementById('metaTimeline').value;

      await fetch('/api/data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appData)
      });
      alert('All document changes saved successfully!');
      renderPage();
    }

    loadData();
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
        else:
            self.send_error(HTTPStatus.NOT_FOUND)


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ForumRequestHandler) as httpd:
        print("=" * 60)
        print(f"🎉 Exclusive Dating Forum Planning App running at:")
        print(f"👉 http://localhost:{PORT}")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
