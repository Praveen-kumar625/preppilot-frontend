// PrePilot has no account server yet. Login and Register therefore work
// entirely in the browser: the details are validated on the client and kept
// in localStorage on this device only. Nothing is sent to a server, and no
// real account is created. Replace these helpers with real API calls when a
// backend auth service exists.

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
