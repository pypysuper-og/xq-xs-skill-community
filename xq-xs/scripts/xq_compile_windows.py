"""Windows-only desktop adapter. Compiles isolated scripts; never runs a strategy.

The temporary target-process buffer below is non-executable and is used only as
the output buffer of Scintilla's documented SCI_GETTEXT message. No remote code,
threads, DLL injection, database writes, or existing-script edits are performed.
"""
from __future__ import annotations

import ctypes as C
from ctypes import wintypes as W
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import re
import struct
import time


@contextmanager
def desktop_lock():
    """One native mutex for the whole compile/poll operation in this session."""
    kernel = C.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes, kernel.CreateMutexW.restype = [C.c_void_p, W.BOOL, W.LPCWSTR], W.HANDLE
    kernel.WaitForSingleObject.argtypes, kernel.WaitForSingleObject.restype = [W.HANDLE, W.DWORD], W.DWORD
    kernel.ReleaseMutex.argtypes, kernel.ReleaseMutex.restype = [W.HANDLE], W.BOOL
    kernel.CloseHandle.argtypes, kernel.CloseHandle.restype = [W.HANDLE], W.BOOL
    handle = kernel.CreateMutexW(None, False, "Local\\XQXSCommunityCompile")
    if not handle:
        raise ValueError("Cannot create the desktop compiler mutex.")
    acquired = kernel.WaitForSingleObject(handle, 0) in (0, 128)
    try:
        yield acquired
    finally:
        if acquired:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


class POINT(C.Structure):
    _fields_ = [("x", W.LONG), ("y", W.LONG)]


class RECT(C.Structure):
    _fields_ = [("left", W.LONG), ("top", W.LONG), ("right", W.LONG), ("bottom", W.LONG)]


class GUIINFO(C.Structure):
    _fields_ = [("size", W.DWORD), ("flags", W.DWORD), ("active", W.HWND),
                ("focus", W.HWND), ("capture", W.HWND), ("menu", W.HWND),
                ("move", W.HWND), ("caret", W.HWND), ("rect", RECT)]


class LASTINPUT(C.Structure):
    _fields_ = [("size", W.UINT), ("tick", W.DWORD)]


