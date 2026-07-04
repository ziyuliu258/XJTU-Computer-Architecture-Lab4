import { useRef } from "react";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

const PLACEHOLDER = `# Paste trace content here, e.g.:
0 7ffebc64 0
1 100039b8 0
2 400190 8fa40000`;

export default function TracePanel({ value, onChange }: Props) {
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
      <textarea
        className="trace-textarea"
        placeholder={PLACEHOLDER}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
      />
    </div>
  );
}
