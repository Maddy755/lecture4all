/**
 * Lecture4All - Source to Target Translation Engine
 * Source Language: Nederlands (Dutch)
 * Target Languages:
 *   - ta: தமிழ் (Tamil)
 *   - ml: മലയാളം (Malayalam)
 *   - hi: हिन्दी (Hindi)
 */

const TRANSLATION_DATA = {
  ta: {
    targetName: "தமிழ்",
    targetEnglish: "Tamil",
    sourceName: "Nederlands",
    directionLabel: "Nederlands → தமிழ்",
    searchPlaceholder: "விரிவுரையில் ஒரு தலைப்பைத் தேடுங்கள்...",
    speechCode: "ta-IN",
    sampleLabel: "Sample search queries in Tamil (for Dutch lecture content):",
    sampleQueries: [
      "வரிசைப்படுத்துதல் அல்காரிதம்கள்",
      "பைனரி தேடல் மரம்",
      "டைனமிக் புரோகிராமிங்",
      "நினைவக மேலாண்மை"
    ],
    transcriptBadge: "Translated Transcript: தமிழ் (Tamil)",
    listeningPrompt: "Listening in Tamil... Speak now",
    voiceCancel: "Cancel",
    voiceDone: "Done"
  },
  ml: {
    targetName: "മലയാളം",
    targetEnglish: "Malayalam",
    sourceName: "Nederlands",
    directionLabel: "Nederlands → മലയാളം",
    searchPlaceholder: "പ്രഭാഷണത്തിൽ ഒരു വിഷയം തിരയുക...",
    speechCode: "ml-IN",
    sampleLabel: "Sample search queries in Malayalam (for Dutch lecture content):",
    sampleQueries: [
      "സോർട്ടിംഗ് അൽഗോരിതങ്ങൾ",
      "ബൈനറി സെർച്ച് ട്രീ",
      "ഡൈനാമിക് പ്രോഗ്രാമിംഗ്",
      "മെമ്മറി മാനേജ്മെന്റ്"
    ],
    transcriptBadge: "Translated Transcript: മലയാളം (Malayalam)",
    listeningPrompt: "Listening in Malayalam... Speak now",
    voiceCancel: "Cancel",
    voiceDone: "Done"
  },
  hi: {
    targetName: "हिन्दी",
    targetEnglish: "Hindi",
    sourceName: "Nederlands",
    directionLabel: "Nederlands → हिन्दी",
    searchPlaceholder: "व्याख्यान में किसी विषय को खोजें...",
    speechCode: "hi-IN",
    sampleLabel: "Sample search queries in Hindi (for Dutch lecture content):",
    sampleQueries: [
      "सॉर्टिंग एल्गोरिदम",
      "बाइनरी सर्च ट्री",
      "डायनामिक प्रोग्रामिंग",
      "मेमोरी प्रबंधन"
    ],
    transcriptBadge: "Translated Transcript: हिन्दी (Hindi)",
    listeningPrompt: "Listening in Hindi... Speak now",
    voiceCancel: "Cancel",
    voiceDone: "Done"
  }
};

class TranslationManager {
  constructor() {
    this.storageKey = "lecture4all_target_lang";
    this.currentTarget = this.getSavedTarget();
  }

  getSavedTarget() {
    const saved = localStorage.getItem(this.storageKey);
    if (saved && TRANSLATION_DATA[saved]) {
      return saved;
    }
    return "ta"; // Default target is Tamil
  }

  setTargetLanguage(langCode) {
    if (!TRANSLATION_DATA[langCode]) return;
    this.currentTarget = langCode;
    localStorage.setItem(this.storageKey, langCode);
    this.applyTargetLanguage();
    window.dispatchEvent(new CustomEvent("lecture4all:targetLanguageChanged", { detail: { target: langCode } }));
  }

  getTargetConfig() {
    return TRANSLATION_DATA[this.currentTarget] || TRANSLATION_DATA.ta;
  }

  applyTargetLanguage() {
    const config = this.getTargetConfig();

    // 1. Update Search Input Placeholder
    const queryInput = document.getElementById("query");
    if (queryInput) {
      queryInput.setAttribute("placeholder", config.searchPlaceholder);
    }

    // 2. Update Target Language Selector Buttons
    document.querySelectorAll(".lf-lang-btn").forEach(btn => {
      const code = btn.getAttribute("data-lang");
      if (code === this.currentTarget) {
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
      } else {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
      }
    });

    // 3. Update Pipeline Label if present
    const pipelineDirectionEl = document.getElementById("pipelineDirectionText");
    if (pipelineDirectionEl) {
      pipelineDirectionEl.textContent = `Nederlands → ${config.targetName}`;
    }

    // 4. Update Target Name Badges
    document.querySelectorAll(".target-lang-name-display").forEach(el => {
      el.textContent = config.targetName;
    });

    // 5. Update Sample Queries Chips
    const chipsContainer = document.getElementById("sampleChipsContainer");
    const sampleLabel = document.getElementById("sampleQueriesLabel");
    if (sampleLabel) {
      sampleLabel.textContent = config.sampleLabel;
    }
    if (chipsContainer) {
      chipsContainer.innerHTML = "";
      config.sampleQueries.forEach(q => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "lf-chip notranslate";
        chip.setAttribute("translate", "no");
        chip.textContent = q;
        chip.addEventListener("click", () => {
          if (queryInput) {
            queryInput.value = q;
            const form = document.getElementById("searchForm");
            if (form) form.submit();
          }
        });
        chipsContainer.appendChild(chip);
      });
    }

    // 6. Update Voice Recognition Listening Language
    if (window.lectureVoiceRecognition) {
      window.lectureVoiceRecognition.lang = config.speechCode;
    }

    const voicePromptEl = document.getElementById("voiceDialogTitle");
    if (voicePromptEl) {
      voicePromptEl.textContent = config.listeningPrompt;
    }

    // 7. Update Transcript Header Badges if on Video Page
    const transcriptTargetBadge = document.getElementById("transcriptTargetBadge");
    if (transcriptTargetBadge) {
      transcriptTargetBadge.textContent = config.transcriptBadge;
    }
  }
}

// Global singleton
window.translationManager = new TranslationManager();

document.addEventListener("DOMContentLoaded", () => {
  window.translationManager.applyTargetLanguage();

  // Attach button listeners
  document.querySelectorAll(".lf-lang-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const code = btn.getAttribute("data-lang");
      if (code) {
        window.translationManager.setTargetLanguage(code);
      }
    });
  });
});
