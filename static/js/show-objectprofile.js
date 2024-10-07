function ObjectProfile(profile_type, id) {
    if(profile_type == 'album') {
        window.location.href = '/album/' + id;
    } else if(profile_type == 'playlist') {
        window.location.href = '/playlist/' + id;
    }  else if(profile_type == 'single') {
        window.location.href = '/single/' + id;
    } else if(profile_type == 'artist') {
        window.location.href = '/artist/' + id;
    }
}