#!/bin/bash
# Build and flash the Waveshare ESP32-S3-Touch-AMOLED-1.75C.
#
#   tools/my-board.sh [build|flash|monitor] [PORT]
#
# The SDK token is read from ~/.config/muse/sdkconfig.token, outside the repo,
# as one line: CONFIG_GADGET_SDK_TOKEN="mgst_..."
set -euo pipefail
cmd=${1:-flash}
port=${2:-/dev/cu.usbmodem1101}
token=${MUSE_TOKEN_FILE:-$HOME/.config/muse/sdkconfig.token}
[ -f "$token" ] || { echo "no SDK token file at $token" >&2; exit 1; }
cd "$(dirname "$0")/.."
command -v idf.py >/dev/null 2>&1 || . "$HOME/esp/esp-idf-v6/export.sh" >/dev/null 2>&1
B=build-muse-waveshare-s3-175c
args=(-B $B -DIDF_TARGET=esp32s3 -DSDKCONFIG=$B/sdkconfig
      -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;devices/sdkconfig.muse;devices/sdkconfig.muse-waveshare-s3-175c;$token")
case $cmd in
    build)   idf.py "${args[@]}" build ;;
    flash)   idf.py "${args[@]}" -p "$port" build flash ;;
    monitor) idf.py "${args[@]}" -p "$port" monitor ;;
    *) echo "usage: $0 [build|flash|monitor] [PORT]" >&2; exit 2 ;;
esac
