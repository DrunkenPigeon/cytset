/* ==========================================================================
   CYTSET - ADVANCED DUOLINGO-STYLE GAMIFIED ENGINE
   - 30-Day Infosec Curriculum (270 Core Questions)
   - Mistake Tracking System (Guaranteed review of failed questions next day)
   - Spaced Repetition (Random review questions from previous days)
   - Web Audio API Sound Synthesizer
   - LocalStorage Persistence
   ========================================================================== */

// Global State
let appState = {
  xp: 0,
  streak: 1,
  hearts: 5,
  completedDays: [],
  mistakes: {}, // { [qId]: { id, day, q, options, correct, explain, failCount, active: true } }
  currentDay: 1,
  currentQueue: [], // Array of question objects for today's session
  stepIndex: 'theory', // 'theory' | number (index in currentQueue)
  selectedOption: null,
  isAnswerChecked: false
};

// ==========================================================================
// Web Audio API Sound Synthesizer
// ==========================================================================
let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playTone(freq, type, duration, delay = 0) {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);

    gain.gain.setValueAtTime(0.15, ctx.currentTime + delay);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + duration);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(ctx.currentTime + delay);
    osc.stop(ctx.currentTime + delay + duration);
  } catch (e) {
    // Audio restricted before user gesture
  }
}

function playCorrectSound() {
  playTone(523.25, 'sine', 0.15, 0.0);   // C5
  playTone(659.25, 'sine', 0.15, 0.1);   // E5
  playTone(783.99, 'sine', 0.25, 0.2);   // G5
}

function playWrongSound() {
  playTone(180, 'sawtooth', 0.25, 0.0);
  playTone(140, 'sawtooth', 0.35, 0.15);
}

function playCompleteSound() {
  playTone(523.25, 'sine', 0.15, 0.0);
  playTone(659.25, 'sine', 0.15, 0.12);
  playTone(783.99, 'sine', 0.15, 0.24);
  playTone(1046.50, 'sine', 0.4, 0.36); // C6!
}

// ==========================================================================
// LocalStorage Persistence & Mistake Management
// ==========================================================================
function loadState() {
  try {
    const savedXp = localStorage.getItem('cytset_xp');
    const savedStreak = localStorage.getItem('cytset_streak');
    const savedHearts = localStorage.getItem('cytset_hearts');
    const savedCompleted = localStorage.getItem('cytset_completed');
    const savedMistakes = localStorage.getItem('cytset_mistakes');

    if (savedXp !== null) appState.xp = parseInt(savedXp, 10);
    if (savedStreak !== null) appState.streak = parseInt(savedStreak, 10);
    if (savedHearts !== null) appState.hearts = parseInt(savedHearts, 10);
    if (savedCompleted !== null) appState.completedDays = JSON.parse(savedCompleted);
    if (savedMistakes !== null) appState.mistakes = JSON.parse(savedMistakes);
  } catch (e) {
    console.error('Failed to load state', e);
  }
}

function saveState() {
  try {
    localStorage.setItem('cytset_xp', appState.xp);
    localStorage.setItem('cytset_streak', appState.streak);
    localStorage.setItem('cytset_hearts', appState.hearts);
    localStorage.setItem('cytset_completed', JSON.stringify(appState.completedDays));
    localStorage.setItem('cytset_mistakes', JSON.stringify(appState.mistakes));
  } catch (e) {
    console.error('Failed to save state', e);
  }
}

// Get array of currently active (unresolved) mistakes
function getActiveMistakes() {
  return Object.values(appState.mistakes).filter(m => m.active);
}

// Record an incorrect answer into the mistake bank
function recordMistake(qItem) {
  const qId = qItem.id;
  if (!appState.mistakes[qId]) {
    appState.mistakes[qId] = {
      id: qId,
      day: qItem.day,
      q: qItem.q,
      options: qItem.options,
      correct: qItem.correct,
      explain: qItem.explain,
      failCount: 1,
      active: true,
      lastFailedAt: Date.now()
    };
  } else {
    appState.mistakes[qId].failCount++;
    appState.mistakes[qId].active = true;
    appState.mistakes[qId].lastFailedAt = Date.now();
  }
  saveState();
}

