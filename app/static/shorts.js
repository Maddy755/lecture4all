const short = document.getElementById('currentShort');
const metaDaten = document.querySelector('.meta-daten');
const videoButton = document.getElementById('videoButton');
const sideboard = document.querySelector('.sideboard');
const resultsJS = getResultsJS();

    document.getElementById('right').addEventListener('click', skipVideo);
    document.getElementById('left').addEventListener('click', videoBack);
    // Konfiguration

    const chunks = resultsJS.flatMap(video =>
        video.chunks.map(chunk => ({
            url: video.m3u8_url,
            videoId: video.video_id,
            title: video.title,
            speaker: video.speaker,
            date: video.date,
            text: chunk.text,
            rank: chunk.chunk_rank,
            start: chunk.start,
            end: chunk.end
        }))
    );

    // Chunks nach Rank sortieren
    const sortedChunks = chunks.sort((a, b) => a.rank - b.rank);

    let currentIndex = 0;

    function changeSrc(videoUrl) 
    {
        if (!videoUrl) return;
        const isHls = videoUrl.includes('.m3u8') || videoUrl.includes('.smil');
        if (!isHls) {
            short.src = videoUrl;
            return;
        }
        if (short.canPlayType('application/vnd.apple.mpegurl')) {
            short.src = videoUrl;
        } else if (Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(videoUrl);
            hls.attachMedia(short);
            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                // auszuführen wenn geladen evtl loadedmetadata hier rein
            });
        } else {
            alert('Dein Browser unterstützt leider keine Wiedergabe von HLS-Streams.');
        }
    }

    // Aktualisieren des Iframes und Sideboards
    function updateUI(index) {
        const chunk = sortedChunks[index];
        changeSrc(chunk.url);
        short.currentTime = chunk.start;
        //metaDaten.innerHTML = `<h5>${chunk.title}</h5><p>${chunk.speaker} <br> ${chunk.date}</p>`;
        videoButton.href = `${getVideoUrl()}?video_id=${chunk.videoId}`;
        sideboard.innerHTML = `<h3>${chunk.title}</h3><h5>${chunk.speaker}</h5><h6>${chunk.date}</h6><br><p>...${chunk.text}...</p>`;
        short.play();
    }
    updateUI(0);

    function skipVideo() {
        if (currentIndex < sortedChunks.length - 1) {
            currentIndex++;
            updateUI(currentIndex);
        }
    }

    function videoBack() {
        if (currentIndex > 0) {
            currentIndex--;
            updateUI(currentIndex);
        }
    }
    short.addEventListener('click', () => {
        if (short.paused) {
            short.play();
        } else {
            short.pause();
        }
    });
    

    // Mobileview
    const MOVE_THRESHOLD = 100;

    let initialX = 0;
    let moveX = 0;
    let isDeleteButtonOpen = false;

    document.addEventListener("touchstart", e => {
        initialX = e.touches[0].pageX;
    });
    document.addEventListener("touchmove", e => {
        let currentX = e.touches[0].pageX;
        moveX = currentX - initialX;
    });
    document.addEventListener("touchend", e => {
        if (moveX < MOVE_THRESHOLD * (-1)) {
            // Swipe right
            skipVideo();
        } else if (moveX > MOVE_THRESHOLD ) {
            // Swipe left
            videoBack();
        }

        moveX = 0;
    });

      // Add play button overlay
    const playOverlay = document.createElement('div');
    playOverlay.id = 'play-overlay';
    playOverlay.style = 'position:absolute;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;z-index:20;pointer-events:none;';
    playOverlay.innerHTML = `
      <button id="play-btn-overlay" style="
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: none;
        background: rgba(114, 55, 106, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: auto;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        padding: 0;
      ">
        <svg width="40" height="40" viewBox="0 0 40 40" style="display:block;margin:auto;" xmlns="http://www.w3.org/2000/svg">
          <polygon points="12,8 32,20 12,32" fill="white" />
        </svg>
      </button>
    `;
    short.parentElement.style.position = 'relative';
    short.parentElement.appendChild(playOverlay);

    const playBtnOverlay = document.getElementById('play-btn-overlay');
    playOverlay.style.display = short.paused ? 'flex' : 'none';

    playBtnOverlay.addEventListener('click', function(e) {
        e.stopPropagation();
        short.play().then(() => {
            playOverlay.style.display = 'none';
        });
    });

    short.addEventListener('play', () => {
        playOverlay.style.display = 'none';
    });
    short.addEventListener('pause', () => {
        playOverlay.style.display = 'flex';
    });
