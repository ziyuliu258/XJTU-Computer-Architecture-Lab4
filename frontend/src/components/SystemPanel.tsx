import type { CacheStats } from "../types";

interface Props {
  stats: CacheStats | null;
}

function fmt(n: number): string {
  return n.toLocaleString();
}

function pct(r: number): string {
  return `${(r * 100).toFixed(2)}%`;
}

export default function SystemPanel({ stats }: Props) {
  return (
    <div className="panel">
      <div className="panel-head">
        <span className="panel-title">统计详情</span>
      </div>
      {stats === null ? (
        <p className="empty-text">运行模拟后显示统计数据。</p>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-chip">
              <span>总访问次数</span>
              <strong>{fmt(stats.total_accesses)}</strong>
            </div>
            <div className="stat-chip stat-warn">
              <span>总缺失次数</span>
              <strong>{fmt(stats.total_misses)}</strong>
            </div>
            <div className="stat-chip">
              <span>读访问</span>
              <strong>{fmt(stats.read_accesses)}</strong>
            </div>
            <div className="stat-chip stat-warn">
              <span>读缺失率</span>
              <strong>{pct(stats.read_miss_rate)}</strong>
            </div>
            <div className="stat-chip">
              <span>写访问</span>
              <strong>{fmt(stats.write_accesses)}</strong>
            </div>
            <div className="stat-chip stat-warn">
              <span>写缺失率</span>
              <strong>{pct(stats.write_miss_rate)}</strong>
            </div>
            <div className="stat-chip">
              <span>驱逐次数</span>
              <strong>{fmt(stats.evictions)}</strong>
            </div>
            <div className="stat-chip stat-warn">
              <span>总缺失率</span>
              <strong>{pct(stats.total_miss_rate)}</strong>
            </div>
          </div>

          <p className="section-sub" style={{ marginTop: 14 }}>读 / 写 明细</p>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>访问次数</th>
                  <th>缺失次数</th>
                  <th>缺失率</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="cell-label">读</td>
                  <td>{fmt(stats.read_accesses)}</td>
                  <td>{fmt(stats.read_misses)}</td>
                  <td>{pct(stats.read_miss_rate)}</td>
                </tr>
                <tr>
                  <td className="cell-label">写</td>
                  <td>{fmt(stats.write_accesses)}</td>
                  <td>{fmt(stats.write_misses)}</td>
                  <td>{pct(stats.write_miss_rate)}</td>
                </tr>
                <tr style={{ fontWeight: 700 }}>
                  <td className="cell-label">合计</td>
                  <td>{fmt(stats.total_accesses)}</td>
                  <td>{fmt(stats.total_misses)}</td>
                  <td>{pct(stats.total_miss_rate)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
