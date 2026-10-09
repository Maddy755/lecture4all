const customVideo = document.getElementById('custom-video');
const playPauseBtn = document.getElementById('play-pause-btn');
const seekBar = document.getElementById('seek-bar');
const muteUnmuteBtn = document.getElementById('mute-unmute-btn');
const volumeBar = document.getElementById('volume-bar');
const fullscreenBtn = document.getElementById('fullscreen-btn');
const linkList = getLinks();
const MUTE = 0;
const LOUD = 1;
const CROSS = 2;
const PLAY = 3;
const PAUSE = 4;

const thisVideo = getVideo();

function changeSrc(videoUrl) 
{
    if (customVideo.canPlayType('application/vnd.apple.mpegurl')) {
        customVideo.src = videoUrl;
    } else if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(videoUrl);
        hls.attachMedia(customVideo);
        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            // auszuführen wenn geladen evtl loadedmetadata hier rein
        });
    } else {
        alert('Dein Browser unterstützt leider keine Wiedergabe von HLS-Streams.');
    }
}

const chunks = thisVideo.chunks;
changeSrc(thisVideo.m3u8_url);
customVideo.poster = thisVideo.thumbnail_url;
loadSubtitles();
document.getElementById('title').innerHTML = thisVideo.title;
document.getElementById('speaker+date').innerHTML = thisVideo.speaker + "<br>" + thisVideo.date;

// Create lists for texts times and ends of chunks
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
    sideboard.innerHTML = `<button style="border: none; background: none;" onclick="closeChunk()"><img src="${linkList[CROSS]}" alt="exit" style="height: 32px; position: absolute; right: 1rem; top: 1rem;"></button>
    <h3 style="line-height: 1.5;">Timestamp ${makeTimeString(time)}</h3> 
    <p style="text-align: justify;">...${text}...</p>`;
    if (currentSideboard != null) {
        currentSideboard.style = "opacity: 0;";
    }
    currentSideboard = sideboard;
    currentSideboardTimestamp = time;
    closechunk = false;
    sideboard.style.height = `${document.getElementById('timestampPlaylist').scrollHeight}px`;
    console.log(document.getElementById('timestampPlaylist').scrollHeight);
    document.getElementById('timestampPlaylist').appendChild(sideboard);
}

function closeChunk() {
    closechunk = true;
    currentSideboard.style = "right: -150%;";
}

function updateSidebar() {
    if (currentSideboard == null) {
        return;
    }
    if (Math.abs(customVideo.currentTime - currentSideboardTimestamp) > 10) {
        currentSideboard.style = "right: -150%;";
    } else if (closechunk == false) {
        currentSideboard.style = "right: 0;";
    }
}
// End Sideboard fly in

// Play/Pause, Controls
function pausePlay() {
    if (customVideo.paused) {
        customVideo.play();
        document.getElementById('playIcon').src = `${linkList[PAUSE]}`;
    } else {
        customVideo.pause();
        document.getElementById('playIcon').src = `${linkList[PLAY]}`;
    }
}
function mute() {
    customVideo.muted = true;
    document.getElementById('volumeIcon').src = `${linkList[MUTE]}`;
}

function unmute() {
    customVideo.muted = false;
    document.getElementById('volumeIcon').src = `${linkList[LOUD]}`;
}

playPauseBtn.addEventListener('click', pausePlay);
customVideo.addEventListener('click', pausePlay);
document.addEventListener('keydown', (e) => {
    if (e.code === "Space") {
        pausePlay();
    }
});

seekBar.style.setProperty('--progress', 0);
seekBar.addEventListener('input', () => {
    const time = (seekBar.value / 100) * customVideo.duration;
    customVideo.currentTime = time;
});

let volumeBeforeMute = 1.0;
muteUnmuteBtn.addEventListener('click', () => {
    if (customVideo.muted) {
        unmute();
        volumeBar.value = volumeBeforeMute;
    } else {
        mute();
        volumeBeforeMute = volumeBar.value;
        volumeBar.value = 0;
    }
});
volumeBar.addEventListener('input', () => {
    customVideo.volume = volumeBar.value;
    if (customVideo.volume > 0) {
        unmute();
    } else {
        mute();
    }
});

