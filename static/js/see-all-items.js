function showAll(category){
    if(category == 'tracks'){
        window.location.href = '/see-all?category=tracks';
    } else if (category == 'artists'){
        window.location.href = '/see-all?category=artists';
    } else if (category == 'your-playlists') {
        window.location.href = '/see-all?category=your-playlists';
    } else if (category == 'liked-playlists') {
        window.location.href = '/see-all?category=liked-playlits'; 
    }
}

