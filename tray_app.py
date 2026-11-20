"""
System tray controller for the ATS Resume Tracker server.

Launched by ATS.bat (via pythonw, no console window). Shows a tray icon
that is GREEN while the server is running and RED while it is stopped,
with a right-click menu to Start / Stop the server, open the app in the
browser, or exit the tray (which also stops the server).

Server state is tracked via an in-process Popen handle (poll/terminate/wait)
so status checks and shutdown are instant, with a one-time PID-file/port
fallback at startup to adopt a server left running by a previous session.
"""
import os
import subprocess
import time
import socket
import webbrowser
import threading

import pystray
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
URL = f"http://127.0.0.1:{PORT}"

PID_FILE = os.path.join(ROOT, "server.pid")
LOG_FILE = os.path.join(ROOT, "server.log")
ERR_LOG_FILE = os.path.join(ROOT, "server.err.log")
VENV_PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

GREEN = (34, 197, 94)
RED = (239, 68, 68)

CREATE_NO_WINDOW = 0x08000000
LOCK_PORT = PORT + 1  # held for the tray's lifetime as a single-instance guard

_lock_socket = None
_proc = None  # the uvicorn subprocess.Popen this tray instance owns
_lock = threading.Lock()


def acquire_single_instance_lock() -> bool:
    """Binds a loopback port for this process's lifetime so a second tray
    instance (e.g. double-launching ATS.bat) can detect one is already running."""
    global _lock_socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", LOCK_PORT))
    except OSError:
        sock.close()
        return False
    _lock_socket = sock  # keep alive; never closed until process exit
    return True


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _adopt_stray_server_at_startup():
    """One-time check (not on the hot path): if server.pid points at a live
    process, or something else is already listening on our port, leave it
    alone and just remember that a server is up so we don't launch a second
    one. We don't hold a Popen handle for it, so Stop/Exit fall back to
    taskkill only in this adopted case."""
    if os.path.exists(PID_FILE):
        try:
            pid = int(open(PID_FILE).read().strip())
        except (ValueError, OSError):
            pid = None
        if pid:
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True, text=True, creationflags=CREATE_NO_WINDOW,
                    timeout=5,
                )
                if str(pid) in result.stdout:
                    return True
            except Exception:
                pass
    return is_port_in_use(PORT)


_adopted_stray_server = False  # set once at startup if we didn't launch the server ourselves


def is_server_running() -> bool:
    if _proc is not None:
        return _proc.poll() is None
    return _adopted_stray_server


def start_server():
    global _proc
    with _lock:
        if is_server_running():
            return
        if not os.path.exists(VENV_PYTHON):
            return
        log_out = open(LOG_FILE, "a")
        log_err = open(ERR_LOG_FILE, "a")
        _proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "uvicorn", "app.server:app", "--host", "127.0.0.1", "--port", str(PORT)],
            cwd=ROOT, stdout=log_out, stderr=log_err,
            creationflags=CREATE_NO_WINDOW,
        )
        with open(PID_FILE, "w") as f:
            f.write(str(_proc.pid))


def stop_server():
    global _proc, _adopted_stray_server
    with _lock:
        if _proc is not None:
            if _proc.poll() is None:
                _proc.terminate()
                try:
                    _proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    _proc.kill()
                    _proc.wait(timeout=5)
            _proc = None
        elif _adopted_stray_server:
            # We never held a handle for this one (started by a previous
            # session) - fall back to taskkill by PID/port.
            pid = None
            if os.path.exists(PID_FILE):
                try:
                    pid = int(open(PID_FILE).read().strip())
                except (ValueError, OSError):
                    pid = None
            if pid:
                try:
                    subprocess.run(
                        ["taskkill", "/PID", str(pid), "/T", "/F"],
                        creationflags=CREATE_NO_WINDOW, timeout=5,
                    )
                except Exception:
                    pass
            _adopted_stray_server = False

        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass


def make_icon_image(color):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((6, 6, 58, 58), fill=color, outline=(15, 23, 42, 255), width=3)
    return img


def refresh(icon: pystray.Icon):
    running = is_server_running()
    icon.icon = make_icon_image(GREEN if running else RED)
    icon.title = f"ATS Resume Tracker - {'Running' if running else 'Stopped'}"
    icon.update_menu()


def on_open(icon, item):
    webbrowser.open(URL)


def on_toggle(icon, item):
    if is_server_running():
        stop_server()
    else:
        start_server()
    refresh(icon)


def on_exit(icon, item):
    icon.visible = False
    stop_server()
    icon.stop()


def monitor_loop(icon: pystray.Icon):
    while True:
        time.sleep(2)
        try:
            refresh(icon)
        except Exception:
            pass


def build_menu():
    return pystray.Menu(
        pystray.MenuItem("Open ATS Tracker", on_open, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda item: "\U0001F534 Stop Server" if is_server_running() else "\U0001F7E2 Start Server",
            on_toggle,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit),
    )


def setup(icon: pystray.Icon):
    global _adopted_stray_server
    icon.visible = True
    if not is_port_in_use(PORT):
        start_server()
    else:
        _adopted_stray_server = _adopt_stray_server_at_startup()
    refresh(icon)
    webbrowser.open(URL)
    threading.Thread(target=monitor_loop, args=(icon,), daemon=True).start()


def main():
    if not acquire_single_instance_lock():
        # A tray instance is already running; just surface the app instead of
        # starting a second icon/monitor loop.
        webbrowser.open(URL)
        return

    icon = pystray.Icon(
        "ats_resume_tracker",
        icon=make_icon_image(RED),
        title="ATS Resume Tracker",
        menu=build_menu(),
    )
    icon.run(setup=setup)


if __name__ == "__main__":
    main()
