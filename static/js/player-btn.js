const details = document.querySelector("#HiddenDetails").getAttribute("data-details")

if (details !== null) {
  const skipPreviousButton = document.getElementById("skipPreviousButton");
  const skipNextButton = document.getElementById("skipNextButton");

  const HiddenDiv = document.getElementById("hidden");
  let isPlaying = null;
  if (HiddenDiv) {
    isPlaying = HiddenDiv.getAttribute("data-is-playing");
  }

  let playORpause = null;
  if (isPlaying === 'True') {
    playORpause = document.getElementById("pauseButton");
  } else {
    playORpause = document.getElementById("playButton");
  }

  skipPreviousButton.addEventListener("click", function () {
    skipPrevious();
  });

  skipNextButton.addEventListener("click", function () {
    skipNext();
  });

  playORpause.addEventListener("click", function (){
    togglePlayback();
  })


  function togglePlayback() {
    if (isPlaying === 'True') {
      pausePlayback();
      isPlaying = 'False';
    } else {
      startPlayback();
      isPlaying = 'True';
    }
    document.getElementById("hidden").setAttribute("data-is-playing", isPlaying);
  }


  function startPlayback() {
    fetch("/start", {
      method: "PUT",
    }).then((response) => {
      if (response.ok) {
        console.log("PLAYBACK HAS STARTED");
        const icon = document.querySelector(".fa-play");
        if (icon) {
          icon.classList.remove("fa-play");
          icon.classList.add("fa-pause");  
        }
        const btn = document.querySelector("#playButton");
        if (btn) {
          btn.removeAttribute("id");
          btn.setAttribute("id","pauseButton");
        }
      } else {
        console.error("ERROR STARTING PLAYBACK");
      }
    });
  }

  function pausePlayback() {
    fetch("/pause", {
      method: "PUT",
    }).then((response) => {
      if (response.ok) {
        console.log("PLAYBACK HAS BEEN PAUSED");
        const icon = document.querySelector(".fa-pause");
        if (icon) {
          icon.classList.remove("fa-pause");
          icon.classList.add("fa-play");
        }
        const btn = document.querySelector("#pauseButton");
        if (btn) {
          btn.removeAttribute("id");
          btn.setAttribute("id","playButton");
        }
      } else {
        console.error("ERROR PAUSING PLAYBACK");
      }
    });
  }

  function skipNext() {
    fetch("/skipnext", {
      method: "POST",
    }).then((response) => {
      if (response.ok) {
        console.log("Skipped to the next song");
        const pauseBtn = document.querySelector("#pauseButton");
        if(pauseBtn === null) {
          const icon = document.querySelector(".fa-play");
          icon.classList.remove("fa-play");
          icon.classList.add("fa-pause");
          const btn = document.querySelector("#playButton");
          btn.removeAttribute("id");
          btn.setAttribute("id","pauseButton");
        }

        updatePlaybackState();

      } else {
        console.error("Error skipping to the next song");
      }
    });
  }

  function skipPrevious() {
    fetch("/skipprevious", {
      method: "POST",
    }).then((response) => {
      if (response.ok) {
        console.log("Skipped to the previous song");
        const pauseBtn = document.querySelector("#pauseButton");
        if(pauseBtn === null) {
          const icon = document.querySelector(".fa-play");
          icon.classList.remove("fa-play");
          icon.classList.add("fa-pause");
          const btn = document.querySelector("#playButton");
          btn.removeAttribute("id");
          btn.setAttribute("id","pauseButton");
        }

        updatePlaybackState();

      } else {
        console.error("Error skipping to the previous song");
      }
    });
  }

  function updatePlaybackState() {
    fetch("/playback-state")
          .then((response) => response.json())
          .then((data) => {
            updateUI(data); 
          })
          .catch((error) => {
            console.error("Error: ", error);
          })
  }


  function updateUI(data) {
    document.getElementById("currentlyTitle").innerText = data.song_name;
    document.getElementById("currentlyArtist").innerText = data.artist;
    document.getElementById("currentlyDuration").innerText = data.duration;
    document.getElementById("currentlyCover").src = data.image;
    console.log(data);
  }

  async function fetchPlaybackState() {
    try {
        const response = await fetch("/playback-state");
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            throw new Error("Failed to fetch playback state");
        }
    } catch (error) {
        console.error("Error fetching playback state:", error);
        throw error;
    }
  }

  let intervalId;
  function lookingEndSong() {
    intervalId = setInterval(async () => {
      try {
        const currentPlaybackState = await fetchPlaybackState();
        const { progress, duration_ms } = currentPlaybackState;
        const remainingTime = duration_ms - progress;
        console.log("Checking->Current position: ", remainingTime);
        var once = 1;
        if (remainingTime <= 1000 && once == 1) {
          console.log("UPDATING PLAYBACK STATE!!!");
          once --;
          updatePlaybackState();
        }
      } catch(error) {

      }
    }, 1000);
  }

  ///console.log(playORpause);
  ///console.log(isPlaying);

  if (isPlaying === 'True') {
    lookingEndSong();
    ///console.log(isPlaying);
  } 

  playORpause.addEventListener('click', function(){
    if(isPlaying === 'True') {
      lookingEndSong();
      ///console.log(isPlaying);
    } else {
      clearInterval(intervalId);
      ///console.log(isPlaying);
    }
  }); 

}


