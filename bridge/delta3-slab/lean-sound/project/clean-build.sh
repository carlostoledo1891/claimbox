#!/bin/bash
# the clean build: every local module (Astra, Model, Sound) rebuilt from source; Mathlib from its cache
cd /root/work/bridge
export PATH=$HOME/.elan/bin:$PATH
echo "CLEAN-BUILD start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
lean --version; lake --version; nproc
echo "--- sources (sha256)"
sha256sum lakefile.toml lean-toolchain lake-manifest.json astra/*.lean model/*.lean Sound/*.lean attempt/*.lean
rm -rf .lake/build
echo "--- removed .lake/build; lake build (default targets Astra Model Sound)"
start=$(date +%s)
lake build
rc=$?
end=$(date +%s)
echo "CLEAN-BUILD lake build exit $rc, wall $((end-start)) s, end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "--- kernel (type checking) seconds summed over the profiler lines"
grep -oE "type checking [0-9.]+(ms|s)" /root/work/bridge/logs/clean-build.log | awk "{v=\$3; if (v ~ /ms\$/) {sub(/ms/,\"\",v); s+=v/1000} else {sub(/s/,\"\",v); s+=v}} END {printf \"KERNEL-SUM %.1f s over %d lines\n\", s, NR}"
