import subprocess
import os
import json

class AudioTagExtractorNodeA:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "custom_prompt": ("STRING", {"default": "Extract semantic tags: instruments, structure, vocals, temporal features"}),
                "model_name": ("STRING", {"default": "audiosemantic"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("semantic_tags",)
    FUNCTION = "extract_semantic_tags"
    CATEGORY = "audio_tagging"
    OUTPUT_NODE = False

    def extract_semantic_tags(self, audio_path, custom_prompt="Extract semantic tags: instruments, structure, vocals, temporal features", model_name="audiosemantic"):
        """Extract semantic audio tags using Nexa CLI"""

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
            # Call Nexa CLI for semantic audio tags
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
                    tags = "No semantic tags extracted"
                return (tags,)
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                return (f"Error extracting semantic tags: {error_msg}",)

        except subprocess.TimeoutExpired:
            return ("Error: Tag extraction timed out after 60 seconds",)
        except FileNotFoundError:
            return ("Error: Nexa CLI not found. Please install Nexa CLI and ensure it's in your PATH",)
        except Exception as e:
            return (f"Unexpected error during semantic tag extraction: {str(e)}",)