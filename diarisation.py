# -*- coding: utf-8 -*-
"""Diarisation Multilingual
Source: https://github.com/gnmarten/Whisper-Diarisation-Multilingual

"""

#you need a key from huggingface with at least finegrained access to all of the pyannote repositories
#the code involves all kinds of verbose troubleshooting in case you want to run this on HPC
HF_KEY = "ENTERYOURHUGGINFACECODEHERE"
input_dir = "/kyukon/data/gent/427/vsc42730/sample_data/transcribes"  # Replace with your input directory
output_dir = "/kyukon/data/gent/427/vsc42730/sample_data/herzog/extracted_audio"  # Replace with your output directory
lang="de" #change language according to your needs, tested with German

#from pyannote.audio import Model
import torch
import subprocess
print(torch.version.cuda)
import os

# Check the CUDA_HOME environment variable
cuda_home = os.environ.get('CUDA_HOME')
print(f"CUDA_HOME: {cuda_home}")

# Check the LD_LIBRARY_PATH environment variable
ld_library_path = os.environ.get('LD_LIBRARY_PATH')
print(f"LD_LIBRARY_PATH: {ld_library_path}")
import os
import torch

print("CUDA_HOME:", os.environ.get('CUDA_HOME'))
print("LD_LIBRARY_PATH:", os.environ.get('LD_LIBRARY_PATH'))
print("PyTorch CUDA available:", torch.cuda.is_available())
print("PyTorch CUDA version:", torch.version.cuda)
import os
import torch
import torchaudio

print("LD_LIBRARY_PATH:", os.environ.get('LD_LIBRARY_PATH'))
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("PyTorch version:", torch.__version__)
print("PyTorch CUDA available:", torch.cuda.is_available())
print("PyTorch CUDA version:", torch.version.cuda)
print("torchaudio version:", torchaudio.__version__)

def check_cuda():
    print("Checking CUDA availability:")
    
    # Check if nvidia-smi is available
    try:
        nvidia_smi = subprocess.check_output(["nvidia-smi"]).decode('utf-8')
        print("CUDA is available. GPU information:")
        print(nvidia_smi)
    except:
        print("nvidia-smi is not available on this system.")
    
    # Check CUDA availability using PyTorch
    if torch.cuda.is_available():
        print("PyTorch CUDA is available.")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("PyTorch CUDA is not available.")

# Call the function to check CUDA
check_cuda()

# Your other code here

import torch
from pyannote.audio import Pipeline

try:
    # Initialize the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the diarization model
    diarize_model = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                             use_auth_token=HF_KEY)

    # Move the model to the specified device
    diarize_model = diarize_model.to(device)

    print("Diarization model initialized successfully.")
except Exception as e:
    print(f"Error initializing diarization model: {e}")

#with loops
import whisperx
import gc
import json
import os
import pandas as pd
import torch
# Set up parameters
device = "cuda"
batch_size = 16 # reduce if low on GPU mem
compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)


# Function to save results to a file
def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(data, pd.DataFrame):
            data.to_json(f, orient='records', lines=True)
        else:
            json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Results saved to {filename}")

# Load models (do this only once, outside the loop)
model = whisperx.load_model("large-v2", device, compute_type=compute_type, language=lang)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_KEY, device=device)

# Process each WAV file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".wav"):
        print(f"Processing {filename}")
        audio_file = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]

        # 1. Transcribe with original whisper (batched)
        audio = whisperx.load_audio(audio_file)
        result = model.transcribe(audio, language='de', batch_size=batch_size)
        print("Transcription complete")
        save_to_file(result["segments"], os.path.join(output_dir, f"{base_name}_transcription_before_alignment.json"))

        # 2. Align whisper output
        model_a, metadata = whisperx.load_align_model(language_code=lang, device=device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
        print("Alignment complete")
        save_to_file(result["segments"], os.path.join(output_dir, f"{base_name}_transcription_after_alignment.json"))

        # 3. Assign speaker labels
        diarize_segments = diarize_model(audio)
        print("Diarization complete")
        save_to_file(diarize_segments, os.path.join(output_dir, f"{base_name}_diarization_segments.json"))

        result = whisperx.assign_word_speakers(diarize_segments, result)
        print("Speaker assignment complete")
        save_to_file(result["segments"], os.path.join(output_dir, f"{base_name}_final_result_with_speakers.json"))

        # 4. Save full transcript with speaker labels
        full_transcript = ""
        for segment in result["segments"]:
            speaker = segment.get("speaker", "Unknown")
            text = segment["text"]
            full_transcript += f"Speaker {speaker}: {text}\n"

        with open(os.path.join(output_dir, f"{base_name}_full_transcript.txt"), "w", encoding="utf-8") as f:
            f.write(full_transcript)
        print(f"Full transcript saved for {filename}")

        # Clear some memory
        gc.collect()
        torch.cuda.empty_cache()

print("All processing complete")
