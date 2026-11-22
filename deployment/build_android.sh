#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_COMMIT="58d21141f17c889bf8585f5665921d72028f8831"
P4A_URL="https://github.com/kivy/python-for-android.git"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

P4A_DIR="${HELIOS_P4A_DIR:-$REPO_ROOT/deployment/python-for-android-local}"
VENV_DIR="${HELIOS_DEPLOY_VENV:-$HOME/venvs/helios-deploy}"
SDK_DIR="${HELIOS_ANDROID_SDK:-$HOME/.buildozer/android/platform/android-sdk}"
NDK_DIR="${HELIOS_ANDROID_NDK:-$HOME/.buildozer/android/platform/android-ndk-r28c}"
WHEELS_DIR="${HELIOS_ANDROID_WHEELS:-$HOME/.pyside6_android_deploy/wheels}"

COMMAND="${1:-prepare}"
if [[ $# -gt 0 ]]; then
    shift
fi

case "$COMMAND" in
    prepare|debug|release|deploy|run) ;;
    *)
        echo "Uso: $0 {prepare|debug|release|deploy|run}"
        exit 2
        ;;
esac

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

echo "========== 1. VALIDAR HERRAMIENTAS =========="

[[ -f "$VENV_DIR/bin/activate" ]] ||
    fail "No existe el entorno: $VENV_DIR"

[[ -d "$SDK_DIR" ]] ||
    fail "No existe el SDK: $SDK_DIR"

[[ -d "$NDK_DIR" ]] ||
    fail "No existe el NDK: $NDK_DIR"

[[ -f "$WHEELS_DIR/pyside6-android-aarch64.whl" ]] ||
    fail "Falta el wheel Android de PySide6"

[[ -f "$WHEELS_DIR/shiboken6-android-aarch64.whl" ]] ||
    fail "Falta el wheel Android de Shiboken6"

[[ -f "$REPO_ROOT/buildozer.spec" ]] ||
    fail "No existe buildozer.spec"

[[ -x "$SCRIPT_DIR/apply_p4a_patches.sh" ]] ||
    fail "No existe el aplicador de parches ejecutable"

command -v git >/dev/null ||
    fail "Git no está disponible"

echo "Herramientas y archivos comprobados."

echo
echo "========== 2. PREPARAR CHECKOUT P4A =========="

if [[ ! -e "$P4A_DIR" ]]; then
    mkdir -p "$(dirname "$P4A_DIR")"
    git clone --branch master --single-branch \
        "$P4A_URL" "$P4A_DIR"
fi

[[ -d "$P4A_DIR/.git" ]] ||
    fail "La ruta P4A no es un checkout Git válido: $P4A_DIR"

P4A_ROOT="$(git -C "$P4A_DIR" rev-parse --show-toplevel)"
[[ "$P4A_ROOT" == "$P4A_DIR" ]] ||
    fail "La ruta no corresponde a la raíz del checkout P4A"

ORIGIN="$(git -C "$P4A_DIR" remote get-url origin)"
BUILDOZER_P4A="$REPO_ROOT/.buildozer/android/platform/python-for-android"

case "$ORIGIN" in
    "$P4A_URL"|"https://github.com/kivy/python-for-android")
        ;;
    *)
        if [[ "$ORIGIN" != "$BUILDOZER_P4A" ]]; then
            fail "Origen Git P4A inesperado: $ORIGIN"
        fi

        [[ -d "$BUILDOZER_P4A/.git" ]] ||
            fail "No existe el repositorio P4A original de Buildozer"

        [[ "$(git -C "$BUILDOZER_P4A" rev-parse HEAD)" == "$EXPECTED_COMMIT" ]] ||
            fail "El repositorio P4A de Buildozer tiene otro commit"
        ;;
esac

EXPECTED_FILES=(
    "pythonforandroid/build.py"
    "pythonforandroid/bootstraps/common/build/build.py"
    "pythonforandroid/bootstraps/qt/build/src/main/java/org/kivy/android/PythonActivity.java"
    "pythonforandroid/bootstraps/qt/build/templates/strings.tmpl.xml"
)

check_worktree() {
    local file
    local allowed
    local found

    [[ -z "$(git -C "$P4A_DIR" diff --cached --name-only)" ]] ||
        fail "P4A contiene cambios preparados en el índice Git"

    [[ -z "$(git -C "$P4A_DIR" ls-files --others --exclude-standard)" ]] ||
        fail "P4A contiene archivos no rastreados"

    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        found=0

        for allowed in "${EXPECTED_FILES[@]}"; do
            if [[ "$file" == "$allowed" ]]; then
                found=1
                break
            fi
        done

        [[ "$found" -eq 1 ]] ||
            fail "Modificación inesperada en P4A: $file"
    done < <(git -C "$P4A_DIR" diff --name-only)
}

