"""Pydantic models for Cache Simulator A API."""

from pydantic import BaseModel


class CacheConfig(BaseModel):
    cache_size: int = 16384    # bytes
    associativity: int = 2
    block_size: int = 32       # bytes


class SimulateRequest(BaseModel):
    trace_data: str            # raw text of .din file
    config: CacheConfig = CacheConfig()
    run_sweep: bool = True     # also run parameter sweeps


class CacheStats(BaseModel):
    read_accesses: int
    read_misses: int
    read_miss_rate: float
    write_accesses: int
    write_misses: int
    write_miss_rate: float
    total_accesses: int
    total_misses: int
    total_miss_rate: float
    evictions: int


class SweepPoint(BaseModel):
    label: str
    read_miss_rate: float
    write_miss_rate: float
    total_miss_rate: float


class SimulateResponse(BaseModel):
    stats: CacheStats
    sweep_by_size: list[SweepPoint]    # 2-way, 32B, vary cache size
    sweep_by_assoc: list[SweepPoint]   # 16KB, 32B, vary associativity
    sweep_by_block: list[SweepPoint]   # 16KB, 2-way, vary block size
