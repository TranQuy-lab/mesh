#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "$0")" && pwd)
sdk_dir=$(cd "$project_dir/.." && pwd)/.android-sdk
tools_dir="$sdk_dir/build-tools/36.0.0"
android_jar="$sdk_dir/platforms/android-36/android.jar"
build_dir="$project_dir/build"

mkdir -p "$build_dir/classes" "$build_dir/dex"

"$tools_dir/aapt2" compile --dir "$project_dir/res" -o "$build_dir/resources.flata"

"$tools_dir/aapt2" link \
  -o "$build_dir/resources.apk" \
  -I "$android_jar" \
  -R "$build_dir/resources.flata" \
  -A "$project_dir/assets" \
  --manifest "$project_dir/AndroidManifest.xml" \
  --min-sdk-version 26 \
  --target-sdk-version 36

mapfile -t java_files < <(find "$project_dir/src" -name "*.java" | sort)
javac -source 11 -target 11 \
  -cp "$android_jar" \
  -d "$build_dir/classes" \
  "${java_files[@]}"

jar --create --file "$build_dir/classes.jar" -C "$build_dir/classes" .
"$tools_dir/d8" --lib "$android_jar" --min-api 26 \
  --output "$build_dir/dex" "$build_dir/classes.jar"
cp "$build_dir/resources.apk" "$build_dir/unsigned.apk"
zip -q -j "$build_dir/unsigned.apk" "$build_dir/dex/classes.dex"
"$tools_dir/zipalign" -f 4 "$build_dir/unsigned.apk" "$build_dir/aligned.apk"

if [[ ! -f "$build_dir/debug.keystore" ]]; then
  keytool -genkeypair -noprompt \
    -keystore "$build_dir/debug.keystore" \
    -storepass android -keypass android -alias androiddebugkey \
    -dname "CN=RescueMesh G0,O=Research,C=VN" \
    -keyalg RSA -keysize 2048 -validity 3650
fi

"$tools_dir/apksigner" sign \
  --ks "$build_dir/debug.keystore" \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$build_dir/rescuemesh-g0.apk" \
  "$build_dir/aligned.apk"

"$tools_dir/apksigner" verify --verbose "$build_dir/rescuemesh-g0.apk"
mkdir -p "$project_dir/../releases"
cp "$build_dir/rescuemesh-g0.apk" "$project_dir/../releases/rescuemesh-g0.apk"
echo "$build_dir/rescuemesh-g0.apk"
