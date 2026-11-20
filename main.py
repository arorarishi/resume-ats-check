import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser
import uvicorn

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_free_port(start_port: int = 8765) -> int:
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def launch_desktop_window(url: str):
    """
    Attempts to open a clean standalone desktop app window without browser URL/navigation bars.
    Falls back to default system browser if standalone app mode is unavailable.
    """
    time.sleep(1.2)  # Wait for server to bind

    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe")
    ]

    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]

    for p in edge_paths + chrome_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={url}", "--window-size=1360,880"])
                print(f"[Desktop Launcher] Started native window with: {p}")
                return
            except Exception as e:
                print(f"[Desktop Launcher] Error launching app mode: {e}")

    # Fallback to default browser
    print("[Desktop Launcher] Standalone app mode not available; opening in default browser.")
    webbrowser.open(url)

def main():
    port = find_free_port(8765)
    url = f"http://127.0.0.1:{port}"
    print("=" * 60)
    print("   Resume ATS Check - Desktop App")
    print(f"   Starting UI at: {url}")
    print("=" * 60)

    # Spawn desktop window launcher in background thread
    launcher_thread = threading.Thread(target=launch_desktop_window, args=(url,), daemon=True)
    launcher_thread.start()

    # Start FastAPI / Uvicorn server
    uvicorn.run("app.server:app", host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    main()
