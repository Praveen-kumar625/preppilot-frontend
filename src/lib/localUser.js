// PrePilot has no account server yet. So Login and Register work only in
// the browser: the details are checked here and kept in localStorage on
// this device only. Nothing is sent to a server, and no real account is
// made. Change these helpers to real API calls when a login backend is built.

const STORAGE_KEY = "preppilot_user";

export function getLocalUser() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

export function saveLocalUser(user) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function clearLocalUser() {
    localStorage.removeItem(STORAGE_KEY);
}

export function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
