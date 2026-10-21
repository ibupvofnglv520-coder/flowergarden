[app]
# (str) Title of your application
title = FlowerGarden

# (str) Package name
package.name = flowergarden

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3==3.10.12,hostpython3==3.10.12,pygame,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# =============================================================================
# 🎨 ここにColabのコードで指定されていたアイコン設定をすべて反映しました
# =============================================================================
icon.filename = %(source.dir)s/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/icon.png
icon.adaptive_background.color = #FFFFFF

# =============================================================================
# Android specific (最新スマホ向けの時短・安定設定)
# =============================================================================
# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) The Android architectures to build for (時短のためにarm64のみに指定)
android.archs = arm64-v8a

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

android.ndk = 25c
p4a.bootstrap = sdl2

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
