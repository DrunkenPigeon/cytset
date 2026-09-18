/* ==========================================================================
   CYBERSECURITY ACADEMY - INTERACTIVE CORE
   Handles:
   - LocalStorage Progress Tracker & Rank calculation
   - Interactive Code Tabs (Vulnerable vs Patched vs Defense)
   - Copy to clipboard
   - Live Search & Role Filtering
   - Collapsible Solutions & Hints
   - Lab Modal Management
   - Interactive Terminal / Quiz Sandbox
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initProgressTracker();
  initCodeTabs();
  initCopyButtons();
  initHintToggles();
  initFilters();
  initSearch();
  initLabModal();
  initTerminalQuiz();
});

/* ==========================================================================
   1. PROGRESS TRACKER & GAMIFIED RANKS
   ========================================================================== */
const STORAGE_KEY = 'cybersec_course_completed_tasks';

function getCompletedTasks() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (e) {
    console.error('Error reading localStorage', e);
    return [];
  }
}

function saveCompletedTasks(tasks) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  } catch (e) {
    console.error('Error writing to localStorage', e);
  }
}

function initProgressTracker() {
  const checkboxes = document.querySelectorAll('.task-checkbox');
  const completedList = getCompletedTasks();

  checkboxes.forEach((cb) => {
    const taskId = cb.dataset.taskId;
    if (completedList.includes(taskId)) {
      cb.checked = true;
      const card = cb.closest('.task-card');
      if (card) card.classList.add('completed');
    }

    cb.addEventListener('change', (e) => {
      const currentCompleted = getCompletedTasks();
      if (e.target.checked) {
        if (!currentCompleted.includes(taskId)) currentCompleted.push(taskId);
        e.target.closest('.task-card')?.classList.add('completed');
      } else {
        const index = currentCompleted.indexOf(taskId);
        if (index > -1) currentCompleted.splice(index, 1);
        e.target.closest('.task-card')?.classList.remove('completed');
      }
      saveCompletedTasks(currentCompleted);
      updateProgressDisplay();
    });
  });

  updateProgressDisplay();
}

function updateProgressDisplay() {
  const checkboxes = document.querySelectorAll('.task-checkbox');
  const total = checkboxes.length;
  const completed = getCompletedTasks().length;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

  // Update Mini Nav Bar
  const fillMini = document.getElementById('progress-fill-mini');
  const textMini = document.getElementById('progress-text-mini');
  const rankBadge = document.getElementById('user-rank-badge');
  const statCompleted = document.getElementById('stat-completed-count');
  const statPercent = document.getElementById('stat-percent-display');

  if (fillMini) fillMini.style.width = `${percent}%`;
  if (textMini) textMini.textContent = `${completed}/${total} (${percent}%)`;
  if (statCompleted) statCompleted.textContent = completed;
  if (statPercent) statPercent.textContent = `${percent}%`;

  // Determine Rank
  let rank = 'Студент СПО';
  let rankColor = 'var(--text-muted)';
  if (percent >= 100) {
    rank = '🏆 Lead Sec Architect';
    rankColor = 'var(--accent-purple)';
  } else if (percent >= 75) {
    rank = '🛡️ Senior SecOps / AppSec';
    rankColor = 'var(--accent-crimson)';
  } else if (percent >= 45) {
    rank = '⚡ Middle Blue/Red Teamer';
    rankColor = 'var(--accent-cyan)';
  } else if (percent >= 15) {
    rank = '🎯 Junior SOC Analyst';
    rankColor = 'var(--accent-emerald)';
  }

  if (rankBadge) {
    rankBadge.textContent = rank;
    rankBadge.style.borderColor = rankColor;
  }
}

/* ==========================================================================
   2. INTERACTIVE CODE TABS
   ========================================================================== */
function initCodeTabs() {
  document.querySelectorAll('.code-viewer').forEach((viewer) => {
    const tabBtns = viewer.querySelectorAll('.code-tab-btn');
    const panels = viewer.querySelectorAll('.code-panel');

    tabBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;

        tabBtns.forEach((b) => b.classList.remove('active'));
        panels.forEach((p) => p.classList.remove('active'));

        btn.classList.add('active');
        const activePanel = viewer.querySelector(`.code-panel[data-panel="${targetTab}"]`);
        if (activePanel) activePanel.classList.add('active');
      });
    });
  });
}

/* ==========================================================================
   3. COPY TO CLIPBOARD
   ========================================================================== */
function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const codeContainer = btn.closest('.code-viewer')?.querySelector('.code-panel.active') ||
                            btn.closest('.hint-content') ||
                            document.querySelector(btn.dataset.copyTarget);

      if (!codeContainer) return;
      const textToCopy = codeContainer.innerText || codeContainer.textContent;

      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<span>✓ Скопировано!</span>';
        btn.style.borderColor = 'var(--accent-emerald)';
        btn.style.color = '#34d399';

        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 2000);
      });
    });
  });
}

