#!/usr/bin/env python3
"""
Adaptive Image Improvement Agent
Orchestrates the autonomous image refinement loop.
"""

import os
import subprocess
import requests
import json
import time
from PIL import Image
import logging

# Configure logging
logging.basicConfig(filename='improvement_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PromptMutatorNode:
    def mutate(self, prompt, feedback):
        # Use LLM to revise prompt based on feedback
        # Placeholder: simple concatenation
        new_prompt = f"{prompt}, improved: {feedback}"
        logging.info(f"Mutated prompt: {new_prompt}")
        return new_prompt

class ComfyParamTunerNode:
    def tune(self, params, feedback):
        # Adjust parameters based on feedback
        # Placeholder: increase steps if quality low
        if 'quality' in feedback.lower():
            params['steps'] += 5
        logging.info(f"Tuned params: {params}")
        return params

class VisionTagExtractorNode:
    def __init__(self, model_name):
        self.model_name = model_name

    def extract(self, image_path):
        # Call Nexa CLI
        cmd = ['nexa', 'run', self.model_name, '--image', image_path, '--prompt', 'Extract tags and critique']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            tags = result.stdout.strip()
            logging.info(f"Extracted tags from {self.model_name}: {tags}")
            return tags
        else:
            logging.error(f"Error extracting tags: {result.stderr}")
            return ""

class PromptScoreNode:
    def score(self, prompt, tags_qwen, tags_wizard):
        # Compare prompt to tags
        # Placeholder: simple overlap count
        prompt_words = set(prompt.lower().split())
        tags_words = set((tags_qwen + tags_wizard).lower().split())
        overlap = len(prompt_words & tags_words)
        score = overlap / len(prompt_words) if prompt_words else 0
        logging.info(f"Alignment score: {score}")
        return score

class ImprovementArbiterNode:
    def decide(self, score, prev_score):
        if score > prev_score + 0.1:
            return 'accept'
        elif score < prev_score:
            return 'revert'
        else:
            return 'continue'

class LoopControllerNode:
    def __init__(self, max_iter=10):
        self.max_iter = max_iter
        self.iteration = 0

    def next(self):
        self.iteration += 1
        return self.iteration <= self.max_iter

def generate_image(prompt, params):
    # Placeholder for ComfyUI API call
    # Assume ComfyUI server running on 8188
    workflow = {
        # Simplified workflow JSON
        "prompt": {
            "3": {"inputs": {"seed": 123, "steps": params['steps'], "cfg": params['cfg'], "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
            "4": {"inputs": {"ckpt_name": "model.ckpt"}, "class_type": "CheckpointLoaderSimple"},
            "5": {"inputs": {"width": 512, "height": 512, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "6": {"inputs": {"text": prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "7": {"inputs": {"text": "blurry, low quality", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
            "9": {"inputs": {"filename_prefix": "output", "images": ["8", 0]}, "class_type": "SaveImage"}
        }
    }
    response = requests.post('http://127.0.0.1:8188/prompt', json=workflow)
    if response.status_code == 200:
        prompt_id = response.json()['prompt_id']
        # Poll for completion
        while True:
            status = requests.get(f'http://127.0.0.1:8188/history/{prompt_id}')
            if status.json():
                break
            time.sleep(1)
        # Assume image saved as output_00001_.png
        image_path = 'output/output_00001_.png'
        logging.info(f"Generated image: {image_path}")
        return image_path
    else:
        logging.error("Failed to generate image")
        return None

def main():
    # Initialize nodes
    mutator = PromptMutatorNode()
    tuner = ComfyParamTunerNode()
    extractor_qwen = VisionTagExtractorNode('qwen3')
    extractor_wizard = VisionTagExtractorNode('wizard')
    scorer = PromptScoreNode()
    arbiter = ImprovementArbiterNode()
    controller = LoopControllerNode()

    # Initial state
    prompt = "a beautiful sunset over mountains"
    params = {'cfg': 7.0, 'steps': 20}
    prev_score = 0
    best_image = None

    while controller.next():
        logging.info(f"Iteration {controller.iteration}")
        image_path = generate_image(prompt, params)
        if not image_path:
            break

        tags_qwen = extractor_qwen.extract(image_path)
        tags_wizard = extractor_wizard.extract(image_path)

        score = scorer.score(prompt, tags_qwen, tags_wizard)

        decision = arbiter.decide(score, prev_score)

        if decision == 'accept':
            best_image = image_path
            logging.info("Accepted image")
            break
        elif decision == 'revert':
            # Revert to previous
            logging.info("Reverted")
            break
        else:
            feedback = f"Qwen: {tags_qwen}, Wizard: {tags_wizard}"
            prompt = mutator.mutate(prompt, feedback)
            params = tuner.tune(params, feedback)
            prev_score = score

    if best_image:
        print(f"Final image: {best_image}")
    else:
        print("No acceptable image generated")

if __name__ == "__main__":
    main()