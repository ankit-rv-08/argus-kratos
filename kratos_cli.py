"""Kratos edge inference terminal presentation."""

from __future__ import annotations

import json
import time
from pathlib import Path

from inference import MODEL_PATH, analyze_context, load_model
from tools import build_dossier

try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover
    Console = None


def run() -> None:
    dossier = build_dossier()
    if Console is None:
        print("Install dependencies with: pip install -r requirements.txt")
        print(json.dumps(dossier, indent=2))
        return
    console = Console()
    console.print(Panel("[bold white]KRATOS[/] [dim]edge inference runtime v1.0.0[/]\n[dim]target: apple-metal (MPS) | quant: q4_k_m[/]", border_style="cyan"))
    if not Path(MODEL_PATH).is_file():
        console.print("[bold red]ERROR[/] model not found: " + str(MODEL_PATH))
        return
    started = time.perf_counter()
    model = load_model()
    load_time = time.perf_counter() - started
    console.print(f"[green]OK[/] Model mapped to unified memory in {load_time:.2f}s  [dim]{MODEL_PATH.name}[/]\n")
    console.print("[bold yellow]TOKEN STREAM (LOCAL GPU)[/]")
    output = analyze_context("NVIDIA data center revenue hit records, but new export restrictions threaten APAC growth.")
    rendered = json.dumps({key: output[key] for key in ("ticker", "sentiment", "risk_factor")})
    with Live(console=console, refresh_per_second=24) as live:
        current = ""
        for character in rendered:
            current += character
            live.update(f"[bright_white]{current}[/]")
            time.sleep(0.004)
    console.print("\n")
    tokens = output.get("tokens", 0)
    elapsed = output.get("elapsed", 0.0)
    speed = tokens / elapsed if elapsed else 0
    table = Table(title="HARDWARE TELEMETRY", title_style="bold #c5ff67", border_style="#364253")
    table.add_column("metric", style="dim")
    table.add_column("value", justify="right", style="bright_white")
    table.add_row("tokens generated", str(tokens))
    table.add_row("inference speed", f"{speed:.1f} tok/s")
    table.add_row("inference latency", f"{elapsed:.2f} s")
    table.add_row("compute hardware", "Apple Metal Performance Shaders")
    table.add_row("API cost", "$0.00 (Offline)")
    console.print(table)


if __name__ == "__main__":
    run()
