[app]
android.add_resources = /home/mhsen/Helios-android-git/deployment/android-res/drawable/helios_launch_logo.jpg:drawable/helios_launch_logo.jpg,/home/mhsen/Helios-android-git/deployment/android-res/drawable/helios_launch_background.xml:drawable/helios_launch_background.xml
android.add_jars = /home/mhsen/Helios-android-git/deployment/jar/PySide6/jar/Qt6AndroidBindings.jar,/home/mhsen/Helios-android-git/deployment/jar/PySide6/jar/Qt6Android.jar
android.no-byte-compile-python = True
android.ndk_api = 28
p4a.setup_py = True
p4a.local_recipes = /home/mhsen/Helios-android-git/deployment/recipes

title = Helios UI Test
package.name = heliosuitest
package.domain = org.helios

source.dir = app
source.include_exts = py,png,jpg,ttf,json

version = 0.1.0

requirements = python3,shiboken6,PySide6

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 28
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = qt
p4a.extra_args = --qt-libs=Widgets,Core,Gui --load-local-libs=plugins_platforms_qtforandroid --init-classes=

[buildozer]

log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = bin
