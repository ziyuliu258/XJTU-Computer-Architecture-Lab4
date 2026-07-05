export interface CacheConfig {
  cache_size: number;
  associativity: number;
  block_size: number;
}

export interface SampleTrace {
  name: string;
  title: string;
  data: string;
}

export interface CacheStats {
  read_accesses: number;
  read_misses: number;
  read_miss_rate: number;
  write_accesses: number;
  write_misses: number;
  write_miss_rate: number;
  total_accesses: number;
  total_misses: number;
  total_miss_rate: number;
  evictions: number;
}

export interface SweepPoint {
  label: string;
  read_miss_rate: number;
  write_miss_rate: number;
  total_miss_rate: number;
}

export interface SimulateResponse {
  stats: CacheStats;
  sweep_by_size: SweepPoint[];
  sweep_by_assoc: SweepPoint[];
  sweep_by_block: SweepPoint[];
}