// Resolve a mistake after a correct answer
function resolveMistake(qId) {
  if (appState.mistakes[qId]) {
    appState.mistakes[qId].active = false;
    appState.mistakes[qId].resolvedAt = Date.now();
    saveState();
  }
}

function updateHeaderStats() {
  const xpEl = document.getElementById('stat-xp-val');
  const streakEl = document.getElementById('stat-streak-val');
  const heartsEl = document.getElementById('stat-hearts-val');
  const mistakesEl = document.getElementById('stat-mistakes-val');

  if (xpEl) xpEl.textContent = appState.xp;
  if (streakEl) streakEl.textContent = appState.streak;
  if (heartsEl) heartsEl.textContent = appState.hearts;
  if (mistakesEl) mistakesEl.textContent = getActiveMistakes().length;
}

// Milestone section titles
const SECTION_BANNERS = {
  1: { title: "Неделя 1: Web Application Security", desc: "SQLi, AST, SSRF, Cloud IMDSv2, Race Conditions & HTTP/2" },
  8: { title: "Неделя 2: Сети и протоколы (L2–L7)", desc: "OSI, ARP Spoofing, DAI, TCP сканирования, OS Fingerprinting & DNS" },
  15: { title: "Неделя 3: Linux & Host Security", desc: "Capabilities, Docker Escapes, SUID, glibc AT_SECURE & Cgroups" },
  22: { title: "Неделя 4: Active Directory & Enterprise", desc: "Kerberos V5, PAC, Kerberoasting, NTLM Relay & AD CS ESC1" },
  29: { title: "Финал: Detection Engineering & DFIR", desc: "Правила Sigma, Sysmon Event IDs, RFC 3227 и Экзамен!" }
};

// ==========================================================================
// Dynamic Queue Generator (Current 9 + Mistakes + Spaced Repetition)
// ==========================================================================
function buildDailyQueue(dayNumber) {
  const lesson = LESSONS_DATA.find(l => l.day === dayNumber);
  if (!lesson) return [];

  const queue = [];

  // 1. БЛОК ОШИБОК: Все не закрытые ошибки из прошлых дней (гарантированно!)
  const pendingMistakes = getActiveMistakes();
  pendingMistakes.forEach(m => {
    queue.push({
      ...m,
      queueType: 'mistake', // ⚠️ Работа над ошибками
      originDay: m.day
    });
  });

  // 2. БЛОК ДНЯ: 9 обязательных новых вопросов текущего дня
  lesson.questions.forEach(q => {
    // Avoid immediate duplicate if this exact question was already added from mistakes
    if (!queue.some(item => item.id === q.id)) {
      queue.push({
        ...q,
        queueType: 'current', // ⚡ Тема дня
        originDay: dayNumber
      });
    }
  });

  // 3. БЛОК ИНТЕРВАЛЬНОГО ПОВТОРЕНИЯ: 2-3 случайные задачи из ПРОЙДЕННЫХ дней
  if (dayNumber > 1) {
    const priorQuestions = [];
    LESSONS_DATA.forEach(l => {
      // Pull only from previous days that the user has completed or unlocked
      if (l.day < dayNumber && (appState.completedDays.includes(l.day) || l.day === 1)) {
        l.questions.forEach(pq => {
          if (!queue.some(item => item.id === pq.id)) {
            priorQuestions.push(pq);
          }
        });
      }
    });

    // Pick 2-3 random questions
    const numRandom = Math.min(3, priorQuestions.length);
    // Fisher-Yates shuffle
    for (let i = priorQuestions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [priorQuestions[i], priorQuestions[j]] = [priorQuestions[j], priorQuestions[i]];
    }

    for (let i = 0; i < numRandom; i++) {
      queue.push({
        ...priorQuestions[i],
        queueType: 'review', // 🎲 Интервальное повторение
        originDay: priorQuestions[i].day
      });
    }
  }

  return queue;
}

