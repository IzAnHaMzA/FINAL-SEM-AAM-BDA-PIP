(function () {
  const APP_KEY = "study-hub-v2";
  const TYPING_GOAL = 5;
  const VOICE_GOAL = 7;

  function weekKey() {
    const date = new Date();
    const utc = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const day = utc.getUTCDay() || 7;
    utc.setUTCDate(utc.getUTCDate() + 4 - day);
    const yearStart = new Date(Date.UTC(utc.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((utc - yearStart) / 86400000) + 1) / 7);
    return `${utc.getUTCFullYear()}-W${String(weekNo).padStart(2, "0")}`;
  }

  function readStore() {
    return JSON.parse(localStorage.getItem(APP_KEY) || '{"profiles":{},"activeUser":"Guest"}');
  }

  function writeStore(store) {
    localStorage.setItem(APP_KEY, JSON.stringify(store));
  }

  function ensureProfile(store, name) {
    if (!store.profiles[name]) store.profiles[name] = { weeks: {} };
    if (!store.profiles[name].weeks[weekKey()]) store.profiles[name].weeks[weekKey()] = { tasks: {} };
    return store.profiles[name];
  }

  function currentContext() {
    const store = readStore();
    const name = store.activeUser || "Guest";
    const profile = ensureProfile(store, name);
    writeStore(store);
    return { store, name, week: profile.weeks[weekKey()] };
  }

  function allQuestions() {
    return window.taskQuestions || window.questions || [];
  }

  function ensureTask(week, questionId) {
    if (!week.tasks[questionId]) week.tasks[questionId] = { typing: 0, voice: 0 };
    return week.tasks[questionId];
  }

  function saveProfileName() {
    const input = document.getElementById("profileName");
    const status = document.getElementById("profileStatus");
    if (!input) return;
    const name = input.value.trim() || "Guest";
    const store = readStore();
    store.activeUser = name;
    ensureProfile(store, name);
    writeStore(store);
    if (status) status.textContent = `Active profile: ${name}. Weekly task progress is stored on this browser.`;
    renderProfileSummary();
    renderTaskList();
  }

  function questionProgress(questionId) {
    const { week } = currentContext();
    return ensureTask(week, String(questionId));
  }

  function incrementQuestionProgress(questionId, kind) {
    const { store, name, week } = currentContext();
    const task = ensureTask(week, String(questionId));
    if (kind === "typing" && task.typing < TYPING_GOAL) task.typing += 1;
    if (kind === "voice" && task.voice < VOICE_GOAL) task.voice += 1;
    store.profiles[name].weeks[weekKey()] = week;
    writeStore(store);
    renderProfileSummary();
    renderTaskList();
    maybeNotify();
  }

  function weeklyTotals() {
    const questions = allQuestions();
    const { week } = currentContext();
    let typingDone = 0;
    let voiceDone = 0;
    questions.forEach((question) => {
      const task = ensureTask(week, String(question.id));
      typingDone += task.typing;
      voiceDone += task.voice;
    });
    return {
      typingDone,
      voiceDone,
      typingTarget: questions.length * TYPING_GOAL,
      voiceTarget: questions.length * VOICE_GOAL,
    };
  }

  function renderProfileSummary() {
    const { name } = currentContext();
    const totals = weeklyTotals();
    const typing = document.getElementById("typingProgress");
    const voice = document.getElementById("voiceProgress");
    const left = document.getElementById("doneLeft");
    const hello = document.getElementById("profileHello");
    const input = document.getElementById("profileName");
    const typingSummary = document.getElementById("weeklyTypingSummary");
    const voiceSummary = document.getElementById("weeklyVoiceSummary");
    if (typing) typing.textContent = `${totals.typingDone} / ${totals.typingTarget}`;
    if (voice) voice.textContent = `${totals.voiceDone} / ${totals.voiceTarget}`;
    if (left) left.textContent = `${totals.typingDone + totals.voiceDone} done / ${Math.max(0, totals.typingTarget + totals.voiceTarget - totals.typingDone - totals.voiceDone)} left`;
    if (hello) hello.textContent = name;
    if (input && !input.value) input.value = name === "Guest" ? "" : name;
    if (typingSummary) typingSummary.textContent = totals.typingDone;
    if (voiceSummary) voiceSummary.textContent = totals.voiceDone;
  }

  function renderTaskList() {
    const root = document.getElementById("taskList");
    if (!root) return;
    const questions = allQuestions();
    const groups = {};
    questions.forEach((question) => {
      const key = question.id >= 300 ? "MAN" : question.id >= 200 ? "BDA" : question.id >= 100 ? "PIP" : "AAM";
      if (!groups[key]) groups[key] = [];
      groups[key].push(question);
    });
    root.innerHTML = Object.entries(groups).map(([group, items]) => `
      <section class="task-group">
        <div class="panel-head"><h3>${group}</h3><span>${items.length} questions</span></div>
        <div class="task-items">
          ${items.map((question) => {
            const progress = questionProgress(question.id);
            return `
              <article class="task-item">
                <div>
                  <strong>Q.${question.id}</strong>
                  <p>${escapeHtml(question.question)}</p>
                </div>
                <div class="task-progress">
                  <span>Type ${progress.typing}/${TYPING_GOAL}</span>
                  <span>Read ${progress.voice}/${VOICE_GOAL}</span>
                </div>
                <div class="test-actions">
                  <button type="button" class="soft-btn" data-task-type="typing" data-task-question="${question.id}">+ Type</button>
                  <button type="button" class="soft-btn" data-task-type="voice" data-task-question="${question.id}">+ Read</button>
                </div>
              </article>
            `;
          }).join("")}
        </div>
      </section>
    `).join("");
  }

  function escapeHtml(text) {
    return String(text).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }

  function maybeNotify() {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    const totals = weeklyTotals();
    const { name } = currentContext();
    const body = `${name}: typing ${totals.typingDone}/${totals.typingTarget}, voice ${totals.voiceDone}/${totals.voiceTarget}.`;
    navigator.serviceWorker?.ready.then((registration) => {
      registration.showNotification("Weekly study task update", { body, icon: "/static/icon-192.png", badge: "/static/icon-192.png" });
    });
  }

  function registerPwa() {
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js");
  }

  function enableNotifications() {
    if ("Notification" in window) Notification.requestPermission().then(() => maybeNotify());
  }

  function formatCountdownParts(distanceMs) {
    const totalSeconds = Math.max(0, Math.floor(distanceMs / 1000));
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return {
      days: String(days).padStart(2, "0"),
      hours: String(hours).padStart(2, "0"),
      minutes: String(minutes).padStart(2, "0"),
      seconds: String(seconds).padStart(2, "0"),
    };
  }

  function renderCountdownClock(clock) {
    const target = clock.dataset.countdown;
    if (!target) return;
    const targetTime = new Date(target);
    const update = () => {
      const distance = targetTime.getTime() - Date.now();
      const values = formatCountdownParts(distance);
      Object.entries(values).forEach(([unit, value]) => {
        const node = clock.querySelector(`[data-unit="${unit}"]`);
        if (node) node.textContent = value;
      });
      clock.classList.toggle("is-complete", distance <= 0);
    };
    update();
    window.setInterval(update, 1000);
  }

  function initCountdowns() {
    document.querySelectorAll("[data-countdown]").forEach((clock) => renderCountdownClock(clock));
  }

  function storedAnswerForVoice(questionId) {
    const question = allQuestions().find((item) => item.id === Number(questionId));
    if (!question) return "";
    if (question.type === "difference") {
      return `${question.definition} ${question.difference_basis.map((basis, index) => `${basis}: ${question.differences[index][0]} and ${question.differences[index][1]}`).join(". ")}.`;
    }
    return `${question.definition} ${question.points.join(". ")}.`;
  }

  function speakAnswer() {
    const select = document.getElementById("voiceQuestionSelect");
    if (!select || !window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(storedAnswerForVoice(select.value));
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }

  function startVoicePractice() {
    const status = document.getElementById("voiceStatus");
    const select = document.getElementById("voiceQuestionSelect");
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition || !select) {
      if (status) status.textContent = "Voice recognition is not available in this browser.";
      return;
    }
    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    if (status) status.textContent = "Listening... read the answer aloud.";
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript || "";
      if (transcript.trim().length > 15) {
        incrementQuestionProgress(Number(select.value), "voice");
        if (status) status.textContent = `Voice practice counted for this question.`;
      } else if (status) {
        status.textContent = "Voice capture was too short. Try reading more of the answer.";
      }
    };
    recognition.onerror = () => {
      if (status) status.textContent = "Voice capture failed. Allow microphone access and try again.";
    };
    recognition.start();
  }

  // Image upload and reference handling
  async function loadAvailableImages(questionId) {
    try {
      const response = await fetch('/api/images');
      const data = await response.json();
      const select = document.querySelector(`.image-reference-select[data-question-id="${questionId}"]`);
      if (!select) return;
      
      // Clear existing options except the first one
      while (select.options.length > 1) {
        select.remove(1);
      }
      
      // Add image options
      data.images.forEach(img => {
        const option = document.createElement('option');
        option.value = img.url;
        option.textContent = `${img.filename} (${img.size_kb}KB)`;
        select.appendChild(option);
      });
    } catch (error) {
      console.error('Error loading images:', error);
    }
  }

  async function uploadImage(questionId) {
    const input = document.querySelector(`.image-upload-input[data-question-id="${questionId}"]`);
    const statusDiv = document.querySelector(`.image-upload-status[data-question-id="${questionId}"]`);
    
    if (!input || !input.files.length) {
      if (statusDiv) statusDiv.textContent = 'Please select a file';
      return;
    }

    const formData = new FormData();
    formData.append('file', input.files[0]);

    if (statusDiv) {
      statusDiv.style.display = 'block';
      statusDiv.textContent = 'Uploading...';
      statusDiv.style.color = 'var(--secondary)';
    }

    try {
      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      });
      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : null;

      if (response.ok && data?.success) {
        if (statusDiv) {
          statusDiv.textContent = 'Upload successful!';
          statusDiv.style.color = 'var(--primary)';
          setTimeout(() => statusDiv.style.display = 'none', 2000);
        }
        input.value = '';
        // Reload image dropdown
        await loadAvailableImages(questionId);
      } else {
        if (statusDiv) {
          statusDiv.textContent = `Error: ${data?.error || 'Upload failed. Please try a smaller image.'}`;
          statusDiv.style.color = '#d32f2f';
        }
      }
    } catch (error) {
      if (statusDiv) {
        statusDiv.textContent = 'Upload failed. Please try again.';
        statusDiv.style.color = '#d32f2f';
      }
      console.error('Upload error:', error);
    }
  }

  function displaySelectedImage(questionId, imageUrl) {
    const displayArea = document.querySelector(`.image-display-area[data-question-id="${questionId}"]`);
    if (!displayArea || !imageUrl) return;

    const img = displayArea.querySelector('.selected-image');
    const filename = displayArea.querySelector('.image-filename');
    
    if (img && imageUrl) {
      img.src = imageUrl;
      displayArea.style.display = 'block';
      if (filename) {
        const parts = imageUrl.split('/');
        filename.textContent = `Image: ${parts[parts.length - 1]}`;
      }
    } else {
      displayArea.style.display = 'none';
    }
  }

  // Initialize image handlers for all questions
  function initImageHandlers() {
    // Load initial image dropdowns
    document.querySelectorAll('.image-reference-select').forEach(select => {
      const questionId = select.dataset.questionId;
      loadAvailableImages(questionId);
      
      // Handle dropdown change
      select.addEventListener('change', (e) => {
        displaySelectedImage(questionId, e.target.value);
      });
    });

    // Handle upload buttons
    document.querySelectorAll('.image-upload-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const questionId = btn.dataset.questionId;
        uploadImage(questionId);
      });
    });

    // Handle file input enter key
    document.querySelectorAll('.image-upload-input').forEach(input => {
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          const questionId = input.dataset.questionId;
          uploadImage(questionId);
        }
      });
    });
  }

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.id === "saveProfileBtn") saveProfileName();
    if (target.id === "notifyBtn") enableNotifications();
    if (target.id === "playAnswerBtn") speakAnswer();
    if (target.id === "startVoiceBtn") startVoicePractice();
    if (target.matches("[data-task-question]")) {
      incrementQuestionProgress(Number(target.dataset.taskQuestion), target.dataset.taskType);
    }
    if (target.matches("[data-check]")) {
      const id = Number(target.dataset.check);
      const textarea = document.querySelector(`[data-answer="${id}"]`);
      if (textarea && textarea.value.trim()) incrementQuestionProgress(id, "typing");
    }
    if (target.id === "submitTestAnswer") {
      const questionBlock = document.querySelector("#testArea h3");
      const match = questionBlock?.textContent?.match(/Q\.(\d+)/);
      if (match) {
        const textarea = document.getElementById("testAnswer");
        if (textarea && textarea.value.trim()) incrementQuestionProgress(Number(match[1]), "typing");
      }
    }
  });

  registerPwa();
  initCountdowns();
  renderProfileSummary();
  renderTaskList();
})();