check_worktree

CURRENT_COMMIT="$(git -C "$P4A_DIR" rev-parse HEAD)"

if [[ "$CURRENT_COMMIT" != "$EXPECTED_COMMIT" ]]; then
    [[ -z "$(git -C "$P4A_DIR" diff --name-only)" ]] ||
        fail "No se cambiará de commit con modificaciones locales"

    git -C "$P4A_DIR" cat-file -e "${EXPECTED_COMMIT}^{commit}" ||
        fail "El commit fijado no está disponible en el checkout"

    git -C "$P4A_DIR" checkout --detach "$EXPECTED_COMMIT"
fi

[[ "$(git -C "$P4A_DIR" rev-parse HEAD)" == "$EXPECTED_COMMIT" ]] ||
    fail "El checkout P4A no coincide con el commit esperado"

echo "Commit P4A: $EXPECTED_COMMIT"

echo
echo "========== 3. APLICAR PARCHES =========="

"$SCRIPT_DIR/apply_p4a_patches.sh" "$P4A_DIR"

check_worktree

ACTUAL_FILES="$(git -C "$P4A_DIR" diff --name-only | LC_ALL=C sort)"
EXPECTED_SORTED="$(printf '%s\n' "${EXPECTED_FILES[@]}" | LC_ALL=C sort)"

[[ "$ACTUAL_FILES" == "$EXPECTED_SORTED" ]] ||
    fail "El conjunto final de archivos modificados no coincide con los seis parches"

echo
echo "========== 4. CONFIGURAR BUILDOZER =========="

export APP_ANDROID_SDK_PATH="$SDK_DIR"
export APP_ANDROID_NDK_PATH="$NDK_DIR"
export APP_P4A_SOURCE_DIR="$P4A_DIR"
export HELIOS_ANDROID_WHEELS="$WHEELS_DIR"

echo "SDK: $APP_ANDROID_SDK_PATH"
echo "NDK: $APP_ANDROID_NDK_PATH"
echo "P4A: $APP_P4A_SOURCE_DIR"
echo "Wheels: $HELIOS_ANDROID_WHEELS"

if [[ "$COMMAND" == "prepare" ]]; then
    echo
    echo "Preparación completada. No se ha iniciado ninguna compilación."
    exit 0
fi

echo
echo "========== 5. EJECUTAR BUILDOZER =========="

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

command -v buildozer >/dev/null ||
    fail "Buildozer no está instalado en el entorno seleccionado"

cd "$REPO_ROOT"

python - "$P4A_DIR" "$COMMAND" "$@" <<'HELIOS_BUILDOZER_PY'
from pathlib import Path
from tempfile import NamedTemporaryFile
from buildozer import Buildozer
import sys

p4a_dir = Path(sys.argv[1]).resolve()
command = sys.argv[2]
extra_args = sys.argv[3:]

repo = Path.cwd().resolve()
original_spec = repo / "buildozer.spec"

content = original_spec.read_text(encoding="utf-8")

if content.count("[app]") != 1:
    raise SystemExit(
        "ERROR: sección [app] inesperada"
    )

import re

pattern = r"(?m)^p4a\.source_dir\s*=.*$"
matches = re.findall(pattern, content)

if len(matches) > 1:
    raise SystemExit(
        "ERROR: p4a.source_dir aparece varias veces"
    )

if matches:
    content = re.sub(
        pattern,
        lambda _: f"p4a.source_dir = {p4a_dir}",
        content,
        count=1,
    )
else:
    content = content.replace(
        "[app]",
        f"[app]\np4a.source_dir = {p4a_dir}",
        1,
    )

with NamedTemporaryFile(
    mode="w",
    prefix=".helios-deploy-",
    suffix=".spec",
    dir=repo,
    encoding="utf-8",
    delete=True,
) as temporary:
    temporary.write(content)
    temporary.flush()

    builder = Buildozer(filename=temporary.name)

    if Path(builder.root_dir).resolve() != repo:
        raise SystemExit("ERROR: raíz Buildozer incorrecta")

    if Path(builder.buildozer_dir).resolve() != repo / ".buildozer":
        raise SystemExit("ERROR: caché Buildozer incorrecta")

    builder.set_target("android")

    if Path(builder.target.p4a_dir).resolve() != p4a_dir:
        raise SystemExit("ERROR: P4A seleccionado incorrecto")

    print("P4A verificado:", p4a_dir, flush=True)
    print("Caché verificada:", builder.buildozer_dir, flush=True)

    builder.run_command(["android", command, *extra_args])
HELIOS_BUILDOZER_PY
