/**
 * KINDRED — APPLICATION JAVASCRIPT
 * Interactive questionnaire, archetype scoring engine, sound feedback & waitlist system
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==================== STATE ====================
  const state = {
    currentStep: 1,
    totalSteps: 5,
    soundEnabled: true,
    answers: {
      step1: null,
      step2Burnout: 8,
      step3: null,
      step4Topics: [],
      step5: null
    },
    scores: {
      candid: 0,
      conversationalist: 0,
      romantic: 0,
      realist: 0
    },
    claimed: false,
    ticketNumber: 'KND-' + Math.floor(1000 + Math.random() * 9000),
    waitlistRank: Math.floor(750 + Math.random() * 200)
  };

  // ==================== AUDIO SYNTHESIZER (Web Audio API) ====================
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  function playSound(type) {
    if (!state.soundEnabled) return;
    initAudio();
    if (!audioCtx) return;

    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'click') {
      // Crisp, subtle wooden tap
      osc.type = 'sine';
      osc.frequency.setValueAtTime(420, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.04);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
      osc.start(now);
      osc.stop(now + 0.04);
    } else if (type === 'select') {
      // Gentle warm blip
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(540, now + 0.06);
      gain.gain.setValueAtTime(0.07, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
      osc.start(now);
      osc.stop(now + 0.06);
    } else if (type === 'celebrate') {
      // Harmonious pleasant chime
      const freqs = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      freqs.forEach((freq, idx) => {
        const chordOsc = audioCtx.createOscillator();
        const chordGain = audioCtx.createGain();
        chordOsc.type = 'sine';
        chordOsc.frequency.setValueAtTime(freq, now + idx * 0.08);
        chordGain.gain.setValueAtTime(0.06, now + idx * 0.08);
        chordGain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.45);
        chordOsc.connect(chordGain);
        chordGain.connect(audioCtx.destination);
        chordOsc.start(now + idx * 0.08);
        chordOsc.stop(now + idx * 0.08 + 0.45);
      });
    }
  }

  // ==================== DOM ELEMENTS ====================
  // Screens
  const heroScreen = document.getElementById('hero-screen');
  const quizScreen = document.getElementById('quiz-screen');
  const loadingScreen = document.getElementById('loading-screen');
  const resultsScreen = document.getElementById('results-screen');

  // Navigation & Buttons
  const headerStartBtn = document.getElementById('header-start-btn');
  const heroStartBtn = document.getElementById('hero-start-btn');
  const sectionQuizBtn = document.getElementById('section-quiz-btn');
  const brandHomeBtn = document.getElementById('brand-home-btn');
  const soundToggleBtn = document.getElementById('sound-toggle-btn');
  const soundIcon = document.getElementById('sound-icon');
  const soundText = soundToggleBtn.querySelector('.sound-text');

  // Quiz Navigation
  const quizBackBtn = document.getElementById('quiz-back-btn');
  const skipQuizBtn = document.getElementById('skip-quiz-btn');
  const progressFill = document.getElementById('progress-fill');
  const stepCounterText = document.getElementById('step-counter-text');
  const progressPercentText = document.getElementById('progress-percent-text');
  const questionSlides = document.querySelectorAll('.question-slide');

  // Step 2 Slider
  const burnoutSlider = document.getElementById('burnout-slider');
  const sliderValDisplay = document.getElementById('slider-val-display');
  const sliderEmojiDisplay = document.getElementById('slider-emoji-display');
  const sliderStatusText = document.getElementById('slider-status-text');
  const sliderContinueBtn = document.getElementById('slider-continue-btn');

  // Step 4 Chips
  const topicChips = document.querySelectorAll('.chip-btn');
  const chipCountText = document.getElementById('chip-count-text');
  const chipsContinueBtn = document.getElementById('chips-continue-btn');

  // Results & Pass
  const ticketNumberDisplay = document.getElementById('ticket-number-display');
  const ticketHolderDisplay = document.getElementById('ticket-holder-display');
  const personaAvatarIcon = document.getElementById('persona-avatar-icon');
  const personaNameText = document.getElementById('persona-name-text');
  const personaTaglineText = document.getElementById('persona-tagline-text');
  const personaSuperpowerText = document.getElementById('persona-superpower-text');
  const personaKryptoniteText = document.getElementById('persona-kryptonite-text');
  const personaMatchText = document.getElementById('persona-match-text');

  // Waitlist Form
  const waitlistForm = document.getElementById('waitlist-form');
  const userNameInput = document.getElementById('user-name-input');
  const userEmailInput = document.getElementById('user-email-input');
  const waitlistFormContainer = document.getElementById('waitlist-form-container');
  const claimedSuccessContainer = document.getElementById('claimed-success-container');
  const confirmedRank = document.getElementById('confirmed-rank');
  const referralLinkInput = document.getElementById('referral-link-input');
  const copyRefBtn = document.getElementById('copy-ref-btn');
  const copyHint = document.getElementById('copy-hint');
  const shareTwitterBtn = document.getElementById('share-twitter-btn');
  const shareWhatsappBtn = document.getElementById('share-whatsapp-btn');

  // Top Nav Scroll Buttons
  const navManifestoBtn = document.getElementById('nav-manifesto-btn');
  const navCommunityBtn = document.getElementById('nav-community-btn');
  const navFaqBtn = document.getElementById('nav-faq-btn');

  // ==================== INITIALIZATION ====================
  ticketNumberDisplay.textContent = '#' + state.ticketNumber;

  // ==================== SCREEN SWITCHING ====================
  function showScreen(screen) {
    [heroScreen, quizScreen, loadingScreen, resultsScreen].forEach(s => s.classList.remove('active'));
    screen.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function startQuiz() {
    playSound('click');
    showScreen(quizScreen);
    state.currentStep = 1;
    updateQuizStep();
  }

  heroStartBtn.addEventListener('click', startQuiz);
  headerStartBtn.addEventListener('click', startQuiz);
  sectionQuizBtn.addEventListener('click', startQuiz);

  brandHomeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    playSound('click');
    showScreen(heroScreen);
  });

  // Nav Scrolls
  navManifestoBtn.addEventListener('click', () => {
    playSound('click');
    showScreen(heroScreen);
    document.getElementById('manifesto-section').scrollIntoView({ behavior: 'smooth' });
  });

  navCommunityBtn.addEventListener('click', () => {
    playSound('click');
    showScreen(heroScreen);
    document.getElementById('community-section').scrollIntoView({ behavior: 'smooth' });
  });

  navFaqBtn.addEventListener('click', () => {
    playSound('click');
    showScreen(heroScreen);
    document.getElementById('faq-section').scrollIntoView({ behavior: 'smooth' });
  });

  // ==================== SOUND TOGGLE ====================
  soundToggleBtn.addEventListener('click', () => {
    state.soundEnabled = !state.soundEnabled;
    if (state.soundEnabled) {
      soundIcon.textContent = '🔊';
      soundText.textContent = 'Sound: On';
      playSound('click');
    } else {
      soundIcon.textContent = '🔇';
      soundText.textContent = 'Sound: Off';
    }
  });

  // ==================== QUIZ PROGRESSION ====================
  function updateQuizStep() {
    // Update Progress Bar
    const progressPercent = Math.round((state.currentStep / state.totalSteps) * 100);
    progressFill.style.width = `${progressPercent}%`;
    progressPercentText.textContent = `${progressPercent}%`;
    stepCounterText.textContent = `Question ${state.currentStep} of ${state.totalSteps}`;

    // Update Back button visibility
    quizBackBtn.style.visibility = state.currentStep === 1 ? 'hidden' : 'visible';

    // Show current slide
    questionSlides.forEach(slide => {
      const step = parseInt(slide.dataset.step, 10);
      slide.classList.toggle('active', step === state.currentStep);
    });
  }

  function nextStep() {
    if (state.currentStep < state.totalSteps) {
      state.currentStep++;
      updateQuizStep();
    } else {
      finishQuiz();
    }
  }

  function prevStep() {
    if (state.currentStep > 1) {
      playSound('click');
      state.currentStep--;
      updateQuizStep();
    }
  }

  quizBackBtn.addEventListener('click', prevStep);
  skipQuizBtn.addEventListener('click', () => {
    playSound('click');
    finishQuiz();
  });

  // ==================== STEP 1, 3, 5: SINGLE SELECT OPTION BUTTONS ====================
  const optionButtons = document.querySelectorAll('.option-btn');
  optionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      playSound('select');
      const slide = btn.closest('.question-slide');
      const step = parseInt(slide.dataset.step, 10);
      const archetype = btn.dataset.archetype;
      const val = btn.dataset.value;

      // Unselect siblings
      slide.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');

      // Record answer
      if (archetype && state.scores[archetype] !== undefined) {
        state.scores[archetype] += 2;
      }

      if (step === 1) state.answers.step1 = val;
      if (step === 3) state.answers.step3 = val;
      if (step === 5) state.answers.step5 = val;

      // Auto advance after slight delay for tactile feedback
      setTimeout(() => {
        nextStep();
      }, 260);
    });
  });

  // ==================== STEP 2: BURNOUT SLIDER ====================
  const burnoutFeedback = {
    1: { emoji: '😌', text: '"Cruising peacefully, no rush"' },
    2: { emoji: '🙂', text: '"Slightly skeptical, but giving it a shot"' },
    3: { emoji: '🧐', text: '"Swiping occasionally on Sunday nights"' },
    4: { emoji: '😐', text: '"Conversations fizzle out way too quickly"' },
    5: { emoji: '😮‍💨', text: '"50% pen-pals, 50% dead ends"' },
    6: { emoji: '🤦', text: '"Tired of reciting the exact same bio trivia"' },
    7: { emoji: '🫠', text: '"Actively deleting and reinstalling apps weekly"' },
    8: { emoji: '🤦‍♂️', text: '"Ready to throw my phone into the nearest ocean"' },
    9: { emoji: '💀', text: '"Swiping feels like an unpaid data entry shift"' },
    10: { emoji: '🔥', text: '"Burn the algorithmic apps to the ground"' }
  };

  burnoutSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value, 10);
    state.answers.step2Burnout = val;
    sliderValDisplay.textContent = val;
    
    if (burnoutFeedback[val]) {
      sliderEmojiDisplay.textContent = burnoutFeedback[val].emoji;
      sliderStatusText.textContent = burnoutFeedback[val].text;
    }

    if (val >= 7) state.scores.realist += 1;
    else if (val >= 4) state.scores.candid += 1;
    else state.scores.conversationalist += 1;
  });

  sliderContinueBtn.addEventListener('click', () => {
    playSound('click');
    nextStep();
  });

  // ==================== STEP 4: TOPICS CHIPS MULTI-SELECT ====================
  topicChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const topic = chip.dataset.topic;
      const isSelected = chip.classList.contains('selected');

      if (isSelected) {
        playSound('click');
        chip.classList.remove('selected');
        state.answers.step4Topics = state.answers.step4Topics.filter(t => t !== topic);
      } else {
        if (state.answers.step4Topics.length < 3) {
          playSound('select');
          chip.classList.add('selected');
          state.answers.step4Topics.push(topic);
        } else {
          // Visual shake hint if trying to select more than 3
          chip.style.transform = 'translateX(4px)';
          setTimeout(() => { chip.style.transform = 'none'; }, 100);
        }
      }

      // Update count & button state
      const count = state.answers.step4Topics.length;
      chipCountText.textContent = count;
      chipsContinueBtn.disabled = count === 0;
    });
  });

  chipsContinueBtn.addEventListener('click', () => {
    playSound('click');
    nextStep();
  });

  // ==================== KEYBOARD SHORTCUTS ====================
  document.addEventListener('keydown', (e) => {
    // Only handle if in quiz screen
    if (!quizScreen.classList.contains('active')) {
      if (heroScreen.classList.contains('active') && e.key === 'Enter') {
        startQuiz();
      }
      return;
    }

    // A, B, C, D keyboard selection for slides 1, 3, 5
    if (state.currentStep === 1 || state.currentStep === 3 || state.currentStep === 5) {
      const currentSlide = document.querySelector(`.question-slide[data-step="${state.currentStep}"]`);
      if (currentSlide) {
        const keyMap = { 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', '1': 'A', '2': 'B', '3': 'C', '4': 'D' };
        const mapped = keyMap[e.key.toLowerCase()];
        if (mapped) {
          const targetBtn = currentSlide.querySelector(`.option-btn[data-key="${mapped}"]`);
          if (targetBtn) {
            targetBtn.click();
          }
        }
      }
    } else if (state.currentStep === 2 && e.key === 'Enter') {
      sliderContinueBtn.click();
    } else if (state.currentStep === 4 && e.key === 'Enter' && !chipsContinueBtn.disabled) {
      chipsContinueBtn.click();
    }
  });

  // ==================== FINISH QUIZ & ARCHETYPE SYNTHESIS ====================
  const archetypes = {
    conversationalist: {
      name: 'The Candid Conversationalist',
      avatar: '⚡',
      tagline: '"Values razor-sharp wit, 2am philosophical deep dives, and zero tolerance for polite small talk."',
      superpower: 'Instant Chemistry Detection',
      kryptonite: '"K" & 3-word replies',
      match: 'The Thoughtful Romantic',
      dna: { depth: 96, banter: 94, bsTolerance: 12 }
    },
    romantic: {
      name: 'The Intentional Romantic',
      avatar: '🍷',
      tagline: '"Believes chemistry is built through genuine vulnerability, intentional courtship, and true emotional presence."',
      superpower: 'Emotional Resonance & Attunement',
      kryptonite: 'Ambiguous "hangouts" & breadcrumbing',
      match: 'The Candid Conversationalist',
      dna: { depth: 98, banter: 84, bsTolerance: 18 }
    },
    candid: {
      name: 'The Radical Truth-Teller',
      avatar: '🎯',
      tagline: '"Prefers brutal honesty with warmth over polite ambiguity. Ready for real people with clear intentions."',
      superpower: 'Zero-BS Filter & Authenticity',
      kryptonite: 'Three-day texting games',
      match: 'The Curious Realist',
      dna: { depth: 90, banter: 88, bsTolerance: 6 }
    },
    realist: {
      name: 'The Curious Realist',
      avatar: '🪐',
      tagline: '"Approaches connection with grounded curiosity, looking for shared intellectual interests and genuine mutual effort."',
      superpower: 'High-Signal Compatibility Radar',
      kryptonite: 'Pretentious resume talk',
      match: 'The Radical Truth-Teller',
      dna: { depth: 92, banter: 86, bsTolerance: 15 }
    }
  };

  function calculateArchetype() {
    let topType = 'conversationalist';
    let highestScore = -1;

    for (const [type, score] of Object.entries(state.scores)) {
      if (score > highestScore) {
        highestScore = score;
        topType = type;
      }
    }
    return archetypes[topType] || archetypes.conversationalist;
  }

  function finishQuiz() {
    showScreen(loadingScreen);

    const loaderStatus = document.getElementById('loader-status-text');
    const loaderSub = document.getElementById('loader-sub-text');
    const loaderBar = document.getElementById('loader-bar-fill');

    // Smooth simulated progression steps
    setTimeout(() => {
      loaderBar.style.width = '35%';
      loaderStatus.textContent = 'Decoding your conversation rhythm...';
      loaderSub.textContent = 'Comparing against 2,480+ member responses';
    }, 400);

    setTimeout(() => {
      loaderBar.style.width = '75%';
      loaderStatus.textContent = 'Calibrating forum compatibility...';
      loaderSub.textContent = 'Generating your VIP Founding Member Pass';
    }, 1100);

    setTimeout(() => {
      loaderBar.style.width = '100%';
      renderResults();
    }, 1800);
  }

  function renderResults() {
    const persona = calculateArchetype();

    // Populate Persona Details
    personaAvatarIcon.textContent = persona.avatar;
    personaNameText.textContent = persona.name;
    personaTaglineText.textContent = persona.tagline;
    personaSuperpowerText.textContent = persona.superpower;
    personaKryptoniteText.textContent = persona.kryptonite;
    personaMatchText.textContent = persona.match;

    // Show Results Screen
    showScreen(resultsScreen);
    playSound('celebrate');

    // Confetti effect
    if (typeof confetti === 'function') {
      confetti({
        particleCount: 60,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#C85A32', '#3D6B52', '#C27803', '#FAF7F2']
      });
    }
  }

  // ==================== WAITLIST FORM SUBMIT ====================
  waitlistForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = userNameInput.value.trim() || 'Founding Member';
    const email = userEmailInput.value.trim();

    if (!email) return;

    // Update Ticket UI live
    ticketHolderDisplay.textContent = name;
    confirmedRank.textContent = state.waitlistRank;
    referralLinkInput.value = `https://kindred.dating/join?ref=${state.ticketNumber.toLowerCase()}`;

    // Switch form to claimed state
    waitlistFormContainer.classList.add('hidden');
    claimedSuccessContainer.classList.remove('hidden');
    state.claimed = true;

    playSound('celebrate');

    // Big celebration confetti shower
    if (typeof confetti === 'function') {
      confetti({
        particleCount: 120,
        spread: 90,
        origin: { y: 0.5 },
        colors: ['#C85A32', '#3D6B52', '#C27803', '#FAF7F2', '#1C1917']
      });
    }
  });

  // Copy Referral Link
  copyRefBtn.addEventListener('click', () => {
    referralLinkInput.select();
    navigator.clipboard.writeText(referralLinkInput.value).then(() => {
      playSound('click');
      copyHint.classList.remove('hidden');
      copyRefBtn.textContent = 'Copied!';
      setTimeout(() => {
        copyHint.classList.add('hidden');
        copyRefBtn.textContent = 'Copy Link';
      }, 2500);
    });
  });

  // Social Sharing
  shareTwitterBtn.addEventListener('click', () => {
    const shareText = encodeURIComponent(`I just unlocked Founding Member Pass #${state.ticketNumber} on Kindred — the candid forum redefining modern dating through real conversation. Check your archetype:`);
    const shareUrl = encodeURIComponent(`https://kindred.dating/join?ref=${state.ticketNumber.toLowerCase()}`);
    window.open(`https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`, '_blank');
  });

  shareWhatsappBtn.addEventListener('click', () => {
    const shareText = encodeURIComponent(`I just took the Kindred Dating Vibe Audit and unlocked Founding Member Pass #${state.ticketNumber}. You should try it: https://kindred.dating/join?ref=${state.ticketNumber.toLowerCase()}`);
    window.open(`https://api.whatsapp.com/send?text=${shareText}`, '_blank');
  });

  // ==================== FORUM POLL INTERACTION ====================
  const pollButtons = document.querySelectorAll('.poll-btn');
  pollButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      playSound('select');
      const pollBox = btn.closest('.poll-buttons');
      pollBox.querySelectorAll('.poll-btn').forEach(b => b.classList.remove('voted'));
      btn.classList.add('voted');
    });
  });

  // ==================== FAQ ACCORDION ====================
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const trigger = item.querySelector('.faq-trigger');
    trigger.addEventListener('click', () => {
      playSound('click');
      const isOpen = item.classList.contains('open');
      
      // Close others for clean accordion
      faqItems.forEach(i => i.classList.remove('open'));
      
      if (!isOpen) {
        item.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
      } else {
        trigger.setAttribute('aria-expanded', 'false');
      }
    });
  });
});
