"""Core cache simulation logic for Lab 4."""

from collections import OrderedDict


class CacheSet:
    def __init__(self, associativity: int):
        self.ways = associativity
        self._lines: OrderedDict[int, bool] = OrderedDict()

    def access(self, tag: int, is_write: bool) -> tuple[bool, bool]:
        if tag in self._lines:
            dirty = self._lines.pop(tag)
            self._lines[tag] = dirty or is_write
            return True, False
        evicted = len(self._lines) >= self.ways
        if evicted:
            self._lines.popitem(last=False)
        self._lines[tag] = is_write
        return False, evicted


class CacheSimulator:
    def __init__(self, cache_size: int, associativity: int, block_size: int):
        assert cache_size % (associativity * block_size) == 0
        self._ob = (block_size - 1).bit_length()
        self._ns = cache_size // (associativity * block_size)
        self._ib = (self._ns - 1).bit_length() if self._ns > 1 else 0
        self._sets = [CacheSet(associativity) for _ in range(self._ns)]
        self.read_accesses = self.read_misses = 0
        self.write_accesses = self.write_misses = self.evictions = 0

    def _decode(self, addr: int) -> tuple[int, int]:
        si = (addr >> self._ob) & (self._ns - 1)
        tag = addr >> (self._ob + self._ib)
        return si, tag

    def access(self, address: int, is_write: bool) -> None:
        si, tag = self._decode(address)
        hit, evicted = self._sets[si].access(tag, is_write)
        if is_write:
            self.write_accesses += 1
            if not hit:
                self.write_misses += 1
        else:
            self.read_accesses += 1
            if not hit:
                self.read_misses += 1
        if evicted:
            self.evictions += 1

    def stats(self) -> dict:
        total = self.read_accesses + self.write_accesses
        tm = self.read_misses + self.write_misses
        return {
            "read_accesses":   self.read_accesses,
            "read_misses":     self.read_misses,
            "read_miss_rate":  self.read_misses / self.read_accesses if self.read_accesses else 0.0,
            "write_accesses":  self.write_accesses,
            "write_misses":    self.write_misses,
            "write_miss_rate": self.write_misses / self.write_accesses if self.write_accesses else 0.0,
            "total_accesses":  total,
            "total_misses":    tm,
            "total_miss_rate": tm / total if total else 0.0,
            "evictions":       self.evictions,
        }


def run_trace(trace_data: str, cache_size: int, associativity: int, block_size: int) -> dict:
    sim = CacheSimulator(cache_size, associativity, block_size)
    for line in trace_data.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            at = int(parts[0])
        except ValueError:
            continue
        if at == 2:
            continue
        try:
            sim.access(int(parts[1], 16), is_write=(at == 1))
        except ValueError:
            continue
    return sim.stats()