/* ==========================================================================
   4. HINT & SOLUTION TOGGLES
   ========================================================================== */
function initHintToggles() {
  document.querySelectorAll('.hint-toggle').forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const content = toggle.nextElementSibling;
      if (!content) return;

      const isShown = content.classList.contains('show');
      if (isShown) {
        content.classList.remove('show');
        toggle.innerHTML = '<span>💡 Показать решение / подсказку</span>';
      } else {
        content.classList.add('show');
        toggle.innerHTML = '<span>🔼 Скрыть решение</span>';
      }
    });
  });
}

/* ==========================================================================
   5. ROLE & CATEGORY FILTERS
   ========================================================================== */
function initFilters() {
  const filterPills = document.querySelectorAll('.filter-pill');
  const topicCards = document.querySelectorAll('.topic-card');

  filterPills.forEach((pill) => {
    pill.addEventListener('click', () => {
      filterPills.forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');

      const filterValue = pill.dataset.filter; // 'all', 'red', 'blue', 'detection'

      topicCards.forEach((card) => {
        if (filterValue === 'all') {
          card.style.display = 'block';
        } else {
          const roles = (card.dataset.roles || '').split(' ');
          if (roles.includes(filterValue)) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        }
      });
    });
  });
}

/* ==========================================================================
   6. LIVE SEARCH
   ========================================================================== */
function initSearch() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const topicCards = document.querySelectorAll('.topic-card');

    topicCards.forEach((card) => {
      const textContent = card.innerText.toLowerCase();
      if (textContent.includes(query)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

/* ==========================================================================
   7. LAB MODAL MANAGEMENT
   ========================================================================== */
function initLabModal() {
  const openBtn = document.getElementById('open-lab-modal-btn');
  const closeBtn = document.getElementById('close-lab-modal-btn');
  const modal = document.getElementById('lab-modal');

  if (openBtn && modal) {
    openBtn.addEventListener('click', () => modal.classList.add('open'));
  }
  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('open'));
  }
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
  }
}

/* ==========================================================================
   8. INTERACTIVE TEST / TERMINAL QUIZ
   ========================================================================== */
function initTerminalQuiz() {
  const runBtn = document.getElementById('terminal-verify-btn');
  const input = document.getElementById('terminal-input');
  const output = document.getElementById('terminal-output');

  if (!runBtn || !input || !output) return;

  runBtn.addEventListener('click', () => {
    const val = input.value.trim();
    if (!val) {
      output.innerHTML = '<span style="color: var(--accent-crimson)">[ERROR] Введите команду, payload или параметр для проверки.</span>';
      return;
    }

    output.innerHTML = '<span style="color: var(--accent-cyan)">[PROCESSING] Запуск симуляции проверки через WAF и фильтры...</span>';

    setTimeout(() => {
      // 1. Check for SQL Injection patterns
      if (/(\bUNION\b.*\bSELECT\b|--|'\s*OR\s*'1'='1)/i.test(val)) {
        output.innerHTML = `
<span style="color: var(--accent-amber)">[INSPECTION RESULT] Обнаружен сигнатурный паттерн SQL Injection!</span>
- Обнаружено: UNION / Logical tautology
- Сработка Suricata SID: 2000002 (In-Band SQLi)
- Рекомендация WAF (ModSecurity): HTTP 403 Forbidden
- Root Cause Fix: Использовать Prepared Statements (параметризованные запросы).
        `;
      } 
      // 2. Check for SSRF cloud metadata
      else if (/169\.254\.169\.254|metadata\.google\.internal|0\.0\.0\.0/i.test(val)) {
        output.innerHTML = `
<span style="color: var(--accent-crimson)">[CRITICAL THREAT] Попытка SSRF к Cloud Metadata Service!</span>
- Адрес цели: ${val}
- Сработка Suricata SID: 2000001
- Угроза: Кража временных IAM/K8s ролей и приватных ключей.
- Исправление: Валидация IP через getaddrinfo() + запрет RFC 1918 / Link-Local + переход на IMDSv2 (Session Token).
        `;
      }
      // 3. Command injection
      else if (/(\||;|&|`|\$\()/.test(val)) {
        output.innerHTML = `
<span style="color: var(--accent-crimson)">[CRITICAL THREAT] Попытка Command Injection через метасимволы shell!</span>
- Метасимволы: ${val.match(/(\||;|&|`|\$\()/g)?.join(', ')}
- Сработка Suricata SID: 2000003
- Исправление: Запрет вызова shell=True в subprocess / exec. Передача аргументов списком ['ping', '-c', '2', ip].
        `;
      }
      // 4. Default / safe
      else {
        output.innerHTML = `
<span style="color: var(--accent-emerald)">[PASSED] Пакет прошел валидацию входных фильтров без явных аномалий.</span>
- Входные данные: "${val}"
- Статус: Clean / Validated
        `;
      }
    }, 400);
  });
}
