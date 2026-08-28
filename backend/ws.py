import asyncio
from collections import deque
from dataclasses import asdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from stats.models import ExperimentConfig
from stats.simulator import DataSimulator
from stats.sequential import MixtureSPRT
from stats.guardrail import GuardrailEngine
from backend import db

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

    experiment_id = await db.create_experiment(p_control, tau, true_effect)

    ctrl_queue: deque = deque()
    trt_queue: deque = deque()
    final_status = "running"

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

            await db.insert_snapshot(experiment_id, test_state, guardrail_state)

            await websocket.send_json({
                "experiment_id": experiment_id,
                "test": asdict(test_state),
                "guardrail": asdict(guardrail_state) if guardrail_state else None,
            })

            if test_state.status != "running":
                final_status = test_state.status
                break
            if guardrail_state and guardrail_state.status == "paused":
                final_status = "paused"
                break

            await asyncio.sleep(delay)

    except WebSocketDisconnect:
        pass
    finally:
        await db.finish_experiment(experiment_id, final_status)
    