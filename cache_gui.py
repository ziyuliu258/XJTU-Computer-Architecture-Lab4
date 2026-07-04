#!/usr/bin/env python3
"""
Cache Simulator A - Graphical Interface
Lab 4: Cache Performance Analysis
Run: uv run python cache_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import OrderedDict
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# ─── Core Simulation Logic ────────────────────────────────────────────────────

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
        self.cache_size    = cache_size
        self.associativity = associativity
        self.block_size    = block_size
        self.num_sets      = cache_size // (associativity * block_size)
        self._sets         = [CacheSet(associativity) for _ in range(self.num_sets)]
        self.read_accesses = self.read_misses = 0
        self.write_accesses = self.write_misses = self.evictions = 0

    def _decode(self, addr: int) -> tuple[int, int]:
        ob = (self.block_size - 1).bit_length()
        ib = (self.num_sets - 1).bit_length() if self.num_sets > 1 else 0
        return (addr >> ob) & (self.num_sets - 1), addr >> (ob + ib)

    def access(self, address: int, is_write: bool) -> None:
        si, tag = self._decode(address)
        hit, evicted = self._sets[si].access(tag, is_write)
        if is_write:
            self.write_accesses += 1
            if not hit: self.write_misses += 1
        else:
            self.read_accesses += 1
            if not hit: self.read_misses += 1
        if evicted: self.evictions += 1

    def stats(self) -> dict:
        total = self.read_accesses + self.write_accesses
        tm    = self.read_misses   + self.write_misses
        return {
            'read_accesses':   self.read_accesses,
            'read_misses':     self.read_misses,
            'read_miss_rate':  self.read_misses / self.read_accesses if self.read_accesses else 0,
            'write_accesses':  self.write_accesses,
            'write_misses':    self.write_misses,
            'write_miss_rate': self.write_misses / self.write_accesses if self.write_accesses else 0,
            'total_accesses':  total,
            'total_misses':    tm,
            'total_miss_rate': tm / total if total else 0,
            'evictions':       self.evictions,
        }


def run_trace(trace_file: str, cache_size: int, associativity: int, block_size: int) -> dict:
    sim = CacheSimulator(cache_size, associativity, block_size)
    with open(trace_file) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2: continue
            at = int(parts[0])
            if at == 2: continue
            sim.access(int(parts[1], 16), is_write=(at == 1))
    return sim.stats()


# ─── GUI ─────────────────────────────────────────────────────────────────────

CACHE_SIZES  = [8192, 16384, 32768, 65536]
ASSOCS       = [1, 2, 4, 8]
BLOCK_SIZES  = [16, 32, 64, 128]
SIZE_LABELS  = ["8 KB", "16 KB", "32 KB", "64 KB"]
ASSOC_LABELS = ["1-way", "2-way", "4-way", "8-way"]
BLOCK_LABELS = ["16 B", "32 B", "64 B", "128 B"]


class CacheSimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cache Simulator A  —  Lab 4")
        self.geometry("1100x720")
        self.resizable(True, True)
        self._trace_path = tk.StringVar()
        self._cache_size = tk.StringVar(value="16 KB")
        self._assoc      = tk.StringVar(value="2-way")
        self._block_size = tk.StringVar(value="32 B")
        self._build_ui()

    # ── Build layout ──────────────────────────────────────────────────────────
    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left config panel ──
        left = ttk.Frame(self, padding=12, relief="ridge")
        left.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)

        ttk.Label(left, text="Cache Simulator A", font=("", 13, "bold")).pack(pady=(0, 10))

        # Trace file
        ttk.Label(left, text="Trace file").pack(anchor="w")
        tf_frame = ttk.Frame(left)
        tf_frame.pack(fill="x", pady=(2, 8))
        ttk.Entry(tf_frame, textvariable=self._trace_path, width=28).pack(side="left", fill="x", expand=True)
        ttk.Button(tf_frame, text="…", width=3, command=self._browse).pack(side="left", padx=(4, 0))

        # Parameters
        for label, var, opts in [
            ("Cache size",    self._cache_size, SIZE_LABELS),
            ("Associativity", self._assoc,      ASSOC_LABELS),
            ("Block size",    self._block_size, BLOCK_LABELS),
        ]:
            ttk.Label(left, text=label).pack(anchor="w")
            ttk.Combobox(left, textvariable=var, values=opts, state="readonly", width=12).pack(anchor="w", pady=(2, 8))

        ttk.Separator(left).pack(fill="x", pady=6)

        # Info label: LRU + write-allocate
        info = ttk.Label(left, text="Policy: LRU + write-allocate",
                         foreground="gray", font=("", 9))
        info.pack(anchor="w", pady=(0, 10))

        # Buttons
        ttk.Button(left, text="Run Simulation",  command=self._run_single).pack(fill="x", pady=3)
        ttk.Button(left, text="Sweep All Params", command=self._run_sweep).pack(fill="x", pady=3)

        # Progress label
        self._status = ttk.Label(left, text="", foreground="blue")
        self._status.pack(pady=(8, 0))

        # ── Right results panel ──
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._notebook = ttk.Notebook(right)
        self._notebook.grid(row=0, column=0, sticky="nsew")

        # Tab 1: Statistics text
        tab_stats = ttk.Frame(self._notebook)
        self._notebook.add(tab_stats, text="Statistics")
        self._stats_text = tk.Text(tab_stats, font=("Courier", 10), state="disabled",
                                   wrap="none", bg="#f8f8f8")
        sb = ttk.Scrollbar(tab_stats, command=self._stats_text.yview)
        self._stats_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._stats_text.pack(fill="both", expand=True)

        # Tabs 2-4: Charts
        self._fig_size  = self._make_chart_tab("Cache Size Effect")
        self._fig_assoc = self._make_chart_tab("Associativity Effect")
        self._fig_block = self._make_chart_tab("Block Size Effect")

    def _make_chart_tab(self, title: str):
        tab = ttk.Frame(self._notebook)
        self._notebook.add(tab, text=title)
        fig = Figure(figsize=(7, 4.5), dpi=96, tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        fig._canvas_ref = canvas
        return fig

    # ── Actions ───────────────────────────────────────────────────────────────
    def _browse(self):
        p = filedialog.askopenfilename(
            title="Select trace file",
            filetypes=[("DIN trace files", "*.din"), ("All files", "*.*")])
        if p:
            self._trace_path.set(p)

    def _parse_params(self) -> tuple[str, int, int, int] | None:
        path = self._trace_path.get().strip()
        if not path:
            messagebox.showwarning("No trace file", "Please select a trace file first.")
            return None
        cs = CACHE_SIZES[SIZE_LABELS.index(self._cache_size.get())]
        wa = ASSOCS[ASSOC_LABELS.index(self._assoc.get())]
        bs = BLOCK_SIZES[BLOCK_LABELS.index(self._block_size.get())]
        return path, cs, wa, bs

    def _set_status(self, msg: str):
        self._status.config(text=msg)
        self.update_idletasks()

    def _run_single(self):
        params = self._parse_params()
        if not params: return
        path, cs, wa, bs = params
        self._set_status("Running…")
        try:
            s = run_trace(path, cs, wa, bs)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._set_status("Error")
            return
        self._show_stats(s, cs, wa, bs, path)
        self._set_status("Done.")
        self._notebook.select(0)

    def _run_sweep(self):
        params = self._parse_params()
        if not params: return
        path, _, _, _ = params
        self._set_status("Sweeping parameters…")
        try:
            self._do_sweep(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._set_status("Error")
            return
        self._set_status("Sweep complete.")
        self._notebook.select(1)

    # ── Output helpers ────────────────────────────────────────────────────────
    def _show_stats(self, s: dict, cs: int, wa: int, bs: int, path: str):
        ns = cs // (wa * bs)
        lines = [
            f"{'='*54}",
            f"  Cache Simulator A",
            f"{'='*54}",
            f"  Trace         : {path}",
            f"  Cache size    : {cs//1024} KB",
            f"  Block size    : {bs} B",
            f"  Associativity : {wa}-way",
            f"  Sets          : {ns}",
            f"  Policy        : LRU + write-allocate",
            f"{'='*54}",
            f"  Read  accesses: {s['read_accesses']:>12,}",
            f"  Read  misses  : {s['read_misses']:>12,}  ({s['read_miss_rate']*100:5.2f}%)",
            f"  Write accesses: {s['write_accesses']:>12,}",
            f"  Write misses  : {s['write_misses']:>12,}  ({s['write_miss_rate']*100:5.2f}%)",
            f"  Total accesses: {s['total_accesses']:>12,}",
            f"  Total misses  : {s['total_misses']:>12,}  ({s['total_miss_rate']*100:5.2f}%)",
            f"  Evictions     : {s['evictions']:>12,}",
            f"{'='*54}",
        ]
        self._stats_text.config(state="normal")
        self._stats_text.delete("1.0", "end")
        self._stats_text.insert("end", "\n".join(lines))
        self._stats_text.config(state="disabled")

    # ── Sweep + chart rendering ───────────────────────────────────────────────
    def _do_sweep(self, path: str):
        # Effect of cache size: fix 2-way, 32B
        cs_rates = []
        for cs in CACHE_SIZES:
            s = run_trace(path, cs, 2, 32)
            cs_rates.append((s['read_miss_rate']*100, s['write_miss_rate']*100, s['total_miss_rate']*100))

        # Effect of associativity: fix 16KB, 32B
        assoc_rates = []
        for wa in ASSOCS:
            s = run_trace(path, 16384, wa, 32)
            assoc_rates.append((s['read_miss_rate']*100, s['write_miss_rate']*100, s['total_miss_rate']*100))

        # Effect of block size: fix 16KB, 2-way
        bs_rates = []
        for bs in BLOCK_SIZES:
            s = run_trace(path, 16384, 2, bs)
            bs_rates.append((s['read_miss_rate']*100, s['write_miss_rate']*100, s['total_miss_rate']*100))

        # Build sweep summary text
        self._show_sweep_text(path, cs_rates, assoc_rates, bs_rates)

        # Draw charts
        self._draw_chart(self._fig_size,  SIZE_LABELS,  cs_rates,
                         "Miss Rate vs Cache Size\n(2-way, 32B block)")
        self._draw_chart(self._fig_assoc, ASSOC_LABELS, assoc_rates,
                         "Miss Rate vs Associativity\n(16KB, 32B block)")
        self._draw_chart(self._fig_block, BLOCK_LABELS, bs_rates,
                         "Miss Rate vs Block Size\n(16KB, 2-way)")

    def _show_sweep_text(self, path, cs_rates, assoc_rates, bs_rates):
        def table(header, labels, rates):
            rows = [header,
                    f"  {'Param':<10} {'Read%':>7} {'Write%':>8} {'Total%':>8}",
                    "  " + "-"*35]
            for lbl, (r, w, t) in zip(labels, rates):
                rows.append(f"  {lbl:<10} {r:>6.2f}%  {w:>6.2f}%  {t:>6.2f}%")
            return "\n".join(rows)

        text = "\n".join([
            f"Sweep results for: {path}",
            "",
            table("Cache Size Effect (2-way, 32B block):", SIZE_LABELS,  cs_rates),
            "",
            table("Associativity Effect (16KB, 32B block):", ASSOC_LABELS, assoc_rates),
            "",
            table("Block Size Effect (16KB, 2-way):", BLOCK_LABELS, bs_rates),
        ])
        self._stats_text.config(state="normal")
        self._stats_text.delete("1.0", "end")
        self._stats_text.insert("end", text)
        self._stats_text.config(state="disabled")

    def _draw_chart(self, fig: Figure, labels: list, rates: list, title: str):
        fig.clear()
        ax = fig.add_subplot(111)
        x  = range(len(labels))
        w  = 0.26
        rd = [r[0] for r in rates]
        wr = [r[1] for r in rates]
        tot= [r[2] for r in rates]

        b1 = ax.bar([i - w for i in x], rd,  w, label="Read miss%",  color="#4e8ef7")
        b2 = ax.bar(x,                  wr,  w, label="Write miss%", color="#f7934e")
        b3 = ax.bar([i + w for i in x], tot, w, label="Total miss%", color="#4ec96a")

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylabel("Miss Rate (%)")
        ax.set_title(title, fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bars in (b1, b2, b3):
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.annotate(f"{h:.2f}",
                                xy=(bar.get_x() + bar.get_width()/2, h),
                                xytext=(0, 2), textcoords="offset points",
                                ha="center", va="bottom", fontsize=7)

        fig._canvas_ref.draw()


def main():
    app = CacheSimApp()
    app.mainloop()


if __name__ == "__main__":
    main()
