"""Generic owner-only directory bootstrap; call before provisioning identities.

Does not generate, read, decrypt or distribute keys. Existing directories are
never silently re-permissioned. Administrators remain outside this access model.
"""
import csv
import ctypes
import io
import os
import re
from pathlib import Path

from .errors import require
from .process import checked, pinned_executable
from .storage import atomic_json, no_links


def create_private_directory(spec):
    path = Path(spec["destination"]).absolute()
    no_links(path.parent)
    require(path.parent.is_dir() and not path.exists(), "EXISTS", "Private directory requires an existing trusted parent and new destination")
    if os.name == "nt":
        observation = checked([pinned_executable(spec["whoami"]), "/user", "/fo", "csv", "/nh"],
                              timeout=30, max_output=65536)["stdout"].decode(spec.get("console_encoding", "utf-8"))
        rows = list(csv.reader(io.StringIO(observation)))
        require(len(rows) == 1 and len(rows[0]) == 2, "ACL", "Unexpected OS identity observation")
        sid = rows[0][1].strip()
        require(re.fullmatch(r"S-1-[0-9]+(?:-[0-9]+)+", sid) and sid == spec["owner_sid"],
                "ACL", "Private directory owner is not the observed current user")
        advapi = ctypes.WinDLL("advapi32", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        volume = ctypes.create_unicode_buffer(len(str(path.parent)) + 2)
        kernel.GetVolumePathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumePathNameW.restype = ctypes.c_int
        require(kernel.GetVolumePathNameW(str(path.parent), volume, len(volume)), "ACL", "Could not query storage volume")
        flags = ctypes.c_uint32()
        kernel.GetVolumeInformationW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32,
                                                ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32),
                                                ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumeInformationW.restype = ctypes.c_int
        require(kernel.GetVolumeInformationW(volume.value, None, 0, None, None, ctypes.byref(flags), None, 0) and flags.value & 8,
                "ACL", "Private storage requires persistent filesystem ACL support")
        descriptor = ctypes.c_void_p()
        advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32,
                                                                              ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = ctypes.c_int
        require(advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            "D:P(A;OICI;FA;;;" + sid + ")(A;OICI;FA;;;SY)", 1, ctypes.byref(descriptor), None),
            "ACL", "OS security descriptor conversion failed", windows_error=ctypes.get_last_error())
        class Attributes(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint32), ("descriptor", ctypes.c_void_p), ("inherit", ctypes.c_int)]
        attributes = Attributes(ctypes.sizeof(Attributes), descriptor, False)
        kernel.CreateDirectoryW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(Attributes)]
        kernel.CreateDirectoryW.restype = ctypes.c_int
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree.restype = ctypes.c_void_p
        try:
            require(kernel.CreateDirectoryW(str(path), ctypes.byref(attributes)), "ACL",
                    "Could not create protected directory", windows_error=ctypes.get_last_error())
        finally:
            kernel.LocalFree(descriptor)
        access = {"owner_sid": sid, "additional_identity": "LocalSystem", "inheritance": "protected DACL, inheritable owner/System full access"}
    else:
        path.mkdir(mode=0o700)
        os.chmod(path, 0o700)
        require(path.stat().st_uid == os.getuid() and path.stat().st_mode & 0o077 == 0, "ACL", "Owner-only directory was not established")
        access = {"owner_uid": os.getuid(), "mode": "0700"}
    record = {"format": "OWNER-ONLY-STORAGE-CREATION", "path": str(path), "access": access,
              "scope": "new directory only; trusted parent required; no administrator resistance claim"}
    atomic_json(path / "storage-creation.json", record)
    return record
