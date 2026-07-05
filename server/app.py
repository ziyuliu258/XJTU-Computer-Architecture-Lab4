"""Cache Simulator A — FastAPI 接口。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sim_a.schemas import (
    CacheStats,
    SimulateRequest,
    SimulateResponse,
    SweepPoint,
)
from sim_a.simulator import run_trace

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

app = FastAPI(title="Simulator A · Cache API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_SAMPLE_DEFS = [
    ("022.li.din",      "022.li      Lisp 解释器"),
    ("047.tomcatv.din", "047.tomcatv 矩阵转置"),
    ("078.swm256.din",  "078.swm256  浅水方程"),
    ("085.gcc.din",     "085.gcc     C 编译器"),
]


class SampleTrace(BaseModel):
    name: str
    title: str
    data: str


@app.get("/api/samples", response_model=list[SampleTrace])
def list_samples() -> list[SampleTrace]:
    result = []
    for filename, title in _SAMPLE_DEFS:
        path = DATA / filename
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        result.append(SampleTrace(name=filename, title=title, data=content))
    return result


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
