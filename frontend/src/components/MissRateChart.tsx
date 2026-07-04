import { useState } from "react";
import type { SweepPoint } from "../types";

interface ChartProps {
  points: SweepPoint[];
  title: string;
}

function BarGroup({ points, title }: ChartProps) {
  const max = Math.max(...points.map((p) => p.total_miss_rate), 1);
  return (
    <div className="chart-section">
      <p className="chart-title">{title}</p>
      <div className="chart-bars">
        {points.map((p) => (
          <div key={p.label}>
            <div className="bar-row">
              <span className="bar-label">{p.label}</span>
              <div className="bar-track">
                <div className="bar-fill read" style={{ width: `${(p.read_miss_rate / max) * 100}%` }} />
              </div>
              <span className="bar-value">{p.read_miss_rate.toFixed(2)}%</span>
            </div>
            <div className="bar-row">
              <span className="bar-label" />
              <div className="bar-track">
                <div className="bar-fill write" style={{ width: `${(p.write_miss_rate / max) * 100}%` }} />
              </div>
              <span className="bar-value">{p.write_miss_rate.toFixed(2)}%</span>
            </div>
            <div className="bar-row">
              <span className="bar-label" />
              <div className="bar-track">
                <div className="bar-fill total" style={{ width: `${(p.total_miss_rate / max) * 100}%` }} />
              </div>
              <span className="bar-value">{p.total_miss_rate.toFixed(2)}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="chart-legend">
        <div className="legend-item"><span className="legend-dot" style={{ background: "var(--teal)" }} />读缺失率</div>
        <div className="legend-item"><span className="legend-dot" style={{ background: "var(--amber)" }} />写缺失率</div>
        <div className="legend-item"><span className="legend-dot" style={{ background: "var(--vermilion)" }} />总缺失率</div>
      </div>
    </div>
  );
}

interface Props {
  bySize: SweepPoint[];
  byAssoc: SweepPoint[];
  byBlock: SweepPoint[];
}

const TABS = [
  { key: "size",  label: "Cache 大小" },
  { key: "assoc", label: "相联度" },
  { key: "block", label: "块大小" },
] as const;

export default function MissRateChart({ bySize, byAssoc, byBlock }: Props) {
  const [tab, setTab] = useState<"size" | "assoc" | "block">("size");

  const data: Record<string, SweepPoint[]> = { size: bySize, assoc: byAssoc, block: byBlock };
  const titleMap: Record<string, string> = {
    size:  "不同 Cache 大小的缺失率（2-way，32 B）",
    assoc: "不同相联度的缺失率（16 KB，32 B）",
    block: "不同块大小的缺失率（16 KB，2-way）",
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <span className="panel-title">缺失率分析</span>
      </div>
      <div className="chart-tabs">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            className={`chart-tab${tab === key ? " active" : ""}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {data[tab].length > 0 ? (
        <BarGroup points={data[tab]} title={titleMap[tab]} />
      ) : (
        <p className="empty-text">运行模拟后显示图表。</p>
      )}
    </div>
  );
}
