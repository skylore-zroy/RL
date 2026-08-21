# Isaac Lab 2.2.0 is the NVIDIA image paired with Isaac Sim 5.0.
FROM nvcr.io/nvidia/isaac-lab:2.2.0

USER root
WORKDIR /workspace/cod-rl

ENV ACCEPT_EULA=Y \
    OMNI_KIT_ACCEPT_EULA=YES \
    PYTHONUNBUFFERED=1

COPY models/cod_balance/usd/ models/cod_balance/usd/
COPY scripts/open_cod_isaac.py scripts/open_cod_isaac.py

ENTRYPOINT ["/workspace/IsaacLab/isaaclab.sh", "-p"]
CMD ["/workspace/cod-rl/scripts/open_cod_isaac.py", "/workspace/cod-rl/models/cod_balance/usd/COD-2026RoboMaster-Balance.usd", "--headless", "--free-base", "--simulate", "--report", "/workspace/validation_results/isaac_model_report.json"]