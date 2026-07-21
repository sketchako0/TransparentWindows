import tkinter as tk
import threading
import time
import win32gui
import win32con
import win32process

enabled = True
alpha = 180

# Processes to ignore
BLACKLIST = {
    "dwm.exe",
    "csrss.exe",
    "wininit.exe",
    "winlogon.exe",
    "smss.exe",
}


def get_process_name(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

        kernel32 = ctypes.windll.kernel32

        hProcess = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            pid
        )

        if not hProcess:
            return ""

        size = wintypes.DWORD(260)
        exe = ctypes.create_unicode_buffer(260)

        kernel32.QueryFullProcessImageNameW(
            hProcess,
            0,
            exe,
            ctypes.byref(size)
        )

        kernel32.CloseHandle(hProcess)

        return exe.value.split("\\")[-1].lower()

    except Exception:
        return ""


def apply(hwnd):
    if not enabled:
        return

    try:
        if not win32gui.IsWindowVisible(hwnd):
            return

        if win32gui.IsIconic(hwnd):
            return

        if hwnd == root.winfo_id():
            return

        title = win32gui.GetWindowText(hwnd)

        if not title.strip():
            return

        process = get_process_name(hwnd)

        if process in BLACKLIST:
            return

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

        if not (style & win32con.WS_EX_LAYERED):
            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                style | win32con.WS_EX_LAYERED
            )

        win32gui.SetLayeredWindowAttributes(
            hwnd,
            0,
            alpha,
            win32con.LWA_ALPHA
        )

    except Exception:
        pass


def restore(hwnd):
    try:
        if not win32gui.IsWindowVisible(hwnd):
            return

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

        if style & win32con.WS_EX_LAYERED:
            win32gui.SetLayeredWindowAttributes(
                hwnd,
                0,
                255,
                win32con.LWA_ALPHA
            )

    except Exception:
        pass


def worker():
    while True:
        if enabled:
            win32gui.EnumWindows(lambda h, _: apply(h), None)
        time.sleep(1)


def slider(value):
    global alpha
    alpha = int(value)


def toggle():
    global enabled

    enabled = not enabled

    if enabled:
        button.config(text="Disable")
    else:
        button.config(text="Enable")
        win32gui.EnumWindows(lambda h, _: restore(h), None)


root = tk.Tk()
root.title("Transparent Windows")
root.geometry("300x140")
root.resizable(False, False)

tk.Label(root, text="Transparency").pack(pady=5)

scale = tk.Scale(
    root,
    from_=30,
    to=255,
    orient="horizontal",
    command=slider,
    length=250
)
scale.set(alpha)
scale.pack()

button = tk.Button(root, text="Disable", command=toggle)
button.pack(pady=10)

threading.Thread(target=worker, daemon=True).start()

root.mainloop()