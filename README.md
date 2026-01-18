# Adaptive Image Improvement

This project implements an autonomous image refinement loop called **Adaptive Image Improvement**. The goal is to iteratively improve the quality, alignment, and aesthetic fidelity of generated images by adjusting prompts and ComfyUI parameters based on feedback from two independent [LLM + Vision] stacks.

## Features

- Uses ComfyUI for image generation
- Two Nexa CLI instances: `nexa_qwen3` (semantic-focused) and `nexa_wizard` (style-focused)
- Iterative loop: generate, critique, mutate, repeat
- Nodes for prompt mutation, parameter tuning, vision tagging, scoring, arbitration, logging

## Installation

1. Install Python 3.x
2. Install dependencies: `pip install -r requirements.txt`
3. Install ComfyUI: Follow instructions at https://github.com/comfyanonymous/ComfyUI
4. Install Nexa CLI: `pip install nexa-cli` (assuming available)
5. Set up models for Nexa: `nexa pull qwen3` and `nexa pull wizardlm` or appropriate models

## Usage

Run the main script: `python src/main.py`

Provide initial prompt and parameters.

## Next Steps

Implement the full agent loop.