// ==========================================================================
// Render Roadmap (30 Days)
// ==========================================================================
function renderRoadmap() {
  const container = document.getElementById('roadmap-path');
  if (!container) return;
  container.innerHTML = '';

  const maxCompleted = appState.completedDays.length > 0 
    ? Math.max(...appState.completedDays) 
    : 0;

  const shifts = ['shift-center', 'shift-left', 'shift-center', 'shift-right'];

  LESSONS_DATA.forEach((lesson, index) => {
    const day = lesson.day;

    if (SECTION_BANNERS[day]) {
      const banner = document.createElement('div');
      banner.className = 'section-banner';
      banner.innerHTML = `
        <div class="section-info">
          <h3>${SECTION_BANNERS[day].title}</h3>
          <p>${SECTION_BANNERS[day].desc}</p>
        </div>
        <span class="section-badge">${lesson.badge}</span>
      `;
      container.appendChild(banner);
    }

    const nodeWrap = document.createElement('div');
    const shiftClass = shifts[index % shifts.length];
    nodeWrap.className = `day-node-wrap ${shiftClass}`;

    const isCompleted = appState.completedDays.includes(day);
    const isUnlocked = day === 1 || isCompleted || day <= (maxCompleted + 1);

    if (isCompleted) {
      nodeWrap.classList.add('completed');
    } else if (isUnlocked) {
      nodeWrap.classList.add('active');
    } else {
      nodeWrap.classList.add('locked');
    }

    const btn = document.createElement('button');
    btn.className = 'day-btn';
    btn.setAttribute('aria-label', lesson.title);

    if (isCompleted) {
      btn.innerHTML = '✓';
    } else if (isUnlocked) {
      btn.innerHTML = '⭐';
    } else {
      btn.innerHTML = '🔒';
    }

    btn.addEventListener('click', () => {
      if (!isUnlocked) {
        btn.style.animation = 'shake 0.3s ease';
        setTimeout(() => btn.style.animation = '', 300);
        return;
      }
      openLesson(day);
    });

    const label = document.createElement('div');
    label.className = 'day-label';
    label.textContent = `День ${day}`;

    nodeWrap.appendChild(btn);
    nodeWrap.appendChild(label);
    container.appendChild(nodeWrap);
  });
}

// ==========================================================================
// Lesson Flow & Quiz Runner
// ==========================================================================
function openLesson(dayNumber) {
  appState.currentDay = dayNumber;
  appState.currentQueue = buildDailyQueue(dayNumber);
  appState.stepIndex = 'theory';
  appState.selectedOption = null;
  appState.isAnswerChecked = false;

  const screen = document.getElementById('lesson-screen');
  screen.classList.add('active');

  renderLessonStep();
}

