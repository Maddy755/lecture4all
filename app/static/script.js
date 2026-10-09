// Lecture4All Main Script - Multilingual Voice Search, Shorts Mode, Dynamic Cards

// Apply the switch state as soon as possible to avoid flicker
(function () {
    const savedState = localStorage.getItem("shortsSwitch");
    const isChecked = savedState === "true";
    const switchElement = document.getElementById("shorts");
    if (switchElement) {
        switchElement.checked = isChecked;
        switchElement.classList.remove("hidden");
    }
})();

document.addEventListener("DOMContentLoaded", function () {
    const switchElement = document.getElementById("shorts");
    const textElement = document.getElementById("shortsViewInfo");
    const searchForm = document.getElementById("searchForm");

    function updateShortsViewInfo(isChecked) {
        if (textElement) {
            textElement.style.display = isChecked ? "block" : "none";
        }
        updateFormAction(isChecked);
    }

    function updateFormAction(isChecked) {
        if (searchForm) {
            const shortsUrl = searchForm.getAttribute('data-shorts-url');
            const searchResultsUrl = searchForm.getAttribute('data-searchresults-url');
            searchForm.action = isChecked ? shortsUrl : searchResultsUrl;
        }
    }

    const savedState = localStorage.getItem("shortsSwitch");
    const isChecked = savedState === "true";
    if (switchElement) {
        switchElement.checked = isChecked;
        updateShortsViewInfo(isChecked);

        switchElement.addEventListener("change", function () {
            localStorage.setItem("shortsSwitch", switchElement.checked);
            updateShortsViewInfo(switchElement.checked);
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const microButton = document.getElementById('micro-btn');
    const audioPopup = document.getElementById('audioPopup');
    const searchForm = document.getElementById('searchForm');
    const loadingPopup = document.getElementById('loadingPopup');
    const warningDiv = document.getElementById('speech-recognition-warning');
    const voiceDoneBtn = document.getElementById('voiceDoneBtn');
    const voiceCancelBtn = document.getElementById('voiceCancelBtn');

    let audioStream = null;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        if (warningDiv) warningDiv.style.display = 'block';
    } else {
        // Pick language matching current translation manager
        const currentLang = (window.translationManager && window.translationManager.currentTarget)
            ? window.translationManager.currentTarget
            : 'en';
        const langMap = {
            en: 'en-US',
            nl: 'nl-NL',
            ta: 'ta-IN',
            ml: 'ml-IN',
            hi: 'hi-IN'
        };
        recognition.lang = langMap[currentLang] || 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        window.lectureVoiceRecognition = recognition;

        if (microButton) {
            microButton.addEventListener("click", async () => {
                try {
                    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    if (audioPopup) audioPopup.style.display = 'flex';
                    recognition.start();
                } catch(err) {
                    console.warn("Microphone access not granted or failed", err);
                    if (audioPopup) audioPopup.style.display = 'flex';
                    recognition.start();
                }
            });
        }

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const queryInput = document.getElementById('query');
            if (queryInput) queryInput.value = transcript;
            stopMediaStream();
            if (audioPopup) audioPopup.style.display = 'none';
            if (searchForm) searchForm.submit();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            stopMediaStream();
            if (audioPopup) audioPopup.style.display = 'none';
        };

        recognition.onend = () => {
            stopMediaStream();
        };

        function stopMediaStream() {
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
                audioStream = null;
            }
        }

        if (voiceDoneBtn) {
            voiceDoneBtn.addEventListener('click', () => {
                stopMediaStream();
                try { recognition.stop(); } catch(e){}
                if (audioPopup) audioPopup.style.display = 'none';
            });
        }

        if (voiceCancelBtn) {
            voiceCancelBtn.addEventListener('click', () => {
                stopMediaStream();
                try { recognition.abort(); } catch(e){}
                if (audioPopup) audioPopup.style.display = 'none';
            });
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && audioPopup && audioPopup.style.display === 'flex') {
                stopMediaStream();
                try { recognition.abort(); } catch(e){}
                audioPopup.style.display = 'none';
            }
        });
    }

    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            const queryInput = document.getElementById('query');
            if (!queryInput || !queryInput.value.trim()) {
                event.preventDefault();
                return;
            }
            if (loadingPopup) loadingPopup.style.display = 'flex';
        });
    }
});

function changePlaceholder(text) {
    const input = document.getElementById('query');
    if (input && text) {
        input.placeholder = text;
    }
}

// Video Card Builder for "Other Lectures"
function createVideoCard(video, videolink) {
    const colDiv = document.createElement('div');
    colDiv.classList.add('col');

    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card', 'h-100', 'shadow-sm', 'border');

    const link = document.createElement('a');
    link.href = videolink;
    link.classList.add('position-relative', 'd-block');

    const img = document.createElement('img');
    img.src = video.thumbnail_url;
    img.alt = video.title || 'Lecture';
    img.classList.add('card-img-top', 'object-fit-cover');
    img.style.aspectRatio = '16/9';
    link.appendChild(img);

    const cardBodyDiv = document.createElement('div');
    cardBodyDiv.classList.add('card-body', 'p-3', 'd-flex', 'flex-column', 'justify-content-between');

    const title = document.createElement('h6');
    title.classList.add('card-title', 'mb-2', 'fw-bold', 'text-dark');
    title.textContent = shortenTextIfNecessary(video.title || `Lecture ${video.video_id}`, 60);

    const metaDiv = document.createElement('div');
    metaDiv.classList.add('small', 'text-muted');

    if (video.speaker) {
        const speaker = document.createElement('div');
        speaker.textContent = video.speaker;
        metaDiv.appendChild(speaker);
    }

    if (video.date) {
        const dateSmall = document.createElement('small');
        dateSmall.classList.add('text-muted');
        dateSmall.textContent = video.date;
        metaDiv.appendChild(dateSmall);
    }

    cardBodyDiv.appendChild(title);
    cardBodyDiv.appendChild(metaDiv);

    cardDiv.appendChild(link);
    cardDiv.appendChild(cardBodyDiv);
    colDiv.appendChild(cardDiv);

    return colDiv;
}

function shortenTextIfNecessary(text, maxLength) {
    if (!text) return '';
    if (text.length > maxLength) {
        return text.slice(0, maxLength - 2) + '...';
    }
    return text;
}