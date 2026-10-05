#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "$0")" && pwd)
sdk_dir=$(cd "$project_dir/.." && pwd)/.android-sdk
android_jar="$sdk_dir/platforms/android-36/android.jar"
classes_dir="$project_dir/build/detector-test-classes"
mkdir -p "$classes_dir"
mapfile -t src_files < <(find "$project_dir/src" -name "*.java" | sort)
mapfile -t test_files < <(find "$project_dir/test" -name "*.java" | sort)
javac -source 11 -target 11 -cp "$android_jar" -d "$classes_dir" "${src_files[@]}" "${test_files[@]}"
java -cp "$classes_dir" org.rescuemesh.g0.DetectorSelfTest