fullscreenBtn.addEventListener('click', () => {
    var UserAgent = navigator.userAgent.toLowerCase();
    if (UserAgent.search(/(iphone|ipod|opera mini|fennec|palm|blackberry|android|symbian|series60)/) > -1) {
        customVideo.webkitEnterFullscreen(); // iOS-spezifische Methode
    } 
    // Auf Desktop: Standard-Fullscreen-API nutzen
    else if (!document.fullscreenElement) {
        customVideo.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
});

customVideo.addEventListener('loadedmetadata', () => {
    // make timestamps
    for (let i = 0; i < times.length; i++) {
        const seekBarWidth = seekBar.clientWidth;
        const timestamp = document.createElement("div");
        timestamp.className = "timestamp";
        let distance = times[i] / customVideo.duration;
        timestamp.style.left = `${distance * (seekBarWidth - 12)}px`;

        timestamp.addEventListener('click', () => {
            customVideo.currentTime = times[i];
            timestampDesc(times[i], texts[i]);
        });
        addListTimestamp(times[i], texts[i]);
        document.getElementById('range+timestamps').appendChild(timestamp);
    }
    // Update Videoplaytime
    document.getElementById('videozeit').innerHTML = `${makeTimeString(customVideo.currentTime)} / ${makeTimeString(customVideo.duration)}`;
    customVideo.addEventListener('timeupdate', () => {
        const value = (customVideo.currentTime / customVideo.duration) * 100;
        seekBar.value = value;
        updateSidebar();
        const progress = (customVideo.currentTime / customVideo.duration) * 100;
        seekBar.style.setProperty('--progress', `${progress}%`);
        document.getElementById('videozeit').innerHTML = `${makeTimeString(customVideo.currentTime)} / ${makeTimeString(customVideo.duration)}`;
    });
});

// Make Format 00:00 to 1:23:01
function makeTimeString(time) {
    const isoString = new Date(time * 1000).toISOString();
    const hours = isoString.slice(11, 13);
    const minutesAndSeconds = isoString.slice(14, 19);

    if (hours === "00") {
        return minutesAndSeconds;
    } else {
        return `${parseInt(hours, 10)}:${minutesAndSeconds}`;
    }
}

// Adds timestamps to List
function addListTimestamp(time, text) {
    const listTimestamp = document.createElement("div");
    listTimestamp.className = "timestamp-item d-flex justify-content-between align-items-center p-3 border-bottom";
    listTimestamp.innerHTML = `
        <div class="timestamp-text">${shortenTextIfNecessary(text, 50)}</div>
        <div class="timestamp-time">${makeTimeString(time)}</div>
    `;
    listTimestamp.addEventListener('click', () => {
        customVideo.currentTime = time;
        timestampDesc(time, text);
    });
    document.querySelector('.timestamps-container').appendChild(listTimestamp);
}

const subtitleBtn = document.querySelector('.subtitle-btn');
let subtitleTrack = customVideo.textTracks[0];

const settingsMenu = document.getElementById('settings-menu');
const subtitleLanguage = document.getElementById('subtitle-language');
let menuTimeout;

subtitleBtn.addEventListener('click', function(e) {
    this.classList.toggle('active');
    if (subtitleTrack.mode === 'showing') {
        subtitleTrack.mode = 'hidden';
        this.classList.remove('active');
    } else {
        subtitleTrack.mode = 'showing';
        this.classList.add('active');
        settingsMenu.style.display = settingsMenu.style.display === 'block' ? 'none' : 'block';
        resetMenuTimeout();
    }
});
settingsMenu.addEventListener('mouseover', function(e) {
    e.stopPropagation();
    resetMenuTimeout();
});
settingsMenu.addEventListener('click', function(e) {
    e.stopPropagation();
    resetMenuTimeout();
});

subtitleLanguage.addEventListener('click', function(e) {
    e.stopPropagation();
    resetMenuTimeout();
});
subtitleLanguage.addEventListener('change', function(e) {
    switch (this.value) {
        case 'de':
            subtitleTrack.mode = 'hidden';
            customVideo.innerHTML = `<track id="subtitleTrack" kind="subtitles" src="/api/convert_srt_to_vtt?srt_path=${thisVideo.ger_sub}" srclang="de" label="Deutsch">`
            subtitleTrack = customVideo.textTracks[0];
            subtitleBtn.click();
            break;

        case 'en':
            subtitleTrack.mode = 'hidden';
            customVideo.innerHTML = `<track id="subtitleTrack" kind="subtitles" src="/api/convert_srt_to_vtt?srt_path=${thisVideo.eng_sub}" srclang="en" label="English">`
            subtitleTrack = customVideo.textTracks[0];
            subtitleBtn.click();
            break;
    }
});
    
function resetMenuTimeout() {
    clearTimeout(menuTimeout);
    menuTimeout = setTimeout(hideMenu, 4000); // 4000ms = nach 4 Sekunden schließen
}
function hideMenu() {
    settingsMenu.style.display = 'none';
}

// Deutsch ausgrauen falls untertitel nicht verfügbar
async function checkSubsAvailable() {
    try {
        const response = await fetch(`/api/convert_srt_to_vtt?srt_path=${thisVideo.ger_sub}`, {
            method: 'HEAD'
        });
        if(!response.ok)
        {
            const germanOption = subtitleLanguage.querySelector('option[value="de"]');
            germanOption.disabled = true;
        }
    }
    catch(e){
        //...
    }
    try {
        const response = await fetch(`/api/convert_srt_to_vtt?srt_path=${thisVideo.eng_sub}`, {
            method: 'HEAD'
        });
        if(!response.ok)
        {
            const englishOption = subtitleLanguage.querySelector('option[value="en"]');
            englishOption.disabled = true;
        }
    }
    catch(e){
        //...
    }
}
checkSubsAvailable();
function loadSubtitles() {
    customVideo.innerHTML = `<track id="subtitleTrack" kind="subtitles" src="/api/convert_srt_to_vtt?srt_path=${thisVideo.eng_sub}" srclang="en" label="English">`
}
// pausePlay(); // Autostart
