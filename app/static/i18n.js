/**
 * Lecture4All - Universal Cross-Lingual Search & Language Manager
 * 
 * Architecture:
 *   - Lectures can be recorded in ANY language (English, Dutch, Tamil, Malayalam, Hindi).
 *   - Users can search in ANY language (English, Dutch, Tamil, Malayalam, Hindi).
 *   - The multilingual vector space (Universal Sentence Encoder) maps all languages
 *     into a shared 512-dimensional semantic embedding space.
 */

const TRANSLATION_DATA = {
  en: {
    targetName: "English",
    targetEnglish: "English",
    directionLabel: "Search in English",
    eyebrowText: "Cross-Lingual Search · Any Language ⇄ Any Language",
    heroTitleHtml: 'Search Across <em class="lf-headline-em">Any Lecture</em><br>In Any Language',
    heroDesc: "Search academic lectures in English, Dutch, Tamil, Malayalam, or Hindi. Jump directly to the exact spoken second across the entire multilingual video catalog.",
    searchPlaceholder: "Search any topic across all lectures (e.g., Sorting algorithms, Machine learning)...",
    speechCode: "en-US",
    sampleLabel: "Try searching in English:",
    sampleQueries: [
      "Sorting algorithms",
      "Binary search tree",
      "Dynamic programming",
      "Memory management",
      "Artificial intelligence",
      "Operating systems"
    ],
    transcriptBadge: "Transcript: English",
    listeningPrompt: "Listening in English... Speak your query",
    voiceCancel: "Cancel",
    voiceDone: "Done",
    voiceHint: "Speak in English, Nederlands, தமிழ், മലയാളം, or हिन्दी",
    searchingMessage: "Searching lecture timestamps...",
    noResultsTitle: "No matching lecture segments found",
    noResultsDesc: "Try searching with alternative keywords in English, Dutch, Tamil, Malayalam, or Hindi.",
    backToSearch: "Return to Search",
    jumpToTimestamp: "Jump to timestamp"
  },
  nl: {
    targetName: "Nederlands",
    targetEnglish: "Dutch",
    directionLabel: "Zoeken in het Nederlands",
    eyebrowText: "Meertalig Zoeken · Elke Taal ⇄ Elke Taal",
    heroTitleHtml: 'Zoek Binnen <em class="lf-headline-em">Elk College</em><br>In Elke Taal',
    heroDesc: "Zoek door academische colleges in het Nederlands, Engels, Tamil, Malayalam of Hindi. Spring direct naar het exacte gesproken moment met precieze tijdstempels.",
    searchPlaceholder: "Zoek een onderwerp in alle colleges (bijv. Sorteeralgoritmen, Neurale netwerken)...",
    speechCode: "nl-NL",
    sampleLabel: "Probeer te zoeken in het Nederlands:",
    sampleQueries: [
      "Sorteeralgoritmen",
      "Binaire zoekboom",
      "Dynamisch programmeren",
      "Geheugenbeheer",
      "Machinaal leren",
      "Besturingssystemen"
    ],
    transcriptBadge: "Transcript: Nederlands",
    listeningPrompt: "Luisteren in het Nederlands... Spreek nu",
    voiceCancel: "Annuleren",
    voiceDone: "Klaar",
    voiceHint: "Spreek in het Nederlands, Engels, தமிழ், മലയാളം of हिन्दी",
    searchingMessage: "Zoeken naar college-tijdstempels...",
    noResultsTitle: "Geen overeenkomende college-segmenten gevonden",
    noResultsDesc: "Probeer te zoeken met alternatieve trefwoorden in het Nederlands, Engels, Tamil, Malayalam of Hindi.",
    backToSearch: "Terug naar Zoeken",
    jumpToTimestamp: "Spring naar tijdstempel"
  },
  ta: {
    targetName: "தமிழ்",
    targetEnglish: "Tamil",
    directionLabel: "தமிழில் தேடுங்கள்",
    eyebrowText: "பன்மொழி தேடல் · அனைத்து மொழிகளும் ⇄ அனைத்தும்",
    heroTitleHtml: 'எந்த விரிவுரையிலும் <em class="lf-headline-em">தமிழில்</em><br>தேடுங்கள்',
    heroDesc: "ஆங்கிலம், டச்சு, தமிழ், மலையாளம் அல்லது இந்தி விரிவுரைகளில் உங்களுக்குத் தேவையான தலைப்புகளைத் தமிழில் தேடி, சரியான நேர முத்திரைக்கு உடனடியாகச் செல்லுங்கள்.",
    searchPlaceholder: "அனைத்து விரிவுரைகளிலும் தேடுங்கள் (எ.கா. வரிசைப்படுத்துதல், செயற்கை நுண்ணறிவு)...",
    speechCode: "ta-IN",
    sampleLabel: "தமிழில் தேட முயற்சி செய்யுங்கள்:",
    sampleQueries: [
      "வரிசைப்படுத்துதல் அல்காரிதம்கள்",
      "பைனரி தேடல் மரம்",
      "டைனமிக் புரோகிராமிங்",
      "நினைவக மேலாண்மை",
      "செயற்கை நுண்ணறிவு",
      "இயக்க முறைமைகள்"
    ],
    transcriptBadge: "டிரான்ஸ்கிரிப்ட்: தமிழ் (Tamil)",
    listeningPrompt: "தமிழில் கேட்கிறது... இப்போது பேசுங்கள்",
    voiceCancel: "ரத்து செய்",
    voiceDone: "முடிந்தது",
    voiceHint: "ஆங்கிலம், டச்சு, தமிழ், மலையாளம் அல்லது இந்தியில் பேசுங்கள்",
    searchingMessage: "விரிவுரை நேரமுத்திரைகளைத் தேடுகிறது...",
    noResultsTitle: "முடிவுகள் எதுவும் கிடைக்கவில்லை",
    noResultsDesc: "வேறு தேடல் வார்த்தையைப் பயன்படுத்தவும் அல்லது ஆங்கிலம், டச்சு, தமிழ், மலையாளம், இந்தி மொழிகளில் பிற தலைப்புகளைத் தேடவும்.",
    backToSearch: "தேடலுக்குத் திரும்பு",
    jumpToTimestamp: "விரிவுரைக்குச் செல்"
  },
  ml: {
    targetName: "മലയാളം",
    targetEnglish: "Malayalam",
    directionLabel: "മലയാളത്തിൽ തിരയുക",
    eyebrowText: "ബഹുഭാഷാ തിരച്ചിൽ · ഏത് ഭാഷയും ⇄ ഏത് ഭാഷയും",
    heroTitleHtml: 'ഏത് പ്രഭാഷണവും <em class="lf-headline-em">മലയാളത്തിൽ</em><br>തിരയുക',
    heroDesc: "ഇംഗ്ലീഷ്, ഡച്ച്, തമിഴ്, മലയാളം, അല്ലെങ്കിൽ ഹിന്ദി പ്രഭാഷണങ്ങളിൽ ആവശ്യമുള്ള ഭാഗങ്ങൾ മലയാളത്തിൽ തിരഞ്ഞ് കൃത്യമായ വീഡിയോ ടൈംസ്റ്റാമ്പിലേക്ക് നേരിട്ടെത്തുക.",
    searchPlaceholder: "ഏത് വിഷയവും തിരയുക (ഉദാ: സോർട്ടിംഗ്, ഡാറ്റാ സ്ട്രക്ചറുകൾ)...",
    speechCode: "ml-IN",
    sampleLabel: "മലയാളത്തിൽ തിരയാൻ ശ്രമിക്കുക:",
    sampleQueries: [
      "സോർട്ടിംഗ് അൽഗോരിതങ്ങൾ",
      "ബൈനറി സെർച്ച് ട്രീ",
      "ഡൈനാമിക് പ്രോഗ്രാമിംഗ്",
      "മെമ്മറി മാനേജ്മെന്റ്",
      "മെഷീൻ ലേണിംഗ്",
      "ഓപ്പറേറ്റിംഗ് സിസ്റ്റങ്ങൾ"
    ],
    transcriptBadge: "ട്രാൻസ്ക്രിപ്റ്റ്: മലയാളം (Malayalam)",
    listeningPrompt: "മലയാളത്തിൽ കേൾക്കുന്നു... സംസാരിക്കുക",
    voiceCancel: "റദ്ദാക്കുക",
    voiceDone: "പൂർത്തിയായി",
    voiceHint: "ഇംഗ്ലീഷ്, ഡച്ച്, തമിഴ്, മലയാളം, അല്ലെങ്കിൽ ഹിന്ദിയിൽ സംസാരിക്കുക",
    searchingMessage: "പ്രഭാഷണ ടൈംസ്റ്റാമ്പുകൾ തിരയുന്നു...",
    noResultsTitle: "പൊരുത്തപ്പെടുന്ന ഭാഗങ്ങൾ കണ്ടെത്തിയില്ല",
    noResultsDesc: "ഇംഗ്ലീഷ്, ഡച്ച്, തമിഴ്, മലയാളം അല്ലെങ്കിൽ ഹിന്ദിയിൽ മറ്റ് കീവേഡുകൾ ഉപയോഗിച്ച് തിരയാൻ ശ്രമിക്കുക.",
    backToSearch: "തിരച്ചിലിലേക്ക് മടങ്ങുക",
    jumpToTimestamp: "ടൈംസ്റ്റാമ്പിലേക്ക് പോകുക"
  },
  hi: {
    targetName: "हिन्दी",
    targetEnglish: "Hindi",
    directionLabel: "हिन्दी में खोजें",
    eyebrowText: "बहुभाषी खोज · किसी भी भाषा ⇄ किसी भी भाषा",
    heroTitleHtml: 'किसी भी व्याख्यान में <em class="lf-headline-em">हिन्दी में</em><br>खोजें',
    heroDesc: "अंग्रेजी, डच, तमिल, मलयालम या हिन्दी के किसी भी शैक्षणिक व्याख्यान में अपनी भाषा में खोजें और सीधे सटीक समय पर पहुंचें।",
    searchPlaceholder: "सभी व्याख्यानों में विषय खोजें (उदा: एल्गोरिदम, मशीन लर्निंग)...",
    speechCode: "hi-IN",
    sampleLabel: "हिन्दी में खोज कर देखें:",
    sampleQueries: [
      "सॉर्टिंग एल्गोरिदम",
      "बाइनरी सर्च ट्री",
      "डायनामिक प्रोग्रामिंग",
      "मेमोरी प्रबंधन",
      "आर्टिफिशियल इंटेलिजेंस",
      "ऑपरेटिंग सिस्टम"
    ],
    transcriptBadge: "ट्रांसक्रिप्ट: हिन्दी (Hindi)",
    listeningPrompt: "हिन्दी में सुन रहे हैं... अब बोलें",
    voiceCancel: "रद्द करें",
    voiceDone: "पूर्ण",
    voiceHint: "अंग्रेजी, डच, तमिल, मलयालम या हिन्दी में बोलें",
    searchingMessage: "व्याख्यान टाइमस्टैम्प खोजे जा रहे हैं...",
    noResultsTitle: "कोई मिलान व्याख्यान खंड नहीं मिला",
    noResultsDesc: "अंग्रेजी, डच, तमिल, मलयालम या हिन्दी में अन्य कीवर्ड से खोजें।",
    backToSearch: "खोज पर वापस जाएं",
    jumpToTimestamp: "टाइमस्टैम्प पर जाएं"
  }
};

