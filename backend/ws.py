import asyncio
from collections import deque
from dataclasses import asdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from stats.models import ExperimentConfig
from stats.simulator import DataSimulator
from stats.sequential import MixtureSPRT
from stats.guardrail import GuardrailEngine

router = APIRouter()

@router.websocket("/ws/experiment")
async def experiment_ws(
    websocket: WebSocket,
    p_control: float = 0.10,
    tau: float = 0.02,
    true_effect: float = 0.03,
    delay: float = 0.05,
):
    await websocket.accept()

    config = ExperimentConfig(p_control=p_control, tau=tau)
    sim = DataSimulator(config, true_effect=true_effect)
    sprt = MixtureSPRT(config)
    guardrail = GuardrailEngine()

    ctrl_queue: deque = deque()
    trt_queue: deque = deque()

    try:
        for event in sim.stream():
            test_state = sprt.update(event)

            if event.arm == "control":
                ctrl_queue.append(event)
            else:
                trt_queue.append(event)

            guardrail_state = None

            if ctrl_queue and trt_queue:
                guardrail_state = guardrail.update(ctrl_queue.popleft(), trt_queue.popleft())

            await websocket.send_json({
                "test": asdict(test_state),
                "guardrail": asdict(guardrail_state) if guardrail_state else None
            })

            if test_state.status != "running":
                break
            if guardrail_state and guardrail_state.status == "paused":
                break

            await asyncio.sleep(delay)

    except WebSocketDisconnect:
        pass
    