import { useEffect, useState } from "react";
import { fetchSamples, simulate } from "./api/client";
import ConfigPanel from "./components/ConfigPanel";
import MissRateChart from "./components/MissRateChart";
import SystemPanel from "./components/SystemPanel";
import TracePanel from "./components/TracePanel";
import type { CacheConfig, SampleTrace, SimulateResponse } from "./types";

const DEFAULT_CONFIG: CacheConfig = { cache_size: 16384, associativity: 2, block_size: 32 };

export default function App() {
  const [samples, setSamples] = useState<SampleTrace[]>([]);
  const [trace, setTrace]     = useState("");
  const [config, setConfig]   = useState<CacheConfig>(DEFAULT_CONFIG);
  const [result, setResult]   = useState<SimulateResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    fetchSamples().then(setSamples).catch(() => undefined);
  }, []);

  async function run() {
    if (!trace.trim()) { setError("请先粘贴或上传 trace 文件内容。"); return; }
    setRunning(true); setError(null);
    try {
      setResult(await simulate(trace, config));
    } catch (e) {
      setError(e instanceof Error ? e.message : "模拟失败");
    } finally {
      setRunning(false);
    }
  }

  const stats = result?.stats ?? null;

  return (
    <div className="app-shell">
      <header className="hero-bar">
        <div className="hero-copy-block">
          <p className="eyebrow">计算机体系结构实验四</p>
          <h1>Simulator A · Cache</h1>
          <p className="hero-copy">N 路组相联 Cache 性能分析模拟器 · LRU 替换 · 写分配策略</p>
        </div>
        <div className="hero-status">
          <div className="hero-stat">
            <span className="hero-stat-label">总访问</span>
            <span className="hero-stat-value">{stats ? stats.total_accesses.toLocaleString() : "–"}</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">总缺失率</span>
            <span className="hero-stat-value">
              {stats ? `${(stats.total_miss_rate * 100).toFixed(2)}%` : "–"}
            </span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">驱逐次数</span>
            <span className="hero-stat-value">{stats ? stats.evictions.toLocaleString() : "–"}</span>
          </div>
        </div>
      </header>

      <main className="workspace-layout">
        <section className="workspace-grid">
          <section className="workspace-input">
            <TracePanel value={trace} samples={samples} onChange={setTrace} />
            <ConfigPanel config={config} onChange={setConfig} />
            <div className="panel">
              {error && <p className="error-banner">{error}</p>}
              <div className="control-bar">
                <button className="btn btn-primary" onClick={run} disabled={running}>
                  {running ? "运行中…" : "运行模拟"}
                </button>
                <button className="btn btn-ghost" onClick={() => { setResult(null); setError(null); }}>
                  重置
                </button>
              </div>
            </div>
          </section>

          <section className="workspace-main">
            <MissRateChart
              bySize={result?.sweep_by_size ?? []}
              byAssoc={result?.sweep_by_assoc ?? []}
              byBlock={result?.sweep_by_block ?? []}
            />
          </section>

          <section className="workspace-side">
            <SystemPanel stats={stats} />
          </section>
        </section>
      </main>
    </div>
  );
}