class XqDesktop:
    TYPE_LABELS = {"indicator": "指標", "filter": "選股", "sensor": "警示", "autotrade": "交易"}

    def __init__(self, executable: str | None = None):
        self.u = C.WinDLL("user32", use_last_error=True)
        self.k = C.WinDLL("kernel32", use_last_error=True)
        self.callback = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
        self._bind(self.u, "EnumWindows", [self.callback, W.LPARAM], W.BOOL)
        self._bind(self.u, "EnumChildWindows", [W.HWND, self.callback, W.LPARAM], W.BOOL)
        self._bind(self.u, "GetWindowTextW", [W.HWND, W.LPWSTR, C.c_int], C.c_int)
        self._bind(self.u, "GetClassNameW", [W.HWND, W.LPWSTR, C.c_int], C.c_int)
        self._bind(self.u, "GetWindowThreadProcessId", [W.HWND, C.POINTER(W.DWORD)], W.DWORD)
        self._bind(self.u, "GetParent", [W.HWND], W.HWND)
        self._bind(self.u, "GetForegroundWindow", [], W.HWND)
        self._bind(self.u, "SetForegroundWindow", [W.HWND], W.BOOL)
        self._bind(self.u, "GetDlgCtrlID", [W.HWND], C.c_int)
        self._bind(self.u, "IsWindowVisible", [W.HWND], W.BOOL)
        self._bind(self.u, "GetGUIThreadInfo", [W.DWORD, C.POINTER(GUIINFO)], W.BOOL)
        self._bind(self.u, "GetLastInputInfo", [C.POINTER(LASTINPUT)], W.BOOL)
        self._bind(self.u, "GetAsyncKeyState", [C.c_int], C.c_short)
        self._bind(self.u, "SetCursorPos", [C.c_int, C.c_int], W.BOOL)
        self._bind(self.u, "GetWindowRect", [W.HWND, C.POINTER(RECT)], W.BOOL)
        self._bind(self.u, "mouse_event", [W.DWORD, W.DWORD, W.DWORD, W.DWORD, C.c_size_t], None)
        self._bind(self.u, "keybd_event", [W.BYTE, W.BYTE, W.DWORD, C.c_size_t], None)
        self._bind(self.u, "PostMessageW", [W.HWND, W.UINT, W.WPARAM, W.LPARAM], W.BOOL)
        self._bind(self.u, "SendMessageTimeoutW", [W.HWND, W.UINT, W.WPARAM, W.LPARAM,
                                                   W.UINT, W.UINT, C.POINTER(C.c_size_t)], W.LPARAM)
        self._bind(self.k, "OpenProcess", [W.DWORD, W.BOOL, W.DWORD], W.HANDLE)
        self._bind(self.k, "QueryFullProcessImageNameW", [W.HANDLE, W.DWORD, W.LPWSTR,
                                                         C.POINTER(W.DWORD)], W.BOOL)
        self._bind(self.k, "CloseHandle", [W.HANDLE], W.BOOL)
        self._bind(self.k, "VirtualAllocEx", [W.HANDLE, C.c_void_p, C.c_size_t, W.DWORD, W.DWORD], C.c_void_p)
        self._bind(self.k, "VirtualFreeEx", [W.HANDLE, C.c_void_p, C.c_size_t, W.DWORD], W.BOOL)
        self._bind(self.k, "ReadProcessMemory", [W.HANDLE, C.c_void_p, C.c_void_p,
                                                 C.c_size_t, C.POINTER(C.c_size_t)], W.BOOL)
        self._bind(self.k, "GetTickCount", [], W.DWORD)
        self.executable_filter = Path(executable).resolve() if executable else None
        self.pid = 0
        self.root = 0
        self.executable = None
        self.deadline = time.monotonic() + 20
        self.stage = "preflight"
        self.trigger_attempted = False

    @staticmethod
    def _bind(lib, name, args, result):
        fn = getattr(lib, name)
        fn.argtypes, fn.restype = args, result

    def windows(self, parent: int = 0) -> list[int]:
        result = []
        callback = self.callback(lambda hwnd, _: result.append(int(hwnd)) is None or True)
        if parent:
            self.u.EnumChildWindows(parent, callback, 0)
        else:
            self.u.EnumWindows(callback, 0)
        return result

    def caption(self, hwnd: int) -> str:
        buffer = C.create_unicode_buffer(4096)
        self.u.GetWindowTextW(hwnd, buffer, len(buffer))
        return buffer.value

    def class_name(self, hwnd: int) -> str:
        buffer = C.create_unicode_buffer(256)
        self.u.GetClassNameW(hwnd, buffer, len(buffer))
        return buffer.value

    def owner(self, hwnd: int) -> int:
        pid = W.DWORD()
        self.u.GetWindowThreadProcessId(hwnd, C.byref(pid))
        return pid.value

    def process_path(self, pid: int) -> Path | None:
        handle = self.k.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        try:
            buffer, length = C.create_unicode_buffer(32768), W.DWORD(32768)
            return Path(buffer.value) if self.k.QueryFullProcessImageNameW(handle, 0, buffer, C.byref(length)) else None
        finally:
            self.k.CloseHandle(handle)

    def doctor(self) -> dict:
        candidates = {}
        cache = {}
        for hwnd in self.windows():
            title = self.caption(hwnd)
            if not title.startswith("XQ全球贏家"):
                continue
            pid = self.owner(hwnd)
            if pid not in cache:
                cache[pid] = self.process_path(pid)
            path = cache[pid]
            if path and path.name.lower() == "daqxqlite.exe" and (not self.executable_filter or path.resolve() == self.executable_filter):
                candidates[pid] = (hwnd, path, title)
        if len(candidates) != 1:
            return {"status": "environment_error", "reason": "Open exactly one accessible XQ personal-edition instance first.", "requires_xq": True}
        self.pid, (self.root, self.executable, title) = next(iter(candidates.items()))
        if "已登入" not in title or "未登入" in title:
            return {"status": "environment_error", "reason": "Log in to XQ first; this tool does not manage credentials."}
        version = re.search(r"版本\s+([^\]]+)", title)
        return {"status": "ready", "executable": str(self.executable), "install_dir": str(self.executable.parent),
                "version": version[1] if version else None, "requires_xq": True,
                "requires_interactive_desktop": True, "pid": self.pid}

    def message(self, hwnd: int, msg: int, wparam=0, lparam=0) -> int:
        if self.owner(hwnd) != self.pid:
            raise ValueError("The target control no longer belongs to this XQ instance.")
        result = C.c_size_t()
        if not self.u.SendMessageTimeoutW(hwnd, msg, wparam, lparam, 2, 2000, C.byref(result)):
            raise ValueError("XQ did not answer a control request within two seconds.")
        return result.value

    def control_text(self, hwnd: int) -> str:
        buffer = C.create_unicode_buffer(32768)
        self.message(hwnd, 13, len(buffer), C.addressof(buffer))
        return buffer.value

    def set_edit_text(self, hwnd: int, text: str):
        if self.class_name(hwnd) != "Edit":
            raise ValueError("Refusing to write to an unexpected control.")
        buffer = C.create_unicode_buffer(text)
        self.message(hwnd, 12, 0, C.addressof(buffer))
        if self.control_text(hwnd) != text:
            raise ValueError("The file dialog did not accept the requested filename.")

    def assert_foreground(self):
        if self.owner(self.u.GetForegroundWindow()) != self.pid:
            raise ValueError("XQ lost foreground focus; no further input was sent.")

    def focus(self, hwnd: int):
        if self.owner(hwnd) != self.pid:
            raise ValueError("Unexpected foreground target.")
        self.u.SetForegroundWindow(hwnd)
        time.sleep(0.15)
        self.assert_foreground()

    def tap(self, key: int, modifier: int | None = None):
        self.assert_foreground()
        try:
            if modifier:
                self.u.keybd_event(modifier, 0, 0, 0)
            self.u.keybd_event(key, 0, 0, 0)
            self.u.keybd_event(key, 0, 2, 0)
        finally:
            if modifier:
                self.u.keybd_event(modifier, 0, 2, 0)
        time.sleep(0.12)

    def click(self, hwnd: int):
        self.assert_foreground()
        if self.owner(hwnd) != self.pid or not self.u.IsWindowVisible(hwnd):
            raise ValueError("The target control is not visible in XQ.")
        rect = RECT()
        self.u.GetWindowRect(hwnd, C.byref(rect))
        self.u.SetCursorPos((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
        self.u.mouse_event(2, 0, 0, 0, 0)
        self.u.mouse_event(4, 0, 0, 0, 0)
        time.sleep(0.15)

    def wait(self, predicate, label: str, limit: float = 20):
        stop = min(self.deadline, time.monotonic() + limit)
        while time.monotonic() < stop:
            result = predicate()
            if result:
                return result
            time.sleep(0.2)
        raise TimeoutError("Timed out waiting for " + label + "; inspect XQ before retrying.")

    def named_window(self, prefix: str, exact=False):
        matches = [h for h in self.windows() if self.owner(h) == self.pid and self.u.IsWindowVisible(h)
                   and (self.caption(h) == prefix if exact else self.caption(h).startswith(prefix))]
        if len(matches) > 1:
            raise ValueError("Ambiguous XQ window: " + prefix)
        return matches[0] if matches else None

    def read_scintilla(self, hwnd: int) -> str:
        if self.class_name(hwnd) != "Scintilla":
            raise ValueError("Unexpected source editor control.")
        length, codepage = self.message(hwnd, 2183), self.message(hwnd, 2137)
        if length > 1_048_576:
            raise ValueError("The source control exceeds the bounded read size.")
        process = self.k.OpenProcess(0x1000 | 0x0008 | 0x0010, False, self.pid)
        if not process:
            raise ValueError("Cannot read the XQ source control; use matching desktop privileges.")
        remote = None
        completed_read_request = False
        try:
            remote = self.k.VirtualAllocEx(process, None, length + 1, 0x3000, 0x04)
            if not remote:
                raise ValueError("Cannot allocate a temporary non-executable text buffer.")
            self.message(hwnd, 2182, length + 1, remote)
            completed_read_request = True
            buffer, read = C.create_string_buffer(length + 1), C.c_size_t()
            if not self.k.ReadProcessMemory(process, remote, buffer, length + 1, C.byref(read)) or read.value != length + 1:
                raise ValueError("Cannot read the Scintilla text response.")
            encoding = "utf-8" if codepage == 65001 else (f"cp{codepage}" if codepage else "mbcs")
            return buffer.raw[:length].decode(encoding, errors="strict")
        finally:
            # A timed-out cross-process message may still be using its output
            # pointer. Leave that bounded data buffer to XQ's process lifetime.
            if remote and completed_read_request:
                self.k.VirtualFreeEx(process, remote, 0, 0x8000)
            self.k.CloseHandle(process)

    def compilation_output(self, editor: int, name: str) -> str | None:
        controls = [h for h in self.windows(editor) if self.class_name(h) == "Scintilla"
                    and self.u.GetDlgCtrlID(h) == 59751]
        if len(controls) != 1:
            raise ValueError("Cannot identify the XQ compiler output control.")
        text = self.read_scintilla(controls[0])
        if name + " 編譯成功，" in text or name + " 編譯發生錯誤，" in text:
            return "\n".join(line for line in text.splitlines()
                             if re.match(r"^\[\d{2}:\d{2}:\d{2}\] " + re.escape(name) + r" ", line))
        return None

    def capture_error_grid(self, editor: int, name: str, destination: Path) -> str:
        """Capture only XQ's visible diagnostic table; no OCR or clipboard access."""
        self.assert_foreground()
        if name not in self.caption(editor):
            raise ValueError("The active editor no longer identifies the submitted script.")
        grids = [h for h in self.windows(editor) if self.class_name(h) == "XTPReport"
                 and self.u.GetDlgCtrlID(h) == 59752 and self.u.IsWindowVisible(h)]
        if len(grids) != 1:
            raise ValueError("The compiler diagnostic grid is not visible; open its result tab to inspect details.")
        gdi = C.WinDLL("gdi32", use_last_error=True)
        self._bind(self.u, "SetThreadDpiAwarenessContext", [C.c_void_p], C.c_void_p)
        self._bind(self.u, "GetDC", [W.HWND], W.HDC)
        self._bind(self.u, "ReleaseDC", [W.HWND, W.HDC], C.c_int)
        self._bind(gdi, "CreateCompatibleDC", [W.HDC], W.HDC)
        self._bind(gdi, "CreateCompatibleBitmap", [W.HDC, C.c_int, C.c_int], W.HBITMAP)
        self._bind(gdi, "SelectObject", [W.HDC, W.HANDLE], W.HANDLE)
        self._bind(gdi, "BitBlt", [W.HDC, C.c_int, C.c_int, C.c_int, C.c_int,
                                   W.HDC, C.c_int, C.c_int, W.DWORD], W.BOOL)
        self._bind(gdi, "GetDIBits", [W.HDC, W.HBITMAP, W.UINT, W.UINT, C.c_void_p,
                                     C.c_void_p, W.UINT], C.c_int)
        self._bind(gdi, "DeleteObject", [W.HANDLE], W.BOOL)
        self._bind(gdi, "DeleteDC", [W.HDC], W.BOOL)
        previous_dpi = self.u.SetThreadDpiAwarenessContext(C.c_void_p(-4))
        screen = memory = bitmap = previous_object = None
        try:
            if not previous_dpi:
                raise ValueError("Cannot establish physical pixel coordinates for diagnostic capture.")
            rect = RECT()
            self.u.GetWindowRect(grids[0], C.byref(rect))
            width, height = rect.right - rect.left, rect.bottom - rect.top
            if width < 30 or height < 30 or width * height > 6_000_000:
                raise ValueError("The diagnostic table has an unsupported capture size.")
            screen = self.u.GetDC(0)
            memory = gdi.CreateCompatibleDC(screen)
            bitmap = gdi.CreateCompatibleBitmap(screen, width, height)
            if not screen or not memory or not bitmap:
                raise ValueError("Cannot allocate the diagnostic image.")
            previous_object = gdi.SelectObject(memory, bitmap)
            self.assert_foreground()
            if not gdi.BitBlt(memory, 0, 0, width, height, screen, rect.left, rect.top, 0x00CC0020):
                raise ValueError("Cannot capture the visible diagnostic table.")
            gdi.SelectObject(memory, previous_object)
            previous_object = None
            pixels = C.create_string_buffer(width * height * 4)
            header = struct.pack("<IiiHHIIiiII", 40, width, -height, 1, 32, 0, len(pixels), 0, 0, 0, 0)
            info = C.create_string_buffer(header)
            if gdi.GetDIBits(screen, bitmap, 0, height, pixels, info, 0) != height:
                raise ValueError("Cannot read the diagnostic image pixels.")
            destination.write_bytes(struct.pack("<2sIHHI", b"BM", 54 + len(pixels), 0, 0, 54) + header + pixels.raw)
            return str(destination.resolve())
        finally:
            if previous_object and memory:
                gdi.SelectObject(memory, previous_object)
            if bitmap:
                gdi.DeleteObject(bitmap)
            if memory:
                gdi.DeleteDC(memory)
            if screen:
                self.u.ReleaseDC(0, screen)
            if previous_dpi:
                self.u.SetThreadDpiAwarenessContext(previous_dpi)

    def compile(self, request: dict) -> dict:
        ready = self.doctor()
        if ready["status"] != "ready":
            return ready
        self.deadline = time.monotonic() + request["timeout"]
        blocking = [h for h in self.windows() if self.owner(h) == self.pid
                    and self.u.IsWindowVisible(h) and self.class_name(h) == "#32770"]
        if blocking:
            return {"status": "desktop_busy", "reason": "Close the existing XQ dialog before starting a compilation."}
        info = LASTINPUT(C.sizeof(LASTINPUT), 0)
        if not self.u.GetLastInputInfo(C.byref(info)):
            raise ValueError("Cannot verify desktop input state.")
        idle = ((self.k.GetTickCount() - info.tick) & 0xffffffff) / 1000
        if idle < request["idle_seconds"] or any(self.u.GetAsyncKeyState(k) & 0x8000 for k in (0x10, 0x11, 0x12, 0x5B)):
            return {"status": "desktop_busy", "reason": "Pause keyboard/mouse input before running the desktop compiler.", "idle_seconds": idle}
        editor = self.named_window("XScript")
        self.stage = "open_editor"
        if not editor:
            self.focus(self.root)
            self.tap(ord("D"), 0x12)
            self.tap(ord("E"))
            editor = self.wait(lambda: self.named_window("XScript"), "the XScript editor")
        self.focus(editor)
        self.stage = "open_source_file"
        self.tap(ord("F"), 0x12)
        self.tap(0x24)  # Home selects New; Open XS is the third File menu item.
        self.tap(0x28)
        self.tap(0x28)
        self.tap(0x0D)
        dialog = self.wait(lambda: self.named_window("開啟", exact=True), "the XS file dialog")
        if self.class_name(dialog) != "#32770":
            raise ValueError("The XS file picker is not the expected native dialog.")
        self.tap(ord("N"), 0x12)
        thread = self.u.GetWindowThreadProcessId(self.u.GetForegroundWindow(), None)
        gui = GUIINFO()
        gui.size = C.sizeof(gui)
        if not self.u.GetGUIThreadInfo(thread, C.byref(gui)) or not gui.focus:
            raise ValueError("Cannot locate the filename field.")
        field = int(gui.focus)
        ancestor = field
        while ancestor and ancestor != dialog:
            ancestor = self.u.GetParent(ancestor)
        if ancestor != dialog:
            raise ValueError("The filename control is outside the expected file dialog.")
        self.set_edit_text(field, request["source"])
        self.tap(0x0D)
        creation = self.wait(lambda: self.named_window("新增腳本", exact=True), "the script-type dialog")
        self.stage = "select_script_type"
        controls = self.windows(creation)
        label = self.TYPE_LABELS[request["script_type"]]
        radio = [h for h in controls if self.class_name(h) == "Button" and self.control_text(h).replace("&", "") == label]
        confirm = [h for h in controls if self.class_name(h) == "Button" and self.control_text(h).replace("&", "") == "確認"]
        if len(radio) != 1 or len(confirm) != 1:
            raise ValueError("The script creation controls differ from the tested XQ interface.")
        self.click(radio[0])
        if self.message(radio[0], 240) != 1:
            raise ValueError("XQ did not select the requested script category.")
        self.click(confirm[0])
        name = request["script_name"]
        def find_view():
            matches = [h for h in self.windows(editor) if self.class_name(h).startswith("AfxFrameOrView")
                       and self.caption(h).startswith(name + "(")]
            return matches[0] if len(matches) == 1 else None
        view = self.wait(find_view, "the newly imported script")
        self.stage = "verify_source_and_type"
        if f"({label})" not in self.caption(view):
            raise ValueError("The imported script has the wrong XQ category.")
        source_controls = [h for h in self.windows(view) if self.class_name(h) == "Scintilla" and self.u.GetDlgCtrlID(h) == 9999]
        if len(source_controls) != 1:
            raise ValueError("The newly created script has no unambiguous source control.")
        actual = self.read_scintilla(source_controls[0]).replace("\r\n", "\n").rstrip("\n")
        expected = request["source_text"].replace("\r\n", "\n").rstrip("\n")
        if actual != expected:
            raise ValueError("The editor source differs from the submitted file; compilation was not triggered.")
        self.click(source_controls[0])
        requested_at = datetime.now(timezone.utc).isoformat()
        self.stage = "trigger_compile"
        self.trigger_attempted = True
        self.tap(0x75)  # F6 only. No run/backtest/trade command exists in this adapter.
        self.stage = "read_compiler_output"
        output = self.wait(lambda: self.compilation_output(editor, name), "the matching compiler output",
                           limit=request["timeout"])
        capture = {}
        if name + " 編譯發生錯誤，" in output:
            try:
                capture["diagnostic_image"] = self.capture_error_grid(
                    editor, name, Path(request["evidence_dir"]) / "diagnostics.bmp")
            except (OSError, ValueError) as exc:
                capture["diagnostic_capture_error"] = str(exc)
        return {"status": "triggered", "source_matches": True, "type_matches": True,
                "script_name": name, "compile_requested_at": requested_at,
                "compilation_output": output, **capture}
