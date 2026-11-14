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
)

PENDING=()

echo "========== 1. COMPROBAR PARCHES =========="

for name in "${PATCHES[@]}"; do
    patch="$PATCH_DIR/$name"

    if [[ ! -f "$patch" ]]; then
        echo "ERROR: no se encuentra el parche: $patch"
        exit 1
    fi

    if git -C "$P4A_DIR" apply --reverse --check "$patch" >/dev/null 2>&1; then
        echo "YA APLICADO: $name"
    elif git -C "$P4A_DIR" apply --check "$patch" >/dev/null 2>&1; then
        echo "PENDIENTE:   $name"
        PENDING+=("$name")
    else
        echo "ERROR: parche incompatible: $name"
        echo "No se ha aplicado ningún parche."
        exit 1
    fi
done

echo
echo "========== 2. APLICAR PARCHES PENDIENTES =========="

if [[ ${#PENDING[@]} -eq 0 ]]; then
    echo "No hay cambios pendientes."
else
    for name in "${PENDING[@]}"; do
        echo "Aplicando: $name"
        git -C "$P4A_DIR" apply "$PATCH_DIR/$name"
    done
fi

echo
echo "========== 3. VERIFICACIÓN FINAL =========="

for name in "${PATCHES[@]}"; do
    if ! git -C "$P4A_DIR" apply --reverse --check "$PATCH_DIR/$name" >/dev/null 2>&1; then
        echo "ERROR: no se pudo verificar el parche: $name"
        exit 1
    fi
    echo "OK: $name"
done

echo
echo "========== 4. ESTADO DE P4A =========="
git -C "$P4A_DIR" status --short

echo
echo "Proceso completado correctamente."
