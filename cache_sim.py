#!/usr/bin/env python3
"""
Cache Simulator A  -  Lab 4: Cache Performance Analysis
Architecture: N-way set-associative, LRU replacement, write-allocate policy.

Usage:
    python cache_sim.py <trace_file> [options]

Options:
    -s, --cache-size       Cache size in bytes (8192/16384/32768/65536)
    -a, --associativity    Ways (1/2/4/8)
    -b, --block-size       Block size in bytes (16/32/64/128)
    --batch                Sweep all parameter combinations, print table
"""

import argparse
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
        self.cache_size = cache_size
        self.associativity = associativity
        self.block_size = block_size
        self.num_sets = cache_size // (associativity * block_size)
        self._sets = [CacheSet(associativity) for _ in range(self.num_sets)]
        self.read_accesses = 0
        self.read_misses = 0
        self.write_accesses = 0
        self.write_misses = 0
        self.evictions = 0

    @property
    def _offset_bits(self) -> int:
        return (self.block_size - 1).bit_length()

    @property
    def _index_bits(self) -> int:
        return (self.num_sets - 1).bit_length() if self.num_sets > 1 else 0

    def _decode(self, address: int) -> tuple[int, int]:
        ob = self._offset_bits
        ib = self._index_bits
        set_index = (address >> ob) & (self.num_sets - 1)
        tag = address >> (ob + ib)
        return set_index, tag

    def access(self, address: int, is_write: bool) -> None:
        set_idx, tag = self._decode(address)
        hit, evicted = self._sets[set_idx].access(tag, is_write)
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
        total_misses = self.read_misses + self.write_misses
        return {
            'read_accesses':   self.read_accesses,
            'read_misses':     self.read_misses,
            'read_miss_rate':  self.read_misses / self.read_accesses if self.read_accesses else 0.0,
            'write_accesses':  self.write_accesses,
            'write_misses':    self.write_misses,
            'write_miss_rate': self.write_misses / self.write_accesses if self.write_accesses else 0.0,
            'total_accesses':  total,
            'total_misses':    total_misses,
            'total_miss_rate': total_misses / total if total else 0.0,
            'evictions':       self.evictions,
        }


def run_trace(trace_file: str, cache_size: int, associativity: int, block_size: int) -> dict:
    sim = CacheSimulator(cache_size, associativity, block_size)
    with open(trace_file) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            access_type = int(parts[0])
            if access_type == 2:
                continue
            address = int(parts[1], 16)
            sim.access(address, is_write=(access_type == 1))
    return sim.stats()


def print_stats(stats: dict, cache_size: int, associativity: int,
                block_size: int, trace_file: str) -> None:
    num_sets = cache_size // (associativity * block_size)
    sep = '=' * 62
    print(f'\n{sep}')
    print(f'  Cache Simulator A')
    print(sep)
    print(f'  Trace file    : {trace_file}')
    print(f'  Cache size    : {cache_size // 1024} KB  ({cache_size} B)')
    print(f'  Block size    : {block_size} B')
    print(f'  Associativity : {associativity}-way')
    print(f'  Sets          : {num_sets}')
    print(f'  Replace policy: LRU   |  Write policy: write-allocate')
    print(sep)
    s = stats
    print(f'  Read accesses : {s["read_accesses"]:>12,}')
    print(f'  Read misses   : {s["read_misses"]:>12,}  ({s["read_miss_rate"]*100:6.2f}%)')
    print(f'  Write accesses: {s["write_accesses"]:>12,}')
    print(f'  Write misses  : {s["write_misses"]:>12,}  ({s["write_miss_rate"]*100:6.2f}%)')
    print(f'  Total accesses: {s["total_accesses"]:>12,}')
    print(f'  Total misses  : {s["total_misses"]:>12,}  ({s["total_miss_rate"]*100:6.2f}%)')
    print(f'  Evictions     : {s["evictions"]:>12,}')
    print(sep)


def batch_run(trace_file: str) -> None:
    cache_sizes = [8192, 16384, 32768, 65536]
    assocs      = [1, 2, 4, 8]
    block_sizes = [16, 32, 64, 128]
    hdr = (f'{"KB":>4} {"W":>2} {"B":>4} | '
           f'{"Rd_acc":>9} {"Rd_miss":>8} {"Rd%":>6} | '
           f'{"Wr_acc":>9} {"Wr_miss":>8} {"Wr%":>6} | '
           f'{"Tot%":>6} {"Evict":>9}')
    print(f'\nBatch: {trace_file}')
    print(hdr)
    print('-' * len(hdr))
    for cs in cache_sizes:
        for assoc in assocs:
            for bs in block_sizes:
                if cs % (assoc * bs) != 0:
                    continue
                s = run_trace(trace_file, cs, assoc, bs)
                print(f'{cs//1024:>4} {assoc:>2} {bs:>4} | '
                      f'{s["read_accesses"]:>9,} {s["read_misses"]:>8,} {s["read_miss_rate"]*100:>5.2f}% | '
                      f'{s["write_accesses"]:>9,} {s["write_misses"]:>8,} {s["write_miss_rate"]*100:>5.2f}% | '
                      f'{s["total_miss_rate"]*100:>5.2f}% {s["evictions"]:>9,}')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Cache Simulator A  (LRU + write-allocate)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  %(prog)s trace.din -s 16384 -a 2 -b 32\n'
            '  %(prog)s trace.din --batch'
        ),
    )
    parser.add_argument('trace_input_file', help='Path to trace file (.din)')
    parser.add_argument('-s', '--cache-size', type=int, default=16384,
                        choices=[8192, 16384, 32768, 65536], metavar='BYTES',
                        help='Cache size in bytes (default: 16384)')
    parser.add_argument('-a', '--associativity', type=int, default=2,
                        choices=[1, 2, 4, 8],
                        help='N-way associativity (default: 2)')
    parser.add_argument('-b', '--block-size', type=int, default=32,
                        choices=[16, 32, 64, 128],
                        help='Block size in bytes (default: 32)')
    parser.add_argument('--batch', action='store_true',
                        help='Sweep all parameter combos and print table')
    args = parser.parse_args()
    if args.batch:
        batch_run(args.trace_input_file)
    else:
        stats = run_trace(args.trace_input_file, args.cache_size,
                          args.associativity, args.block_size)
        print_stats(stats, args.cache_size, args.associativity,
                    args.block_size, args.trace_input_file)


if __name__ == '__main__':
    main()
