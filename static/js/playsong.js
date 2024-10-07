function playSong(URI) {
    fetch('/play_song', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify ({song_uri: URI})
    })
    .then(response => {
        if(response.ok) {
            updatePlaybackState();
        } else {
            console.error("ERROR PLAYING SONG");
        }
    })
    .catch(error => {
        console.error("Error: ", error);
    })
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


