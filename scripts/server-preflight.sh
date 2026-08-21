#!/usr/bin/env bash
set -euo pipefail

for command_name in docker nvidia-smi awk; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "missing_command=${command_name}" >&2
    exit 1
  fi
done

memory_kib=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
memory_gib=$((memory_kib / 1024 / 1024))
gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
vram_mib=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n 1 | tr -d ' ')
driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1 | tr -d ' ')

echo "gpu=${gpu_name}"
echo "vram_mib=${vram_mib}"
echo "driver=${driver_version}"
echo "system_memory_gib=${memory_gib}"

if (( vram_mib < 16384 )); then
  echo "Isaac Sim 5.0 requires at least 16384 MiB VRAM." >&2
  exit 1
fi
if (( memory_gib < 32 )); then
  echo "Isaac Sim 5.0 requires at least 32 GiB system memory." >&2
  exit 1
fi

docker info >/dev/null
docker compose version
echo "preflight=PASS"