class TranslationManager {
  constructor() {
    this.storageKey = "lecture4all_search_lang";
    this.currentTarget = this.getSavedTarget();
  }

  getSavedTarget() {
    const saved = localStorage.getItem(this.storageKey);
    if (saved && TRANSLATION_DATA[saved]) {
      return saved;
    }
    return "en";
  }

  setTargetLanguage(langCode) {
    if (!TRANSLATION_DATA[langCode]) return;
    this.currentTarget = langCode;
    localStorage.setItem(this.storageKey, langCode);
    this.applyTargetLanguage();
    window.dispatchEvent(
      new CustomEvent("lecture4all:targetLanguageChanged", { detail: { target: langCode } })
    );
  }

  getTargetConfig() {
    return TRANSLATION_DATA[this.currentTarget] || TRANSLATION_DATA.en;
  }

  applyTargetLanguage() {
    const config = this.getTargetConfig();

    // 0. Auto-localize all data-i18n elements
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (config[key]) {
        el.textContent = config[key];
      }
    });

    // 1. Search Input Placeholder
    const queryInput = document.getElementById("query");
    if (queryInput) {
      queryInput.setAttribute("placeholder", config.searchPlaceholder);
    }

    // 2. Language Selector Buttons in Nav & Bar
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

    // 3. Eyebrow & Direction Labels
    const heroEyebrowTarget = document.getElementById("heroEyebrowTarget");
    if (heroEyebrowTarget) {
      heroEyebrowTarget.textContent = config.eyebrowText || config.directionLabel;
    }

    // 4. Hero Headline & Description
    const heroHeadline = document.getElementById("heroHeadline");
    if (heroHeadline && config.heroTitleHtml) {
      heroHeadline.innerHTML = config.heroTitleHtml;
    }

    const heroDesc = document.getElementById("heroDesc");
    if (heroDesc && config.heroDesc) {
      heroDesc.textContent = config.heroDesc;
    }

    // 5. Target Name Badges Across Pages
    document.querySelectorAll(".target-lang-name-display").forEach(el => {
      el.textContent = config.targetName;
    });

    // 6. Highlight active lang in hero flow panel
    document.querySelectorAll(".lf-flow-lang").forEach(el => {
      const lang = el.getAttribute("data-lang");
      if (lang === this.currentTarget) {
        el.classList.add("active");
      } else {
        el.classList.remove("active");
      }
    });

    // 7. Sample Query Chips
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
        chip.innerHTML = `<span class="lf-chip-icon">🔍</span><span>${q}</span>`;
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

    // 8. Voice Recognition Listening Language & Dialog Texts
    if (window.lectureVoiceRecognition) {
      window.lectureVoiceRecognition.lang = config.speechCode;
    }

    const voicePromptEl = document.getElementById("voiceDialogTitle");
    if (voicePromptEl) {
      voicePromptEl.textContent = config.listeningPrompt;
    }

    const voiceHintEl = document.getElementById("voiceHintText");
    if (voiceHintEl && config.voiceHint) {
      voiceHintEl.textContent = config.voiceHint;
    }

    // 9. Transcript Header Badges if on Video Page
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
    btn.addEventListener("click", e => {
      e.preventDefault();
      const code = btn.getAttribute("data-lang");
      if (code) {
        window.translationManager.setTargetLanguage(code);
      }
    });
  });
});
