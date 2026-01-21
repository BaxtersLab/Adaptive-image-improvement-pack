import subprocess
import os
import json

class AudioTagExtractorNodeB:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "custom_prompt": ("STRING", {"default": "Extract style tags: genre, production, texture, mood"}),
                "model_name": ("STRING", {"default": "audiostyle"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("style_tags",)
    FUNCTION = "extract_style_tags"
    CATEGORY = "audio_tagging"
    OUTPUT_NODE = False

    def extract_style_tags(self, audio_path, custom_prompt="Extract style tags: genre, production, texture, mood", model_name="audiostyle"):
        """Extract style audio tags using Nexa CLI"""

        # Validate input
        if not audio_path or not audio_path.strip():
            return ("Error: No audio file path provided",)

        if not os.path.exists(audio_path):
            return (f"Error: Audio file not found: {audio_path}",)

        # Validate file extension
        allowed_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
        if not any(audio_path.lower().endswith(ext) for ext in allowed_extensions):
            return (f"Error: Unsupported audio format. Supported: {', '.join(allowed_extensions)}",)

        try:
            # Call Nexa CLI for style audio tags
            cmd = ['nexa', 'run', model_name, '-i', audio_path, '-p', custom_prompt]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                tags = result.stdout.strip()
                if not tags:
                    tags = "No style tags extracted"
                return (tags,)
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                return (f"Error extracting style tags: {error_msg}",)

        except subprocess.TimeoutExpired:
            return ("Error: Tag extraction timed out after 60 seconds",)
        except FileNotFoundError:
            return ("Error: Nexa CLI not found. Please install Nexa CLI and ensure it's in your PATH",)
        except Exception as e:
            return (f"Unexpected error during style tag extraction: {str(e)}",)