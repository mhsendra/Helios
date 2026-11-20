#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

P4A_DIR="${HELIOS_P4A_DIR:-$HOME/.cache/helios/python-for-android}"
VENV_DIR="${HELIOS_DEPLOY_VENV:-$HOME/venvs/helios-deploy}"
SDK_DIR="${HELIOS_ANDROID_SDK:-$HOME/.pyside6_android_deploy/android-sdk}"
NDK_DIR="${HELIOS_ANDROID_NDK:-$SDK_DIR/ndk/28.2.13676358}"
WHEELS_DIR="${HELIOS_ANDROID_WHEELS:-$HOME/.pyside6_android_deploy/wheels}"

COMMAND="${1:-debug}"

case "$COMMAND" in
    debug|release|clean) ;;
    *)
        echo "Uso: $0 {debug|release|clean}"
        exit 2
        ;;
esac

for path in \
    "$P4A_DIR/pythonforandroid" \
    "$VENV_DIR/bin/activate" \
    "$SDK_DIR" \
    "$NDK_DIR" \
    "$WHEELS_DIR/pyside6-android-aarch64.whl" \
    "$WHEELS_DIR/shiboken6-android-aarch64.whl"
do
    if [[ ! -e "$path" ]]; then
        echo "ERROR: falta $path" >&2
        exit 1
    fi
done

export APP_ANDROID_SDK_PATH="$SDK_DIR"
export APP_ANDROID_NDK_PATH="$NDK_DIR"
export APP_P4A_SOURCE_DIR="$P4A_DIR"
export HELIOS_ANDROID_WHEELS="$WHEELS_DIR"

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

cd "$ROOT"

python - "$P4A_DIR" "$COMMAND" <<'PY'
from pathlib import Path
from tempfile import NamedTemporaryFile
from buildozer import Buildozer
import sys

p4a_dir = Path(sys.argv[1]).resolve()
command = sys.argv[2]
root = Path.cwd().resolve()

content = (root / "buildozer.spec").read_text(encoding="utf-8")

if "p4a.source_dir" in content:
    raise SystemExit("ERROR: p4a.source_dir ya está definido")

content = content.replace(
    "[app]",
    f"[app]\np4a.source_dir = {p4a_dir}",
    1,
)

with NamedTemporaryFile(
    mode="w",
    prefix=".helios-ui-test-",
    suffix=".spec",
    dir=root,
    encoding="utf-8",
    delete=True,
) as temporary:
    temporary.write(content)
    temporary.flush()

    builder = Buildozer(filename=temporary.name)

    if Path(builder.root_dir).resolve() != root:
        raise SystemExit("ERROR: raíz Buildozer incorrecta")

    if Path(builder.buildozer_dir).resolve() != root / ".buildozer":
        raise SystemExit("ERROR: caché no aislada")

    builder.set_target("android")

    if Path(builder.target.p4a_dir).resolve() != p4a_dir:
        raise SystemExit("ERROR: checkout P4A incorrecto")

    print("Laboratorio:", root, flush=True)
    print("P4A:", p4a_dir, flush=True)
    print("Caché:", builder.buildozer_dir, flush=True)

    builder.run_command(["android", command])
PY