function renderLessonStep() {
  const lesson = LESSONS_DATA.find(l => l.day === appState.currentDay);
  if (!lesson) return;

  const content = document.getElementById('lesson-content');
  const footerBtn = document.getElementById('lesson-action-btn');
  const progressBar = document.getElementById('lesson-progress-fill');
  const drawer = document.getElementById('feedback-drawer');

  drawer.className = 'feedback-drawer';

  const queue = appState.currentQueue;
  const totalSteps = queue.length;

  if (appState.stepIndex === 'theory') {
    // 1. THEORY SCREEN
    progressBar.style.width = '8%';
    const mistakeCount = queue.filter(q => q.queueType === 'mistake').length;
    const reviewCount = queue.filter(q => q.queueType === 'review').length;

    let queueAlertText = `Теория на сегодня (⏱️ 5 минут). Впереди 9 новых заданий`;
    if (mistakeCount > 0) {
      queueAlertText += ` + ⚠️ <b>${mistakeCount} ошибки прошлых дней</b>`;
    }
    if (reviewCount > 0) {
      queueAlertText += ` + 🎲 <b>${reviewCount} задачи на повторение</b>`;
    }
    queueAlertText += `!`;

    content.innerHTML = `
      <div class="owl-bubble-wrap">
        <img src="icon.png" class="owl-mascot-img" alt="Cytset Owl">
        <div class="speech-bubble">
          ${queueAlertText}
        </div>
      </div>
      <div class="theory-card">
        ${lesson.theory}
      </div>
    `;

    footerBtn.textContent = 'К ЗАДАНИЯМ ➔';
    footerBtn.disabled = false;
    footerBtn.onclick = () => {
      appState.stepIndex = 0; // First question
      renderLessonStep();
    };

  } else if (typeof appState.stepIndex === 'number' && appState.stepIndex < totalSteps) {
    // 2. QUESTION SCREEN
    const qIndex = appState.stepIndex;
    const qData = queue[qIndex];
    appState.selectedOption = null;
    appState.isAnswerChecked = false;

    const progressPct = Math.round(((qIndex + 1) / (totalSteps + 1)) * 100);
    progressBar.style.width = `${progressPct}%`;

    // Dynamic Badge based on Queue Type
    let badgeHtml = '';
    let bubblePrompt = '';
    if (qData.queueType === 'mistake') {
      badgeHtml = `<span class="q-badge badge-mistake">⚠️ РАБОТА НАД ОШИБКАМИ (День ${qData.originDay})</span>`;
      bubblePrompt = `Внимание! Ты ошибся в этом вопросе ранее. Давай закроем эту тему правильно!`;
    } else if (qData.queueType === 'review') {
      badgeHtml = `<span class="q-badge badge-review">🎲 ИНТЕРВАЛЬНОЕ ПОВТОРЕНИЕ (День ${qData.originDay})</span>`;
      bubblePrompt = `Проверка долгосрочной памяти: вспоминаем тему Дня ${qData.originDay}!`;
    } else {
      const currentDayIdx = queue.filter((item, idx) => item.queueType === 'current' && idx <= qIndex).length;
      badgeHtml = `<span class="q-badge badge-current">⚡ ТЕМА ДНЯ (${currentDayIdx} из 9)</span>`;
      bubblePrompt = `Вопрос ${qIndex + 1} из ${totalSteps}: покажи свои знания атаки и защиты!`;
    }

    let optionsHtml = '';
    const letters = ['A', 'B', 'C', 'D'];
    qData.options.forEach((opt, idx) => {
      optionsHtml += `
        <button class="option-btn" data-opt-index="${idx}">
          <span class="option-key">${letters[idx]}</span>
          <span class="option-text">${opt}</span>
        </button>
      `;
    });

    content.innerHTML = `
      <div class="owl-bubble-wrap">
        <img src="icon.png" class="owl-mascot-img" alt="Cytset Owl">
        <div class="speech-bubble">
          ${bubblePrompt}
        </div>
      </div>
      <div class="q-badge-container">
        ${badgeHtml}
      </div>
      <h2 class="question-title">${qData.q}</h2>
      <div class="options-container" id="options-container">
        ${optionsHtml}
      </div>
    `;

    const optionBtns = content.querySelectorAll('.option-btn');
    optionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        if (appState.isAnswerChecked) return;
        optionBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        appState.selectedOption = parseInt(btn.dataset.optIndex, 10);
        footerBtn.disabled = false;
      });
    });

    footerBtn.textContent = 'ПРОВЕРИТЬ';
    footerBtn.disabled = true;
    footerBtn.onclick = () => checkAnswer(qData);
  }
}

// ==========================================================================
// Answer Checking & Feedback
// ==========================================================================
function checkAnswer(qData) {
  if (appState.selectedOption === null || appState.isAnswerChecked) return;

  appState.isAnswerChecked = true;
  const isCorrect = appState.selectedOption === qData.correct;
  const drawer = document.getElementById('feedback-drawer');
  const footerBtn = document.getElementById('drawer-action-btn');

  if (isCorrect) {
    playCorrectSound();
    let bonusXp = 15;

    // If resolving a previously failed mistake, award double XP!
    if (qData.queueType === 'mistake') {
      resolveMistake(qData.id);
      bonusXp = 25;
      drawer.className = 'feedback-drawer correct';
      document.getElementById('drawer-title').textContent = `ОШИБКА ИСПРАВЛЕНА! +${bonusXp} XP 🏆`;
    } else {
      drawer.className = 'feedback-drawer correct';
      document.getElementById('drawer-title').textContent = `ВЕЛИКОЛЕПНО! +${bonusXp} XP`;
    }

    appState.xp += bonusXp;
    document.getElementById('drawer-explain').textContent = qData.explain;
  } else {
    playWrongSound();
    appState.hearts = Math.max(0, appState.hearts - 1);
    
    // Record into mistake tracking system!
    recordMistake(qData);

    drawer.className = 'feedback-drawer wrong';
    document.getElementById('drawer-title').textContent = 'НЕ СОВСЕМ ТАК... (Добавлено в ошибки)';
    document.getElementById('drawer-explain').innerHTML = `
      <b>Правильный ответ:</b> ${qData.options[qData.correct]}<br>
      <span style="font-size: 13.5px; opacity: 0.95; line-height: 1.5; display: block; margin-top: 6px;">${qData.explain}</span>
    `;
  }

  saveState();
  updateHeaderStats();

  footerBtn.onclick = () => {
    drawer.className = 'feedback-drawer';
    if (appState.stepIndex + 1 < appState.currentQueue.length) {
      appState.stepIndex++;
      renderLessonStep();
    } else {
      finishLesson();
    }
  };
}

