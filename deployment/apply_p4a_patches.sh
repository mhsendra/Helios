#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_COMMIT="58d21141f17c889bf8585f5665921d72028f8831"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PATCH_DIR="$SCRIPT_DIR/patches"

P4A_DIR="${1:-${P4A_SOURCE_DIR:-}}"

if [[ -z "$P4A_DIR" ]]; then
    echo "ERROR: indica el directorio de python-for-android."
    echo "Uso: $0 /ruta/a/python-for-android"
    echo "También puedes definir P4A_SOURCE_DIR."
    exit 1
fi

if [[ ! -d "$P4A_DIR" ]]; then
    echo "ERROR: no existe el directorio: $P4A_DIR"
    exit 1
fi

P4A_DIR="$(cd -- "$P4A_DIR" && pwd)"

if ! git -C "$P4A_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: el directorio indicado no es un repositorio Git."
    exit 1
fi

REPO_ROOT="$(git -C "$P4A_DIR" rev-parse --show-toplevel)"
if [[ "$REPO_ROOT" != "$P4A_DIR" ]]; then
    echo "ERROR: la ruta indicada no es la raíz del repositorio P4A."
    echo "Raíz detectada: $REPO_ROOT"
    exit 1
fi

ACTUAL_COMMIT="$(git -C "$P4A_DIR" rev-parse HEAD)"

if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
    echo "ERROR: versión de P4A inesperada."
    echo "Esperada: $EXPECTED_COMMIT"
    echo "Actual:   $ACTUAL_COMMIT"
    exit 1
fi

PATCHES=(
    "0001-recreate-host-venv.patch"
    "0002-create-adaptive-icon-directory.patch"
    "0003-remove-generic-back-handler.patch"
    "0004-refresh-helios-package.patch"
    "0005-helios-launch-background.patch"
    "0006-android-excel-picker.patch"
    "0007-android-pdf-export.patch"
)

echo "========== 1. RECONSTRUIR ESTADO ESPERADO =========="

TEMP_DIR="$(mktemp -d -t helios-p4a-patches-XXXXXXXX)"

cleanup() {
    rm -rf -- "$TEMP_DIR"
}

trap cleanup EXIT

git -C "$P4A_DIR" archive "$EXPECTED_COMMIT" |
    tar -xf - -C "$TEMP_DIR"

for name in "${PATCHES[@]}"; do
    patch="$PATCH_DIR/$name"

    if [[ ! -f "$patch" ]]; then
        echo "ERROR: falta el parche: $name"
        exit 1
    fi

    if ! git -C "$TEMP_DIR" apply --check "$patch"; then
        echo "ERROR: parche incompatible: $name"
        exit 1
    fi

    git -C "$TEMP_DIR" apply "$patch"
    echo "OK: $name"
done

echo
echo "========== 2. COMPARAR ESTADO ACTUAL =========="

mapfile -t AFFECTED_FILES < <(
    for name in "${PATCHES[@]}"; do
        git apply --numstat "$PATCH_DIR/$name" |
            cut -f3
    done | sort -u
)

for relative in "${AFFECTED_FILES[@]}"; do
    expected="$TEMP_DIR/$relative"
    actual="$P4A_DIR/$relative"

    if [[ ! -f "$expected" || ! -f "$actual" ]]; then
        echo "ERROR: archivo ausente: $relative"
        exit 1
    fi

    if ! cmp -s "$expected" "$actual"; then
        echo "ERROR: archivo diferente: $relative"
        echo "No se han aplicado cambios."
        exit 1
    fi

    echo "OK: $relative"
done

echo
echo "========== 3. VERIFICACIÓN FINAL =========="
echo "OK: los siete parches están incorporados."
echo "OK: el estado de P4A coincide con la reconstrucción."
echo "OK: no se han modificado archivos de P4A."

echo "========== 4. ESTADO DE P4A =========="
git -C "$P4A_DIR" status --short

echo
echo "Proceso completado correctamente."
