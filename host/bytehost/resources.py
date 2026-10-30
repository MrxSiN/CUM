"""Generic Windows per-process counters; no estimates when counters unavailable."""
import ctypes
import os


class ResourceSample:
    def __init__(self, pid):
        self.handle = None
        self.error = None
        if os.name != "nt":
            self.error = "Per-process native counters require Windows; import container/cgroup counters separately"
            return
        try:
            self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            self.psapi = ctypes.WinDLL("psapi", use_last_error=True)
            self.kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
            self.kernel.OpenProcess.restype = ctypes.c_void_p
            self.handle = self.kernel.OpenProcess(0x0410, False, pid)
            if not self.handle:
                self.error = "OpenProcess failed: " + str(ctypes.get_last_error())
        except OSError as exc:
            self.error = str(exc)

    def finish(self):
        if not self.handle:
            return {"status": "BLOCKED", "reason": self.error, "scope": "selected process only"}
        class Memory(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_uint32), ("PageFaultCount", ctypes.c_uint32)] + [
                (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize",
                "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        class FileTime(ctypes.Structure):
            _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]
        memory = Memory()
        memory.cb = ctypes.sizeof(memory)
        times = [FileTime() for _ in range(4)]
        self.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Memory), ctypes.c_uint32]
        self.psapi.GetProcessMemoryInfo.restype = ctypes.c_int
        self.kernel.GetProcessTimes.argtypes = [ctypes.c_void_p, *([ctypes.POINTER(FileTime)] * 4)]
        self.kernel.GetProcessTimes.restype = ctypes.c_int
        self.kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        try:
            memory_ok = self.psapi.GetProcessMemoryInfo(self.handle, ctypes.byref(memory), ctypes.sizeof(memory))
            cpu_ok = self.kernel.GetProcessTimes(self.handle, *(ctypes.byref(value) for value in times))
            if not memory_ok or not cpu_ok:
                return {"status": "BLOCKED", "reason": "Native counter query failed", "scope": "selected process only"}
            seconds = lambda value: ((value.high << 32) | value.low) / 10000000
            return {"status": "PASS", "scope": "selected process only; excludes descendants",
                    "peak_working_set_bytes": int(memory.PeakWorkingSetSize),
                    "peak_pagefile_bytes": int(memory.PeakPagefileUsage),
                    "kernel_cpu_seconds": seconds(times[2]), "user_cpu_seconds": seconds(times[3]),
                    "page_faults": int(memory.PageFaultCount)}
        finally:
            self.kernel.CloseHandle(self.handle)
            self.handle = None
