import { useRef } from "react";
import type { SampleTrace } from "../types";

interface Props {
  value: string;
  samples: SampleTrace[];
  onChange: (v: string) => void;
}

const PLACEHOLDER = `# 粘贴 trace 内容，或点击右上方加载示例 / 上传文件
0 7ffebc64 0
1 100039b8 0
2 400190 8fa40000`;

export default function TracePanel({ value, samples, onChange }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => onChange((ev.target?.result as string) ?? "");
    reader.readAsText(file);
    e.target.value = "";
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <span className="panel-title">Trace 输入</span>
        <button className="btn btn-ghost btn-sm" onClick={() => fileRef.current?.click()}>
          上传文件
        </button>
        <input ref={fileRef} type="file" accept=".din,.txt" hidden onChange={handleFile} />
      </div>

      {samples.length > 0 && (
        <div className="trace-actions">
          {samples.map((s) => (
            <button
              key={s.name}
              className="btn btn-ghost btn-sm"
              onClick={() => onChange(s.data)}
              title={s.name}
            >
              {s.title}
            </button>
          ))}
        </div>
      )}

      <textarea
        className="trace-textarea"
        placeholder={PLACEHOLDER}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
        style={{ marginTop: samples.length > 0 ? 8 : 0 }}
      />
    </div>
  );
}
