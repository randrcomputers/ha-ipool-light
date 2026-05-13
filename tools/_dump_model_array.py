"""Dump R.array used by RgbFragment.buildModel (iPool Light APK)."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)
try:
    from loguru import logger as L

    L.remove()
    L.add(open("nul", "w"), level="ERROR")
except ImportError:
    pass

from androguard.core.apk import APK  # noqa: E402

R_ARRAY_MODEL = 0x7F020004  # const from RgbFragment.buildModel (2130837508)

apk = Path(r"c:\Users\Admin\Downloads\Ipoolight_1.0.3_APKPure.apk")
if not apk.is_file():
    apk = Path(__file__).resolve().parents[2] / "_apk_ipoollight_extract" / "ipool.zip"

a = APK(str(apk))
res = a.get_android_resources()
if res is None:
    print("no resources", file=sys.stderr)
    sys.exit(1)

try:
    name = res.get_resource_xml_name(R_ARRAY_MODEL)
    print("resource:", hex(R_ARRAY_MODEL), name)
except Exception as e:
    print("name err", e)

# get string array content
try:
    arr = res.get_string_array(R_ARRAY_MODEL)
    for i, s in enumerate(arr):
        print(i, repr(s))
except Exception as e:
    print("get_string_array failed", e)
    # fallback: try packages iteration
    for pkg in res.get_packages_names():
        try:
            arr = res.get_string_array(R_ARRAY_MODEL)
        except Exception:
            continue
        print("pkg", pkg, "len", len(arr) if arr else 0)
