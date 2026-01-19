import tkinter as tk
import os
import shutil
import subprocess
# Assume tkinterdnd2 is installed for drag drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = tk
    DND_FILES = None

class NexaPopupLoaderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {} }

    RETURN_TYPES = ()
    FUNCTION = "load"
    CATEGORY = "nexa"
    OUTPUT_NODE = True

    def validate_nexa_model_file(self, file_path):
        valid_extensions = ['.gguf', '.bin', '.safetensors', '.pth', '.ckpt', '.onnx', '.pb']
        file_name = os.path.basename(file_path).lower()
        file_extension = os.path.splitext(file_name)[1]

        if file_extension not in valid_extensions:
            print(f"❌ File type not supported: {file_name}. Supported formats: {', '.join(valid_extensions)}")
            return False

        # Additional validation for known incompatible patterns
        incompatible_patterns = ['.exe', '.dll', '.so', '.dylib', '.zip', '.rar', '.7z']
        if any(pattern in file_name for pattern in incompatible_patterns):
            print(f"❌ Incompatible file: {file_name}. This appears to be an executable or archive, not a model file.")
            return False

        print(f"✅ File accepted: {file_name} ({os.path.getsize(file_path) / (1024 * 1024):.2f}MB)")
        return True

    def load_nexa_model(self, file_path):
        try:
            print(f"Loading Nexa model: {os.path.basename(file_path)}")
            # Assume models directory
            models_dir = os.path.expanduser("~/.nexa/models")
            os.makedirs(models_dir, exist_ok=True)
            dest_path = os.path.join(models_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
            print(f"Model loaded successfully: {dest_path}")
        except Exception as error:
            print(f"Failed to load model: {str(error)}")

    def open_chat(self, model):
        chat_window = tk.Toplevel()
        chat_window.title(f"Chat with {model}")
        chat_window.geometry("500x400")

        output_text = tk.Text(chat_window, height=15, state=tk.DISABLED)
        output_text.pack(expand=True, fill=tk.BOTH)

        input_frame = tk.Frame(chat_window)
        input_frame.pack(fill=tk.X)

        input_entry = tk.Entry(input_frame)
        input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        def send_message():
            message = input_entry.get()
            if message:
                output_text.config(state=tk.NORMAL)
                output_text.insert(tk.END, f"You: {message}\n")
                output_text.config(state=tk.DISABLED)
                input_entry.delete(0, tk.END)
                # Call nexa
                try:
                    result = subprocess.run(['nexa', 'run', model, '-p', message], capture_output=True, text=True, timeout=30)
                    response = result.stdout.strip()
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"{model}: {response}\n")
                    output_text.config(state=tk.DISABLED)
                except Exception as e:
                    output_text.config(state=tk.NORMAL)
                    output_text.insert(tk.END, f"Error: {str(e)}\n")
                    output_text.config(state=tk.DISABLED)

        send_btn = tk.Button(input_frame, text="Send", command=send_message)
        send_btn.pack(side=tk.RIGHT)

    def load(self):
        # Create pop-up window for drag & drop model loading
        root = TkinterDnD.Tk() if TkinterDnD != tk else tk.Tk()
        root.title("Nexa Model Loader")
        root.geometry("400x300")

        label = tk.Label(root, text="Drag and drop Nexa model files here to load")
        label.pack(expand=True)

        def on_drop(event):
            if DND_FILES:
                files = root.splitlist(event.data)
                for file_path in files:
                    if self.validate_nexa_model_file(file_path):
                        self.load_nexa_model(file_path)
                        label.config(text=f"Loaded: {os.path.basename(file_path)}")
                    else:
                        label.config(text="Invalid file")
            else:
                label.config(text="Drag & drop not supported, install tkinterdnd2")

        if DND_FILES:
            label.drop_target_register(DND_FILES)
            label.dnd_bind('<<Drop>>', on_drop)

        # Chat buttons
        semantic_chat_btn = tk.Button(root, text="Chat with Semantic Model", command=lambda: self.open_chat('qwen3'))
        style_chat_btn = tk.Button(root, text="Chat with Style Model", command=lambda: self.open_chat('wizardlm'))
        semantic_chat_btn.pack()
        style_chat_btn.pack()

        # Close button
        close_btn = tk.Button(root, text="Close", command=root.destroy)
        close_btn.pack()

        root.mainloop()
        return ()