# Adaptive Image Improvement

An autonomous image refinement loop that iteratively improves generated images by adjusting prompts and ComfyUI parameters based on feedback from two independent [LLM + Vision] stacks.

## Purpose

To autonomously refine images through a loop of generation, critique, mutation, and repetition, achieving better semantic alignment, style fidelity, and overall quality.

## Features

- **ComfyUI Integration**: Generates images via API.
- **Dual Nexa CLI Instances**:
  - `nexa_qwen3`: Semantic-focused (Qwen3 + Vision)
  - `nexa_wizard`: Style-focused (WizardLM + Vision)
- **Iterative Loop**: Generate → Extract Tags → Score → Mutate → Repeat
- **Modular Nodes**: Classes for mutation, tuning, extraction, scoring, arbitration, logging

## Installation

1. **Clone or Download**: Get the project files.
2. **Python Environment**:
   - Install Python 3.10+
   - Create venv: `python -m venv .venv`
   - Activate: `.venv\Scripts\activate` (Windows)
3. **Install Dependencies**:
   - `pip install -r requirements.txt`
4. **Install ComfyUI**:
   - Follow https://github.com/comfyanonymous/ComfyUI
   - Run ComfyUI server: `comfyui --server` (listens on 127.0.0.1:8188)
5. **Install Nexa CLI**:
   - `pip install nexa-cli`
   - Pull models: `nexa pull qwen3` and `nexa pull wizardlm`

## Usage

1. **Start Services**:
   - Launch ComfyUI server.
   - Ensure Nexa models are ready.

2. **Run the Agent**:
   - Use VS Code task: "Run Adaptive Image Improvement" (configured in .vscode/tasks.json)
   - Or manually: `python src/adaptive_image_improvement.py`

3. **Monitor**:
   - Check `improvement_log.txt` for logs.
   - Images saved in output directory (if configured in ComfyUI workflow).

## Workflow Details

- **Initial Setup**: Prompt and params (CFG, steps).
- **Loop (Max 10 iterations)**:
  1. Generate image via ComfyUI API.
  2. Extract semantic tags (qwen3) and style tags (wizard).
  3. Score alignment.
  4. If improved, accept; else mutate prompt/params.
- **Output**: Final image, log of iterations.

## Configuration

- Edit `src/adaptive_image_improvement.py` for workflow JSON, prompts, thresholds.
- ComfyUI workflow assumes a basic KSampler setup.

## Dependencies

- Python 3.10+
- ComfyUI
- Nexa CLI with qwen3 and wizardlm
- Packages: pillow, opencv-python, numpy, matplotlib, requests

## Troubleshooting

- Ensure ComfyUI server is running on port 8188.
- Check Nexa CLI for model availability.
- Logs in `improvement_log.txt` for debugging.

## License

MIT