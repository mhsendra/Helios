# Helios Android — Compilación y recuperación

## 1. Estado de referencia

Entorno validado el 22 de noviembre de 2026.

La APK se compiló correctamente y se instaló en un
Samsung Galaxy S10e (SM-G970F) con Android 12.

Pruebas funcionales superadas:

- Inicio de la aplicación.
- Navegación entre pantallas.
- Desplazamiento y visualización de gráficos.
- Funcionamiento del botón Atrás de Android.
- Selección de archivos Excel.
- Ejecución del flujo completo de análisis.
- Generación del informe final.
- Estabilidad durante las pruebas.

La validación funcional corresponde al dispositivo
indicado. No constituye una certificación de
compatibilidad con todos los dispositivos Android.

## 2. Repositorio Helios

Repositorio de trabajo:

    ~/Helios-android-git

Rama validada:

    development/android

Commit de referencia previo a esta documentación:

    d9db1e6

El código de Helios debe mantenerse versionado
independientemente de los archivos generados durante
la compilación.

## 3. Herramientas y versiones

Sistema de compilación:

- WSL2 con Ubuntu 24.04.
- Python del sistema: 3.12.3.
- Python del entorno virtual: 3.11.18.
- Buildozer: 1.5.0.
- PySide6 Android: 6.12.0.
- Arquitectura: arm64-v8a.
- Android API: 35.
- Android mínimo: API 28.
- Android NDK API: 28.
- Bootstrap: Qt.

Entorno virtual:

    ~/venvs/helios-deploy

SDK:

    ~/.buildozer/android/platform/android-sdk

NDK:

    ~/.buildozer/android/platform/android-ndk-r28c

Wheels de PySide6 y Shiboken6:

    ~/.pyside6_android_deploy/wheels

Estas rutas corresponden al entorno validado.
El script de compilación permite configurar rutas
alternativas mediante variables de entorno.

## 4. Python-for-Android

Repositorio original:

    https://github.com/kivy/python-for-android.git

Commit fijado:

    58d21141f17c889bf8585f5665921d72028f8831

Checkout local:

    deployment/python-for-android-local

Los siete parches propios están en:

    deployment/patches/

Orden obligatorio:

1. 0001-recreate-host-venv.patch
2. 0002-create-adaptive-icon-directory.patch
3. 0003-remove-generic-back-handler.patch
4. 0004-refresh-helios-package.patch
5. 0005-helios-launch-background.patch
6. 0006-android-excel-picker.patch
7. 0007-android-pdf-export.patch

Los siete parches se aplicaron correctamente sobre
el commit original utilizando un índice temporal.

Se verificó que reconstruyen exactamente los cuatro
archivos modificados del checkout validado.

Resultado de la comprobación:

    Archivos comprobados: 4
    Diferencias detectadas: 0

## 5. Aplicador de parches

Script:

    deployment/apply_p4a_patches.sh

IMPORTANTE:

La versión validada de este script reconstruye
los cambios en un directorio temporal y comprueba
que el checkout local ya contiene esos cambios.

No instala automáticamente los parches sobre
un checkout limpio.

En consecuencia, la recuperación desde cero
requiere aplicar primero los siete parches.

Esta operación todavía debe integrarse y validarse
en un procedimiento automatizado de recuperación.

No utilizar git reset --hard, git clean -fdx
ni eliminar el checkout existente para probar
la recuperación.

## 6. Configuración Android

Archivo:

    buildozer.spec

Configuración principal:

    android.archs = arm64-v8a
    android.api = 35
    android.minapi = 28
    android.ndk_api = 28
    p4a.bootstrap = qt
    p4a.setup_py = True

Recetas locales:

    deployment/recipes

El proyecto utiliza, entre otras dependencias:

- PySide6 y Shiboken6.
- NumPy.
- pandas.
- Matplotlib.
- openpyxl.
- ReportLab.
- requests.

El archivo buildozer.spec contiene la lista
completa de requisitos y los recursos Android.

## 7. Script de compilación

Script principal:

    deployment/build_android.sh

Comandos admitidos:

    prepare
    debug
    release
    deploy
    run

Preparación:

    bash deployment/build_android.sh prepare

Compilación de depuración:

    bash deployment/build_android.sh debug

El comando prepare verifica las herramientas,
el checkout y los parches existentes.

El comando debug inicia la compilación.

El script utiliza un archivo temporal de
configuración para seleccionar el checkout
correcto de python-for-android.

No modifica permanentemente buildozer.spec
durante esta operación.

Los comandos release, deploy y run están
admitidos por el script, pero no se consideran
validados por las pruebas aquí documentadas.

## 8. APK validada

Archivo generado:

    bin/Helios-1.0.0-arm64-v8a-debug.apk

Paquete Android:

    org.helios.helios

Versión:

    1.0.0

Copia de seguridad validada:

    backups/apk/Helios-validada-paso838.apk

SHA-256:

    7f51d0b6e82624ec3f72d78c46a28631b7d059faa3a9c99c8003fc46429d28d7

Respaldo anterior:

    backups/apk/Helios-validada-768d494.apk

SHA-256 anterior:

    26dc098cc3e771bfd5fcc2e6db3aa71357dcf44f09e6a6ad2002b3929112b8ae

No sobrescribir ni eliminar las APK validadas.

Las APK y las cachés locales no deben incorporarse
al repositorio Git.

## 9. Instalación y pruebas

La instalación validada se realizó mediante ADB
desde Windows, conectado al dispositivo Android.

Se utilizó instalación con actualización:

    adb install -r archivo.apk

Esta opción conserva los datos de la aplicación
si la actualización es compatible.

No desinstalar Helios como procedimiento habitual
de actualización, ya que podría eliminar datos.

Después de instalar, verificar:

1. Inicio de la aplicación.
2. Navegación.
3. Gráficos y desplazamiento.
4. Botón Atrás.
5. Importación de Excel.
6. Análisis completo.
7. Generación y acceso al informe.
8. Ausencia de cierres inesperados.

## 10. Registros de compilación

Conservar los registros extensos comprimidos.

Registro de la compilación validada:

    backups/logs/compilacion-paso829.log.gz

Para consultar un registro comprimido:

    zless backups/logs/compilacion-paso829.log.gz

No eliminar registros ni cachés mientras
se investiga una incidencia de compilación.

## 11. Precauciones

Antes de modificar el entorno:

- Comprobar git status.
- Conservar las APK funcionales.
- Verificar el commit de python-for-android.
- Mantener el orden de los siete parches.
- No actualizar dependencias indiscriminadamente.
- No limpiar las cachés sin una justificación.
- Probar las modificaciones de forma incremental.
- Guardar los registros de errores.
- Validar el flujo completo después de compilar.

## 12. Trabajo pendiente

- Automatizar la aplicación inicial de los parches
  sobre un checkout limpio sin afectar al validado.
- Probar una recuperación desde cero en una ruta
  independiente.
- Documentar el procedimiento de publicación
  de versiones de producción.
- Validar compatibilidad en otros dispositivos.

La configuración existente y las APK de referencia
deben conservarse hasta completar estas pruebas.
