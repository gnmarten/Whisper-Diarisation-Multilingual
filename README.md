# Whisper-Diarisation-Multilingual
Diarized transcription of audiofiles in languages other than English. Google Cloud says this is not possible, but it is (not perfect, but with a rather high level of accuracy).

This presupposes that you have a folder with audio files containing one single speaker per file (30 seconds are enough). I used Miguel Valente's [Whisperer](https://github.com/miguelvalente/whisperer)
to extract single speakers from multi-speaker audio first. (Beware that Whisperer requires PyTorch 1.x) When processing via Whisper Diarisation Multilingual script, speakers will be assigned the most likely speaker label on the basis of the single-speaker filenames. Tested with German and Whisper large v2. You need a a Huggingface key granting access to all PyAnnote models.
