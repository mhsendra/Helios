[app]
title = Helios
package.name = Helios
package.domain = org.Helios
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,qml,js,ttf,json,toml
source.include_patterns = helios/resources/**,assets/android/**
version = 1.0.0
requirements = python3,shiboken6,PySide6,contourpy,numpy,pandas,matplotlib,requests,charset-normalizer,idna,urllib3,certifi,openpyxl,et-xmlfile,reportlab,harfbuzz,tzdata,setuptools
orientation = landscape
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.api = 35
android.minapi = 28
android.ndk_api = 28
android.no-byte-compile-python = True
p4a.bootstrap = qt
android.add_resources = deployment/android-res/drawable/helios_launch_logo.jpg:drawable/helios_launch_logo.jpg,deployment/android-res/drawable/helios_launch_background.xml:drawable/helios_launch_background.xml
p4a.local_recipes = deployment/recipes
p4a.branch = master
p4a.commit = 58d21141f17c889bf8585f5665921d72028f8831
p4a.source_dir = /home/mhsen/Helios-android-git/deployment/python-for-android-local
android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE
android.add_jars = deployment/jar/PySide6/jar/Qt6AndroidBindings.jar,deployment/jar/PySide6/jar/Qt6Android.jar
p4a.extra_args = --qt-libs=Widgets,Core,Gui --load-local-libs=plugins_platforms_qtforandroid --init-classes= --force-build
icon.filename = assets/android/helios-icon.png
icon.adaptive_foreground.filename = assets/android/helios-adaptive-foreground.png
icon.adaptive_background.filename = assets/android/helios-adaptive-background.png
p4a.setup_py = True

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = bin
