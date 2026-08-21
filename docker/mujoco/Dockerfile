FROM python:3.10-slim-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MUJOCO_GL=egl \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libgl1 libegl1 libglfw3 libglew2.2 libosmesa6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY validation/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt

COPY models/cod_balance/mjcf/ /workspace/models/cod_balance/mjcf/
COPY validation/ /workspace/validation/

ENTRYPOINT ["python", "-m", "validation.inspect_cod_model"]
CMD ["--model", "/workspace/models/cod_balance/mjcf/COD-2026RoboMaster-Balance-free.xml"]