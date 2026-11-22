#!/usr/bin/env bash

set -euo pipefail

BASE="58d21141f17c889bf8585f5665921d72028f8831"

SCRIPT_DIR="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &&
    pwd -P
)"

ROOT="$(
    cd -- "$SCRIPT_DIR/.." &&
    pwd -P
)"

ORIGINAL="$ROOT/deployment/python-for-android-local"
PARCHES="$ROOT/deployment/patches"

if [ "$#" -ne 1 ]; then
    echo "Uso: bash deployment/install_p4a_patches.sh DIRECTORIO"
    exit 1
fi

DESTINO="$1"

echo "========== INSTALAR PARCHES P4A =========="

echo
echo "1. VALIDAR DESTINO"

if [ ! -d "$DESTINO" ]; then
    echo "ERROR: El directorio no existe."
    exit 1
fi

DESTINO="$(cd -- "$DESTINO" && pwd -P)"

if [ "$DESTINO" = "$ORIGINAL" ]; then
    echo "ERROR: No se permite modificar el checkout funcional."
    exit 1
fi

if [ "$DESTINO" = "$ROOT" ]; then
    echo "ERROR: No se permite modificar el repositorio Helios."
    exit 1
fi

if [ ! -f "$DESTINO/.git" ] && [ ! -d "$DESTINO/.git" ]; then
    echo "ERROR: El destino no parece un checkout Git."
    exit 1
fi

if [ "$(git -C "$DESTINO" rev-parse --show-toplevel)" != "$DESTINO" ]; then
    echo "ERROR: El destino debe ser la raiz del checkout."
    exit 1
fi

if [ "$(git -C "$DESTINO" rev-parse HEAD)" != "$BASE" ]; then
    echo "ERROR: Commit base incorrecto."
    exit 1
fi

if [ -n "$(git -C "$DESTINO" status --porcelain)" ]; then
    echo "ERROR: El checkout contiene modificaciones."
    exit 1
fi

echo "CORRECTO: Checkout limpio y revision correcta."

echo
echo "2. LOCALIZAR PARCHES"

mapfile -t LISTA_PARCHES < <(
    find "$PARCHES" \
        -maxdepth 1 \
        -type f \
        -name '000*.patch' |
    LC_ALL=C sort
)

if [ "${#LISTA_PARCHES[@]}" -ne 7 ]; then
    echo "ERROR: Se esperaban siete parches."
    exit 1
fi

for PATCH in "${LISTA_PARCHES[@]}"; do
    test -s "$PATCH"
    echo "OK: $(basename "$PATCH")"
done

echo
echo "3. COMPROBAR APLICACION SECUENCIAL"

INDICE_TEMPORAL="$(mktemp)"

trap 'rm -f "$INDICE_TEMPORAL"' EXIT

rm -f "$INDICE_TEMPORAL"

GIT_INDEX_FILE="$INDICE_TEMPORAL" \
    git -C "$DESTINO" read-tree HEAD

for PATCH in "${LISTA_PARCHES[@]}"; do

    GIT_INDEX_FILE="$INDICE_TEMPORAL" \
        git -C "$DESTINO" apply \
        --cached \
        --check \
        "$PATCH"

    GIT_INDEX_FILE="$INDICE_TEMPORAL" \
        git -C "$DESTINO" apply \
        --cached \
        "$PATCH"

done

echo "CORRECTO: Los siete parches son aplicables."

echo
echo "4. APLICAR PARCHES"

for PATCH in "${LISTA_PARCHES[@]}"; do

    echo "Aplicando: $(basename "$PATCH")"

    git -C "$DESTINO" apply --check "$PATCH"
    git -C "$DESTINO" apply "$PATCH"

done

echo
echo "5. COMPROBAR RESULTADO"

ARCHIVOS=(
    "pythonforandroid/build.py"
    "pythonforandroid/bootstraps/common/build/build.py"
    "pythonforandroid/bootstraps/qt/build/src/main/java/org/kivy/android/PythonActivity.java"
    "pythonforandroid/bootstraps/qt/build/templates/strings.tmpl.xml"
)

ESPERADOS="$(
    printf '%s\n' "${ARCHIVOS[@]}" |
    LC_ALL=C sort
)"

ACTUALES="$(
    git -C "$DESTINO" diff --name-only |
    LC_ALL=C sort
)"

if [ "$ACTUALES" != "$ESPERADOS" ]; then
    echo "ERROR: El conjunto de archivos modificados no coincide."
    exit 1
fi

for ARCHIVO in "${ARCHIVOS[@]}"; do

    HASH_ESPERADO="$(
        GIT_INDEX_FILE="$INDICE_TEMPORAL" \
            git -C "$DESTINO" rev-parse ":$ARCHIVO"
    )"

    HASH_ACTUAL="$(
        git -C "$DESTINO" hash-object "$DESTINO/$ARCHIVO"
    )"

    if [ "$HASH_ESPERADO" != "$HASH_ACTUAL" ]; then
        echo "ERROR: Diferencia en $ARCHIVO"
        exit 1
    fi

    echo "VERIFICADO: $ARCHIVO"

done

echo
echo "6. VERIFICAR INTEGRIDAD DEL CHECKOUT"

if [ -n "$(git -C "$DESTINO" diff --cached --name-only)" ]; then
    echo "ERROR: El indice Git contiene cambios preparados."
    exit 1
fi

if [ -n "$(git -C "$DESTINO" ls-files --others --exclude-standard)" ]; then
    echo "ERROR: Existen archivos nuevos inesperados."
    exit 1
fi

if ! git -C "$DESTINO" diff --check; then
    echo "ERROR: Git detecta problemas en las modificaciones."
    exit 1
fi

echo "CORRECTO: Indice limpio y sin archivos adicionales."

echo
echo "CORRECTO: Recuperacion de python-for-android completada."
