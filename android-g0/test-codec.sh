#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "$0")" && pwd)
classes_dir="$project_dir/build/codec-test-classes"
mkdir -p "$classes_dir"
javac -source 11 -target 11 -d "$classes_dir" \
  "$project_dir/src/org/rescuemesh/g0/SosCodec.java" \
  "$project_dir/test/org/rescuemesh/g0/SosCodecSelfTest.java"
java -cp "$classes_dir" org.rescuemesh.g0.SosCodecSelfTest
