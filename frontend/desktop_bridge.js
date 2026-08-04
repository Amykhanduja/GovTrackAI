// Intercepts API calls and routes them through Tauri IPC if running in desktop mode
if (window.__TAURI__) {
    console.log("GovTrack AI Desktop Environment Detected.");
    
    const { invoke } = window.__TAURI__.tauri;
    const { sendNotification } = window.__TAURI__.notification;

    window.notifyDesktop = (title, body) => {
        sendNotification({ title: title, body: body });
    };

    // Override fetch for desktop-specific local routing if necessary
    // Example: fetch('http://127.0.0.1:8000/api/v1/jobs')
}
