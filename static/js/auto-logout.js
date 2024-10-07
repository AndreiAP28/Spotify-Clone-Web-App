var Timeout = 24 * 60 * 60 * 1000;
var logoutTimer;

function resetTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(autoLogout, Timeout);
}

function autoLogout() {
    window.location.href = '/logout';
}

document.addEventListener('mousemove', resetTimer);
document.addEventListener('keypress', resetTimer);

resetTimer();