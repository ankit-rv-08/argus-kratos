# Argus-Kratos: Autonomous Financial Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Apple Metal](https://img.shields.io/badge/Hardware_Accel-Apple_Metal_(MPS)-silver?logo=apple&logoColor=white)](https://developer.apple.com/metal/)
[![Model](https://img.shields.io/badge/Model-Llama--3.2--1B--Instruct-purple?logo=meta)](https://huggingface.co/meta-llama)
[![Quantization](https://img.shields.io/badge/Quantization-Q4__K__M_GGUF-brightgreen)](https://github.com/ggerganov/llama.cpp)
[![Weights & Biases](https://img.shields.io/badge/MLOps-Weights_&_Biases-orange?logo=weightsandbiases&logoColor=white)](https://wandb.ai/ankith8804-sforger/huggingface)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Argus-Kratos is a hybrid, edge-accelerated financial intelligence platform. It couples an autonomous research orchestrator (**Argus**) with a domain-specialized, fine-tuned Small Language Model (**Kratos**) running on Apple Silicon unified memory.

Financial analysis requires zero tolerance for mathematical hallucinations, while market sentiment extraction demands nuanced language understanding. Argus-Kratos resolves this duality by decoupling arithmetic and data ingestion into an isolated **AST (Abstract Syntax Tree)** execution sandbox while offloading risk vector classification to an on-device, 4-bit quantized edge SLM.

---

## System Architecture

```mermaid
flowchart TD
    User([User / Browser]) <-->|HTTP / Real-Time JSON| UI[Argus Glassmorphic UI<br/>Split-Screen Observability]
    UI <-->|REST API /api/dossier?ticker=XYZ| Backend[Argus Core Orchestrator<br/>app.py]

    subgraph Deterministic_Pipeline [Deterministic Math & Ingestion Engine]
        Backend -->|Ticker Ingestion| Ingestion[tools.py<br/>Balance Sheets & Filings]
        Ingestion -->|Sanitized Math AST| AST[calculator.py<br/>Isolated AST Parser]
        AST -->|Derived Ratios| Synthesis[Capital Matrix & Ratio Synthesis]
    end

    subgraph Edge_ML_Runtime [Edge SLM Inference Engine]
        Backend -->|Live News Extraction| News[Market Headlines Feed]
        News -->|Batched Context Prompts| Kratos[tools.py / inference.py]
        Kratos -->|Metal Performance Shaders| Metal[(Apple Silicon Unified Memory<br/>Llama-3.2-1B Q4_K_M GGUF)]
        Metal -->|Sub-1.5s Token Classification| Sentiment[Bullish / Bearish / Neutral Risk Vectors]
    end

    Synthesis --> Aggregator[Dossier Compiler]
    Sentiment --> Aggregator
    Aggregator -->|Synthesized Intelligence| UI
```

---

## Key Engineering Highlights

### 1. On-Device Edge ML Inference (Kratos Engine)
* **Fine-Tuning:** Adapted `Llama-3.2-1B-Instruct` on financial market sentiment corpora using Unsloth LoRA adapters, driving cross-entropy loss down from **4.69** to **1.01**.
* **4-bit Quantization:** Merged adapters and quantized into a compact **Q4_K_M GGUF** binary (~800 MB footprint).
* **Apple Silicon Metal Acceleration:** Executes locally via `llama-cpp-python` with Apple Metal Performance Shaders (`GGML_METAL=on`). Operates at **~45.2 tokens/sec** with zero external API calls or cloud token overhead.

### 2. Hallucination-Proof Financial Mathematics (Argus Core)
* LLMs routinely generate inaccurate calculations when evaluating complex financial statements.
* All financial health ratios (Debt-to-Equity, Net Margin, ROE/ROIC) are parsed through an isolated **Abstract Syntax Tree (AST) evaluator** (`calculator.py`) without invoking unsafe Python `eval()`.

### 3. Dynamic Multi-Ticker Pipeline
* Supports real-time query resolution across global equities (e.g., `NVDA`, `AAPL`, `TSLA`, `MSFT`, `COIN`).
* Automatically retrieves real-time pricing, balance sheet assets/debt, and trailing news items, routing text through the edge SLM for real-time risk vector assessment.

### 4. Split-Screen Observability Interface
* Built with an obsidian/glassmorphic interface (`#090a0f` base, backdrop-blur translucent surfaces, tabular-numeral typography).
* **Left Pane (Agent Trace):** Live observability into orchestrator thought steps, tool execution, and inference latency.
* **Right Pane (Executive Dossier):** Structured capital structure matrix, derived financial ratios, and color-coded risk vectors.

---

## Hardware Telemetry & Benchmarks

Benchmarked locally on Apple Silicon unified memory:

| Metric | Target / Measurement | Technical Notes |
| :--- | :--- | :--- |
| **Base Architecture** | `Llama-3.2-1B-Instruct` | LoRA target modules: `q, k, v, o, gate, up, down` |
| **Precision / Format** | 4-bit `Q4_K_M` GGUF | Medium 4-bit quantization via Unsloth/llama.cpp |
| **Unified Memory Footprint** | ~1.84 GB | Peak allocation during 2048-token context window |
| **Inference Speed** | **45.2 tok/s** | Metal Performance Shaders (MPS) |
| **Inference Latency** | **1.50 s** | Average completion latency per evaluation |
| **API Cost per Query** | **$0.00** | 100% offline, privacy-preserving execution |

---

## Repository Structure

```text
argus-kratos/
├── app.py                 # Core Flask backend & API routing (/api/dossier)
├── tools.py               # Dynamic ticker ingestion & Kratos inference bridge
├── calculator.py          # Sandboxed AST-based mathematical evaluation
├── inference.py           # Standalone local Apple Metal inference runner
├── kratos_cli.py          # Rich terminal-based edge inference & telemetry
├── unsloth.Q4_K_M.gguf    # 4-bit fine-tuned local weights (Apple Metal)
├── web/
│   ├── index.html         # Split-screen financial intelligence workspace
│   ├── styles.css         # Glassmorphic obsidian styling & layout
│   └── app.js             # Reactive client engine & real-time search
├── requirements.txt       # Production dependencies
└── README.md
```

---

## Quickstart Guide

### Prerequisites
* macOS with Apple Silicon (M1/M2/M3/M4) for native Metal acceleration.
* Python 3.10 or 3.11.

### 1. Clone & Setup Environment
```bash
git clone [https://github.com/ankit-rv-08/argus-kratos.git](https://github.com/ankit-rv-08/argus-kratos.git)
cd argus-kratos

python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies with Metal Support
```bash
# Install llama-cpp-python compiled with Apple Metal support
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python

# Install application dependencies
pip install -r requirements.txt
```

### 3. Model Weights
Place your quantized weights (`unsloth.Q4_K_M.gguf`) in the repository root directory.

### 4. Launch the Web Interface
```bash
python app.py
```
Open **`http://127.0.0.1:8080`** in your browser. Enter any ticker symbol (e.g., `AAPL`, `NVDA`, `TSLA`) in the search bar to run dynamic analysis.

### 5. Run the Terminal Telemetry CLI
In a separate terminal window:
```bash
source venv/bin/activate
python kratos_cli.py
```

---

## Training Provenance & MLOps

* **Dataset:** Financial news sentiment corpus (`zeroshot/twitter-financial-news-sentiment`, Parquet-backed).
* **Supervised Fine-Tuning:** Executed via Unsloth on an NVIDIA Tesla T4 using 4-bit QLoRA optimizations.
* **Telemetry & Tracking:** Experiment telemetry, learning rate schedules, and gradient updates tracked live via [Weights & Biases](https://wandb.ai/ankith8804-sforger/huggingface).

---

## Roadmap

- [x] Phase 1: LoRA fine-tuning, 4-bit quantization, and local Apple Metal MPS runtime.
- [x] Phase 2: AST calculator sandboxing, dynamic ticker ingestion, and glassmorphic UI.
- [ ] Phase 3: ChromaDB vector store integration for semantic search over SEC 10-K/10-Q filings.
- [ ] Phase 4: Parallelized asynchronous batch processing for multi-ticker comparative intelligence.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.