// ==========================================================================
// Finish Lesson
// ==========================================================================
function finishLesson() {
  playCompleteSound();

  if (!appState.completedDays.includes(appState.currentDay)) {
    appState.completedDays.push(appState.currentDay);
    appState.xp += 100; // Completion bonus
    appState.streak += 1;
  }

  saveState();
  updateHeaderStats();

  const lessonScreen = document.getElementById('lesson-screen');
  lessonScreen.classList.remove('active');

  const celebrate = document.getElementById('celebrate-screen');
  celebrate.classList.add('active');

  const activeMistakes = getActiveMistakes().length;
  document.getElementById('celebrate-xp-val').textContent = '+150 XP';
  document.getElementById('celebrate-streak-val').textContent = `${appState.streak} ДНЕЙ`;

  document.getElementById('celebrate-finish-btn').onclick = () => {
    celebrate.classList.remove('active');
    renderRoadmap();
  };
}

// Exit Lesson Handlers
function exitLessonImmediately() {
  const lessonScreen = document.getElementById('lesson-screen');
  const confirmModal = document.getElementById('confirm-exit-modal');
  const drawer = document.getElementById('feedback-drawer');
  if (confirmModal) confirmModal.classList.remove('active');
  if (lessonScreen) lessonScreen.classList.remove('active');
  if (drawer) drawer.className = 'feedback-drawer';
  renderRoadmap();
}

function promptExitLesson() {
  const lessonScreen = document.getElementById('lesson-screen');
  if (!lessonScreen || !lessonScreen.classList.contains('active')) return;

  // If user is just reading theory (no quiz started yet), exit immediately
  if (appState.stepIndex === 'theory') {
    exitLessonImmediately();
    return;
  }

  // If in the middle of questions, show the custom confirm modal
  const confirmModal = document.getElementById('confirm-exit-modal');
  if (confirmModal) {
    confirmModal.classList.add('active');
  } else {
    exitLessonImmediately();
  }
}

// Android Back Button Handler
window.handleAndroidBack = function() {
  const confirmModal = document.getElementById('confirm-exit-modal');
  if (confirmModal && confirmModal.classList.contains('active')) {
    confirmModal.classList.remove('active');
    return "true";
  }

  const celebrate = document.getElementById('celebrate-screen');
  if (celebrate && celebrate.classList.contains('active')) {
    celebrate.classList.remove('active');
    renderRoadmap();
    return "true";
  }

  const lessonScreen = document.getElementById('lesson-screen');
  if (lessonScreen && lessonScreen.classList.contains('active')) {
    promptExitLesson();
    return "true";
  }

  return "false";
};

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  loadState();
  updateHeaderStats();
  renderRoadmap();

  const closeBtn = document.getElementById('lesson-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      promptExitLesson();
    });
  }

  const stayBtn = document.getElementById('confirm-stay-btn');
  if (stayBtn) {
    stayBtn.addEventListener('click', () => {
      const confirmModal = document.getElementById('confirm-exit-modal');
      if (confirmModal) confirmModal.classList.remove('active');
    });
  }

  const leaveBtn = document.getElementById('confirm-leave-btn');
  if (leaveBtn) {
    leaveBtn.addEventListener('click', () => {
      exitLessonImmediately();
    });
  }
});

