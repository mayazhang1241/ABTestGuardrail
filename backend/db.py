import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.Pool | None = None

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/abtest")

_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS experiments (
    id           SERIAL PRIMARY KEY,
    p_control    DOUBLE PRECISION NOT NULL,
    tau          DOUBLE PRECISION NOT NULL,
    true_effect  DOUBLE PRECISION NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at     TIMESTAMPTZ,
    final_status TEXT
);

CREATE TABLE IF NOT EXISTS stat_snapshots (
    ts                  TIMESTAMPTZ      NOT NULL,
    experiment_id       INT              NOT NULL REFERENCES experiments(id),
    n_control           INT              NOT NULL,
    n_treatment         INT              NOT NULL,
    p_hat_control       DOUBLE PRECISION NOT NULL,
    p_hat_treatment     DOUBLE PRECISION NOT NULL,
    mixture_stat        DOUBLE PRECISION NOT NULL,
    test_status         TEXT             NOT NULL,
    guardrail_n_pairs   INT,
    guardrail_mean_diff DOUBLE PRECISION,
    guardrail_z_score   DOUBLE PRECISION,
    guardrail_status    TEXT
);

SELECT create_hypertable('stat_snapshots', 'ts', if_not_exists => TRUE);
"""

async def init_pool():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL)
    async with _pool.acquire() as conn:
        await conn.execute(_SCHEMA)

async def close_pool():
    if _pool:
        await _pool.close()

def get_pool() -> asyncpg.Pool:
    return _pool

async def create_experiment(p_control: float, tau: float, true_effect: float) -> int:
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO experiments (p_control, tau, true_effect) VALUES ($1, $2, $3) RETURNING id",
            p_control, tau, true_effect,
        )
        return row["id"]

async def finish_experiment(experiment_id: int, status: str):
    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE experiments SET ended_at = NOW(), final_status = $1 WHERE id = $2",
            status, experiment_id,
        )

async def insert_snapshot(experiment_id: int, test_state, guardrail_state):
    from datetime import datetime, timezone
    async with _pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO stat_snapshots (
                ts, experiment_id,
                n_control, n_treatment, p_hat_control, p_hat_treatment,
                mixture_stat, test_status,
                guardrail_n_pairs, guardrail_mean_diff, guardrail_z_score, guardrail_status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
            datetime.now(timezone.utc), experiment_id,
            test_state.n_control, test_state.n_treatment,
            test_state.p_hat_control, test_state.p_hat_treatment,
            test_state.mixture_stat, test_state.status,
            guardrail_state.n_pairs if guardrail_state else None,
            guardrail_state.mean_diff if guardrail_state else None,
            guardrail_state.z_score if guardrail_state else None,
            guardrail_state.status if guardrail_state else None,
        )

async def list_experiments():
    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, p_control, tau, true_effect, started_at, ended_at, final_status "
            "FROM experiments ORDER BY started_at DESC"
        )
        return [dict(r) for r in rows]

async def get_experiment_history(experiment_id: int):
    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ts, n_control, n_treatment, p_hat_control, p_hat_treatment,
                   mixture_stat, test_status,
                   guardrail_n_pairs, guardrail_mean_diff, guardrail_z_score, guardrail_status
            FROM stat_snapshots
            WHERE experiment_id = $1
            ORDER BY ts ASC
            """,
            experiment_id,
        )
        return [dict(r) for r in rows]