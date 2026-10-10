"""Check that your machine has everything Member A needs. Run: python src/dataset/check_env.py"""
import importlib
import shutil
import sys

ok = True
v = sys.version_info
print(f"Python {v.major}.{v.minor}.{v.micro}", "OK" if (3, 10) <= (v.major, v.minor) < (3, 14) else "-> use 3.10-3.12")
for mod, pip in [("numpy", "numpy"), ("scipy", "scipy"), ("yaml", "pyyaml"),
                 ("matplotlib", "matplotlib"), ("parselmouth", "praat-parselmouth"), ("pytest", "pytest")]:
    try:
        m = importlib.import_module(mod)
        print(f"  {mod:12s} OK  {getattr(m, '__version__', '')}")
    except ImportError:
        ok = False
        print(f"  {mod:12s} MISSING -> pip install {pip}")
for tool in ["git", "ffmpeg"]:
    p = shutil.which(tool)
    print(f"  {tool:12s} {'OK  ' + p if p else 'MISSING (see the install step in the guide)'}")
    ok = ok and bool(p)
print("\nALL GOOD" if ok else "\nFix the MISSING items above, then run this again.")
