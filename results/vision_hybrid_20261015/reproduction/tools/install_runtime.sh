#!/usr/bin/env bash
set -euo pipefail
cd /workspace
if [ ! -x /workspace/venvs/safe_iad/bin/python ]; then
  python3 -m venv --system-site-packages /workspace/venvs/safe_iad
fi
PIP_CACHE_DIR=/workspace/.cache/pip /workspace/venvs/safe_iad/bin/python -m pip install --index-url https://download.pytorch.org/whl/cpu -r /workspace/tools/requirements-baseline.txt
PIP_CACHE_DIR=/workspace/.cache/pip /workspace/venvs/safe_iad/bin/python -m pip install --index-url https://download.pytorch.org/whl/cpu torchvision==0.22.1+cpu
PIP_CACHE_DIR=/workspace/.cache/pip /workspace/venvs/safe_iad/bin/python -m pip install -r /workspace/tools/requirements-pipeline.txt
/workspace/venvs/safe_iad/bin/python -m pip install --no-build-isolation --no-deps -e /workspace/tools
/workspace/venvs/safe_iad/bin/python -c 'import torch, numpy, PIL, sklearn; print("CPU research runtime:", torch.__version__)'
# Keep the official backbone dependency at the verified source revision.
dinov2_cache=/workspace/.cache/dinov2-source
dinov2_revision=7764ea0f912e53c92e82eb78a2a1631e92725fc8
if [ ! -e "$dinov2_cache" ]; then
  git clone --depth 1 --no-checkout https://github.com/facebookresearch/dinov2.git "$dinov2_cache"
  git -C "$dinov2_cache" fetch --depth 1 origin "$dinov2_revision"
  git -C "$dinov2_cache" checkout --detach "$dinov2_revision"
fi

# Keep the official baseline scoring dependencies intact and pinned.
baseline_names=(anomalydino subspacead)
baseline_urls=(https://github.com/dammsi/AnomalyDINO.git https://github.com/CLendering/SubspaceAD.git)
baseline_revisions=(b9d1c2648e3a5247437d4d953d907a8f3d994457 ef56d5c8ab2f1feb7dda1c93b25cc3f73f0960d7)
for baseline_index in 0 1; do
  baseline_cache="/workspace/.cache/${baseline_names[$baseline_index]}-source"
  baseline_pin="${baseline_revisions[$baseline_index]}"
  if [ ! -e "$baseline_cache" ]; then
    git clone --depth 1 --no-checkout "${baseline_urls[$baseline_index]}" "$baseline_cache"
    git -C "$baseline_cache" fetch --depth 1 origin "$baseline_pin"
    git -C "$baseline_cache" checkout --detach "$baseline_pin"
  fi
  if [ "$(git -C "$baseline_cache" rev-parse HEAD)" != "$baseline_pin" ]; then
    echo 'Baseline dependency revision differs from the pin; preserve it and investigate.' >&2
    exit 1
  fi
done
if [ "$(git -C "$dinov2_cache" rev-parse HEAD)" != "$dinov2_revision" ]; then
  echo 'DINOv2 dependency revision differs from the verified pin; preserve it and investigate.' >&2
  exit 1
fi
