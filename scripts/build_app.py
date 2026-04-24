"""py2app build script for Octavius.app.

Run:
    .venv/bin/pip install py2app
    .venv/bin/python scripts/build_app.py py2app

Produces dist/Octavius.app — drag to /Applications.

Note on signing:
  - Without a paid Apple Developer cert, the app is unsigned. Users will
    see "Octavius can't be opened because Apple cannot check it for
    malicious software." They can right-click → Open the first time, then
    macOS allows it.
  - With a Developer cert, run:
      codesign --deep --force --sign "Developer ID Application: NAME (TEAMID)" dist/Octavius.app
      xcrun notarytool submit dist/Octavius.zip --keychain-profile "AC_PASSWORD" --wait
      xcrun stapler staple dist/Octavius.app
"""
from setuptools import setup

APP = ["../octavius/menubar.py"]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,  # add an .icns when we have one
    "plist": {
        "CFBundleName": "Octavius",
        "CFBundleDisplayName": "Octavius",
        "CFBundleIdentifier": "com.octavius.menubar",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "LSUIElement": True,  # menubar app — no Dock icon
        "NSHighResolutionCapable": True,
    },
    "packages": ["rumps", "Quartz", "AppKit", "PIL", "psutil", "octavius"],
    "includes": ["octavius.bus", "octavius.web", "octavius.daemon", "octavius.jobs"],
    "site_packages": True,
}

setup(
    app=APP,
    name="Octavius",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
