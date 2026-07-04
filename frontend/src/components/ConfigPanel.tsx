import type { CacheConfig } from "../types";

interface Props {
  config: CacheConfig;
  onChange: (c: CacheConfig) => void;
}

const SIZES  = [8192, 16384, 32768, 65536];
const ASSOCS = [1, 2, 4, 8];
const BLOCKS = [16, 32, 64, 128];

export default function ConfigPanel({ config, onChange }: Props) {
  const upd = (k: keyof CacheConfig, v: number) =>
    onChange({ ...config, [k]: v });

  return (
    <div className="panel">
      <div className="panel-head">
        <span className="panel-title">Cache 参数</span>
      </div>
      <div className="config-grid">
        <div className="config-field">
          <label>Cache 大小</label>
          <select
            value={config.cache_size}
            onChange={(e) => upd("cache_size", Number(e.target.value))}
          >
            {SIZES.map((s) => (
              <option key={s} value={s}>{s / 1024} KB</option>
            ))}
          </select>
        </div>

        <div className="config-field">
          <label>相联度</label>
          <select
            value={config.associativity}
            onChange={(e) => upd("associativity", Number(e.target.value))}
          >
            {ASSOCS.map((a) => (
              <option key={a} value={a}>{a}-way</option>
            ))}
          </select>
        </div>

        <div className="config-field">
          <label>块大小</label>
          <select
            value={config.block_size}
            onChange={(e) => upd("block_size", Number(e.target.value))}
          >
            {BLOCKS.map((b) => (
              <option key={b} value={b}>{b} B</option>
            ))}
          </select>
        </div>

        <div className="config-field">
          <label>替换策略</label>
          <select disabled>
            <option>LRU</option>
          </select>
        </div>
      </div>
    </div>
  );
}
