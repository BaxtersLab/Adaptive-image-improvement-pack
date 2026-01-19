# Adaptive Image Improvement

A ComfyUI extension for autonomous image refinement using dual Nexa CLI instances with drag-and-drop model loading and chat interfaces.

## Purpose

To autonomously refine images through a loop of generation, critique, mutation, and repetition, achieving better semantic alignment, style fidelity, and overall quality.

## Features

- **ComfyUI Integration**: Generates images via API.
- **Dual Nexa CLI Instances**:
  - `qwen3`: Semantic-focused (Qwen3 + Vision)
  - `wizardlm`: Style-focused (WizardLM + Vision)
- **Iterative Loop**: Generate → Extract Tags → Score → Mutate → Repeat
- **Modular Nodes**: Classes for mutation, tuning, extraction, scoring, arbitration, logging
- **NexaPopupLoaderNode**: Drag-and-drop model loading with chat interfaces for both models

## Installation

1. **Install ComfyUI**:
   - Follow https://github.com/comfyanonymous/ComfyUI
2. **Install the Extension**:
   - Clone or download this repo into `ComfyUI/custom_nodes/`
   - Or use ComfyUI Manager to install.
3. **Install Dependencies**:
   - `pip install -r requirements.txt`
4. **Install Nexa CLI**:
   - `pip install nexa-cli`
   - Pull models: `nexa pull qwen3` and `nexa pull wizardlm`

## Usage

1. **Start ComfyUI**:
   - Run ComfyUI server.
2. **Load the Extension**:
   - The nodes will appear in ComfyUI under "nexa" category.
3. **Use NexaPopupLoaderNode**:
   - Add to workflow, run to open GUI for loading models and chatting.
4. **Build Workflow**:
   - Connect nodes for the refinement loop (future: convert script nodes to ComfyUI nodes).
5. **Monitor**:
   - Logs in ComfyUI console.

## Nodes Overview

### NexaPopupLoaderNode

- **Function**: Opens a desktop popup for drag-and-drop model loading, with chat buttons for semantic and style models.
- **Chat**: Interactive chat with qwen3 (semantic) and wizardlm (style) using Nexa CLI.

## Dependencies

- ComfyUI
- Nexa CLI with qwen3 and wizardlm
- tkinter, tkinterdnd2 (for GUI)

## Troubleshooting

- Ensure ComfyUI is running.
- Check Nexa CLI for model availability.
- GUI requires tkinterdnd2 for drag-drop.

## License

MIT

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