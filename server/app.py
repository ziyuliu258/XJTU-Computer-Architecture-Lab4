"""Cache Simulator A — FastAPI 接口。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sim_a.schemas import (
    CacheStats,
    SimulateRequest,
    SimulateResponse,
    SweepPoint,
)
from sim_a.simulator import run_trace

app = FastAPI(title="Simulator A · Cache API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_SIZES  = [8192,  16384, 32768, 65536]
ASSOCS       = [1, 2, 4, 8]
BLOCK_SIZES  = [16, 32, 64, 128]
SIZE_LABELS  = ["8 KB", "16 KB", "32 KB", "64 KB"]
ASSOC_LABELS = ["1-way", "2-way", "4-way", "8-way"]
BLOCK_LABELS = ["16 B", "32 B", "64 B", "128 B"]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(payload: SimulateRequest) -> SimulateResponse:
    cfg = payload.config
    raw = run_trace(payload.trace_data, cfg.cache_size, cfg.associativity, cfg.block_size)
    stats = CacheStats(**raw)

    sweep_size, sweep_assoc, sweep_block = [], [], []
    if payload.run_sweep:
        for cs, lbl in zip(CACHE_SIZES, SIZE_LABELS):
            s = run_trace(payload.trace_data, cs, 2, 32)
            sweep_size.append(SweepPoint(label=lbl, **_rates(s)))

        for wa, lbl in zip(ASSOCS, ASSOC_LABELS):
            s = run_trace(payload.trace_data, 16384, wa, 32)
            sweep_assoc.append(SweepPoint(label=lbl, **_rates(s)))

        for bs, lbl in zip(BLOCK_SIZES, BLOCK_LABELS):
            s = run_trace(payload.trace_data, 16384, 2, bs)
            sweep_block.append(SweepPoint(label=lbl, **_rates(s)))

    return SimulateResponse(
        stats=stats,
        sweep_by_size=sweep_size,
        sweep_by_assoc=sweep_assoc,
        sweep_by_block=sweep_block,
    )


def _rates(s: dict) -> dict:
    return {
        "read_miss_rate":  round(s["read_miss_rate"]  * 100, 3),
        "write_miss_rate": round(s["write_miss_rate"] * 100, 3),
        "total_miss_rate": round(s["total_miss_rate"] * 100, 3),
    }
