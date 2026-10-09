const customVideo = document.getElementById('custom-video');
const playPauseBtn = document.getElementById('play-pause-btn');
const seekBar = document.getElementById('seek-bar');
const muteUnmuteBtn = document.getElementById('mute-unmute-btn');
const volumeBar = document.getElementById('volume-bar');
const fullscreenBtn = document.getElementById('fullscreen-btn');
const linkList = typeof getLinks === 'function' ? getLinks() : [];
const MUTE = 0;
const LOUD = 1;
const CROSS = 2;
const PLAY = 3;
const PAUSE = 4;

const thisVideo = typeof getVideo === 'function' ? getVideo() : null;

// Graceful Empty State Handling
if (!thisVideo) {
    const noLecture = document.getElementById('noLectureState');
    const playerContainer = document.getElementById('lecturePlayerContainer');
    const breadcrumbTitle = document.getElementById('breadcrumbVideoTitle');
    if (noLecture) noLecture.style.display = 'block';
    if (playerContainer) playerContainer.style.display = 'none';
    if (breadcrumbTitle) breadcrumbTitle.textContent = 'No Lecture Selected';
} else {
    initVideoPage();
}

function initVideoPage() {
    function changeSrc(videoUrl) {
        if (!videoUrl) return;
        if (customVideo.canPlayType('application/vnd.apple.mpegurl')) {
            customVideo.src = videoUrl;
        } else if (typeof Hls !== 'undefined' && Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(videoUrl);
            hls.attachMedia(customVideo);
            hls.on(Hls.Events.MANIFEST_PARSED, function () {
                // Stream manifest ready
            });
        } else {
            console.warn('HLS stream reproduction might not be supported in this browser.');
        }
    }

    const chunks = Array.isArray(thisVideo.chunks) ? thisVideo.chunks : [];
    if (thisVideo.m3u8_url) {
        changeSrc(thisVideo.m3u8_url);
    }
    if (thisVideo.thumbnail_url) {
        customVideo.poster = thisVideo.thumbnail_url;
    }

    loadSubtitles();

    const titleEl = document.getElementById('title');
    if (titleEl) titleEl.textContent = thisVideo.title || `Lecture ${thisVideo.video_id}`;

    const breadcrumbTitle = document.getElementById('breadcrumbVideoTitle');
    if (breadcrumbTitle) breadcrumbTitle.textContent = thisVideo.title || `Lecture ${thisVideo.video_id}`;

    const langDisplay = thisVideo.language ? thisVideo.language : 'Multilingual';
    const topBadge = document.getElementById('topVideoLangBadge');
    if (topBadge) topBadge.textContent = `🌐 ${langDisplay} Lecture`;
    const playerAudioBadge = document.getElementById('playerAudioLangBadge');
    if (playerAudioBadge) playerAudioBadge.textContent = `Spoken Audio: ${langDisplay}`;
    const sidebarAudioBadge = document.getElementById('sidebarAudioLangBadge');
    if (sidebarAudioBadge) sidebarAudioBadge.textContent = `Audio: ${langDisplay}`;

    const speakerDateEl = document.getElementById('speaker+date');
    if (speakerDateEl) {
        let metaHtml = '';
        if (thisVideo.speaker) {
            metaHtml += `<span class="me-3"><strong>Speaker:</strong> ${thisVideo.speaker}</span>`;
        }
        if (thisVideo.date) {
            metaHtml += `<span><strong>Date:</strong> ${thisVideo.date}</span>`;
        }
        speakerDateEl.innerHTML = metaHtml;
    }

    const countBadge = document.getElementById('timestampsCountBadge');
    if (countBadge) countBadge.textContent = chunks.length;

    // Create lists for texts, start times, and end times
    const texts = chunks.map(chunk => chunk.text);
    const times = chunks.map(chunk => chunk.start);
    const ends = chunks.map(chunk => chunk.end);

    // Sideboard fly in
    let currentSideboard = null;
    let currentSideboardTimestamp = 0;
    let closechunk = true;

    function timestampDesc(time, text) {
        const sideboard = document.createElement("div");
        sideboard.className = "sideboardChunk";
        sideboard.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-primary font-monospace">⏱ Timestamp ${makeTimeString(time)}</span>
                <button type="button" class="btn-close btn-close-white" aria-label="Close" onclick="closeChunk()"></button>
            </div>
            <p class="transcript-detail-text mb-0">&ldquo;${text}&rdquo;</p>
        `;
        if (currentSideboard != null) {
            currentSideboard.style = "opacity: 0;";
        }
        currentSideboard = sideboard;
        currentSideboardTimestamp = time;
        closechunk = false;
        const playlist = document.getElementById('timestampPlaylist');
        if (playlist) {
            playlist.appendChild(sideboard);
            setTimeout(() => {
                sideboard.style.right = "0";
            }, 10);
        }
    }

    window.closeChunk = function () {
        closechunk = true;
        if (currentSideboard) {
            currentSideboard.style.right = "-150%";
        }
    };

    function updateSidebar() {
        if (currentSideboard == null) return;
        if (Math.abs(customVideo.currentTime - currentSideboardTimestamp) > 12) {
            currentSideboard.style.right = "-150%";
        } else if (closechunk === false) {
            currentSideboard.style.right = "0";
        }
    }

    // Play/Pause, Controls
    function pausePlay() {
        if (customVideo.paused) {
            customVideo.play();
            const playIcon = document.getElementById('playIcon');
            if (playIcon && linkList[PAUSE]) playIcon.src = linkList[PAUSE];
        } else {
            customVideo.pause();
            const playIcon = document.getElementById('playIcon');
            if (playIcon && linkList[PLAY]) playIcon.src = linkList[PLAY];
        }
    }

    function mute() {
        customVideo.muted = true;
        const volIcon = document.getElementById('volumeIcon');
        if (volIcon && linkList[MUTE]) volIcon.src = linkList[MUTE];
    }

    function unmute() {
        customVideo.muted = false;
        const volIcon = document.getElementById('volumeIcon');
        if (volIcon && linkList[LOUD]) volIcon.src = linkList[LOUD];
    }

    if (playPauseBtn) playPauseBtn.addEventListener('click', pausePlay);
    if (customVideo) customVideo.addEventListener('click', pausePlay);

    document.addEventListener('keydown', (e) => {
        if (e.code === "Space" && e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {
            e.preventDefault();
            pausePlay();
        }
    });

    if (seekBar) {
        seekBar.style.setProperty('--progress', '0%');
        seekBar.addEventListener('input', () => {
            if (customVideo.duration) {
                const time = (seekBar.value / 100) * customVideo.duration;
                customVideo.currentTime = time;
            }
        });
    }

    let volumeBeforeMute = 1.0;
    if (muteUnmuteBtn) {
        muteUnmuteBtn.addEventListener('click', () => {
            if (customVideo.muted) {
                unmute();
                if (volumeBar) volumeBar.value = volumeBeforeMute;
            } else {
                mute();
                if (volumeBar) {
                    volumeBeforeMute = volumeBar.value;
                    volumeBar.value = 0;
                }
            }
        });
    }

    if (volumeBar) {
        volumeBar.addEventListener('input', () => {
            customVideo.volume = volumeBar.value;
            if (customVideo.volume > 0) {
                unmute();
            } else {
                mute();
            }
        });
    }

    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => {
            const userAgent = navigator.userAgent.toLowerCase();
            if (userAgent.search(/(iphone|ipod|opera mini|fennec|palm|blackberry|android|symbian|series60)/) > -1 && customVideo.webkitEnterFullscreen) {
                customVideo.webkitEnterFullscreen();
            } else if (!document.fullscreenElement) {
                if (customVideo.requestFullscreen) customVideo.requestFullscreen();
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
            }
        });
    }

    // Active transcript highlighter
    function highlightActiveSegment(currentTime) {
        const items = document.querySelectorAll('.timestamp-item');
        items.forEach(item => {
            const start = parseFloat(item.getAttribute('data-start'));
            const end = parseFloat(item.getAttribute('data-end'));
            const activeTag = item.querySelector('.segment-active-tag');
            if (currentTime >= start && currentTime <= end) {
                item.classList.add('active-timestamp-segment');
                if (activeTag) activeTag.style.display = 'inline-block';
            } else {
                item.classList.remove('active-timestamp-segment');
                if (activeTag) activeTag.style.display = 'none';
            }
        });
    }

    // Loaded metadata: render markers and playlist
    customVideo.addEventListener('loadedmetadata', () => {
        const rangeContainer = document.getElementById('range+timestamps');

        for (let i = 0; i < times.length; i++) {
            if (rangeContainer && customVideo.duration) {
                const seekBarWidth = seekBar ? seekBar.clientWidth : 200;
                const timestampDot = document.createElement("div");
                timestampDot.className = "timestamp";
                const distance = times[i] / customVideo.duration;
                timestampDot.style.left = `${distance * 100}%`;
                timestampDot.title = `⏱ ${makeTimeString(times[i])}: ${texts[i]}`;

                timestampDot.addEventListener('click', (e) => {
                    e.stopPropagation();
                    customVideo.currentTime = times[i];
                    timestampDesc(times[i], texts[i]);
                    highlightActiveSegment(times[i]);
                });
                rangeContainer.appendChild(timestampDot);
            }
            addListTimestamp(times[i], ends[i], texts[i], i);
        }

        // If URL has target timestamp 't', jump immediately
        const urlParams = new URLSearchParams(window.location.search);
        const tParam = parseFloat(urlParams.get('t'));
        if (!isNaN(tParam) && tParam >= 0) {
            customVideo.currentTime = tParam;
            highlightActiveSegment(tParam);
        }

        // Update video playtime
        const timeDisplay = document.getElementById('videozeit');
        if (timeDisplay) {
            timeDisplay.innerHTML = `${makeTimeString(customVideo.currentTime)} / ${makeTimeString(customVideo.duration)}`;
        }

        customVideo.addEventListener('timeupdate', () => {
            if (customVideo.duration) {
                const value = (customVideo.currentTime / customVideo.duration) * 100;
                if (seekBar) {
                    seekBar.value = value;
                    seekBar.style.setProperty('--progress', `${value}%`);
                }
            }
            updateSidebar();
            highlightActiveSegment(customVideo.currentTime);
            if (timeDisplay) {
                timeDisplay.innerHTML = `${makeTimeString(customVideo.currentTime)} / ${makeTimeString(customVideo.duration)}`;
            }
        });
    });

    // Make Format 00:00 to 1:23:01
    function makeTimeString(time) {
        if (isNaN(time) || time === null) return "0:00";
        const sec = Math.floor(time);
        const hrs = Math.floor(sec / 3600);
        const mins = Math.floor((sec % 3600) / 60);
        const remainingSec = sec % 60;
        const mm = String(mins).padStart(2, '0');
        const ss = String(remainingSec).padStart(2, '0');
        if (hrs > 0) {
            return `${hrs}:${mm}:${ss}`;
        }
        return `${mins}:${ss}`;
    }

    // Adds timestamp item to playlist
    function addListTimestamp(time, endTime, text, index) {
        const playlist = document.getElementById('timestampPlaylist');
        if (!playlist) return;

        const listTimestamp = document.createElement("div");
        listTimestamp.className = "timestamp-item p-3 border-bottom";
        listTimestamp.id = `timestamp-item-${index}`;
        listTimestamp.setAttribute('data-start', time);
        listTimestamp.setAttribute('data-end', endTime || (time + 12));

        listTimestamp.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace small px-2 py-1">
                    ⏱ ${makeTimeString(time)}
                </span>
                <span class="segment-active-tag badge bg-success text-white small" style="display: none;">
                    ▶ Playing
                </span>
            </div>
            <div class="timestamp-text text-dark">${text}</div>
        `;

        listTimestamp.addEventListener('click', () => {
            customVideo.currentTime = time;
            if (customVideo.paused) customVideo.play();
            timestampDesc(time, text);
            highlightActiveSegment(time);
        });

        playlist.appendChild(listTimestamp);
    }

    // Subtitles handling
    const subtitleBtn = document.querySelector('.subtitle-btn');
    const settingsMenu = document.getElementById('settings-menu');
    const subtitleLanguage = document.getElementById('subtitle-language');
    let menuTimeout;

    if (subtitleBtn && settingsMenu) {
        subtitleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            this.classList.toggle('active');
            const track = customVideo.textTracks && customVideo.textTracks[0];
            if (track) {
                if (track.mode === 'showing') {
                    track.mode = 'hidden';
                    this.classList.remove('active');
                } else {
                    track.mode = 'showing';
                    this.classList.add('active');
                    settingsMenu.style.display = settingsMenu.style.display === 'block' ? 'none' : 'block';
                    resetMenuTimeout();
                }
            } else {
                settingsMenu.style.display = settingsMenu.style.display === 'block' ? 'none' : 'block';
                resetMenuTimeout();
            }
        });

        settingsMenu.addEventListener('mouseover', function (e) {
            e.stopPropagation();
            resetMenuTimeout();
        });
        settingsMenu.addEventListener('click', function (e) {
            e.stopPropagation();
            resetMenuTimeout();
        });
    }

    if (subtitleLanguage) {
        subtitleLanguage.addEventListener('change', function () {
            const val = this.value;
            if (val === 'none') {
                if (customVideo.textTracks && customVideo.textTracks[0]) {
                    customVideo.textTracks[0].mode = 'hidden';
                }
                const track = customVideo.querySelector('track');
                if (track) track.remove();
                if (settingsMenu) settingsMenu.style.display = 'none';
                return;
            }

            const labelMap = {
                en: 'English',
                nl: 'Nederlands',
                ta: 'தமிழ்',
                ml: 'മലയാളം',
                hi: 'हिन्दी',
                de: 'Deutsch'
            };

            let subPath = `/transcription/subtitles/${thisVideo.video_id}_subtitles_${val}.srt`;
            if (val === 'en') {
                subPath = thisVideo.eng_sub || `/transcription/subtitles/${thisVideo.video_id}_subtitles.srt`;
            } else if (val === 'de') {
                subPath = thisVideo.ger_sub || `/transcription/subtitles/${thisVideo.video_id}_subtitles_de.srt`;
            }

            const langLabel = labelMap[val] || val.toUpperCase();
            customVideo.innerHTML = `<track id="subtitleTrack" kind="subtitles" src="/api/convert_srt_to_vtt?srt_path=${subPath}" srclang="${val}" label="${langLabel}">`;
            
            const newTrackEl = customVideo.querySelector('track');
            if (newTrackEl) {
                newTrackEl.addEventListener('error', () => {
                    console.info(`Subtitles for [${val}] not available for this lecture.`);
                });
            }

            if (customVideo.textTracks && customVideo.textTracks[0]) {
                customVideo.textTracks[0].mode = 'showing';
            }
            if (settingsMenu) settingsMenu.style.display = 'none';
        });
    }

    function resetMenuTimeout() {
        clearTimeout(menuTimeout);
        menuTimeout = setTimeout(hideMenu, 4000);
    }
    function hideMenu() {
        if (settingsMenu) settingsMenu.style.display = 'none';
    }

    function loadSubtitles() {
        const defaultSub = thisVideo.eng_sub || `/transcription/subtitles/${thisVideo.video_id}_subtitles.srt`;
        customVideo.innerHTML = `<track id="subtitleTrack" kind="subtitles" src="/api/convert_srt_to_vtt?srt_path=${defaultSub}" srclang="en" label="English">`;
        const trackEl = customVideo.querySelector('track');
        if (trackEl) {
            trackEl.addEventListener('error', () => {
                // Silently fallback if initial subtitle track is absent
                console.info('Default subtitles not present for this lecture.');
            });
        }
    }
}
