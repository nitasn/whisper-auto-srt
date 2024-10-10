import os
import re
import sys
import tempfile
import subprocess
import subprocess
from pathlib import Path

WHISPER_PATH = '~/whisper.cpp/main'
WHISPER_MODEL_PATH = '~/whisper.cpp/models/ggml-large-v3.bin'


def to_wav_16_audio(input_file, temp_file_name):
  print(f"\nConverting into 16kHz wav format @ '{temp_file_name}'...")
  ffmpeg_argv = ["ffmpeg", "-y", "-i", input_file, "-ar", "16000", temp_file_name]
  result = subprocess.run(ffmpeg_argv, text=True, capture_output=True)
  if result.returncode != 0:
    print("Error: couldn't convert the file into wav format.")
    print(f"ffmpeg command failed with exit status {result.returncode}")
    exit(1)


def run_subprocess_with_output(command):
  with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as proc:
    output = []
    for line in proc.stdout:
      sys.stdout.write(line)
      output.append(line)
  return ''.join(output)


def transcribe_audio(lang, temp_file_name):
  print(f"Transcribing audio using whisper...\n")
  executable = os.path.expanduser(WHISPER_PATH)
  model_path = os.path.expanduser(WHISPER_MODEL_PATH)
  whisper_argv = [executable, "-l", lang, "-m", model_path, "-f", temp_file_name]
  return run_subprocess_with_output(whisper_argv)


def whisper_txt_to_srt(whisper_txt):
  srt_lines = []
  whisper_lines = whisper_txt.strip().split('\n')

  for index, line in enumerate(whisper_lines):
    timestamp_regex = r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s+(.*)"
    
    if time_match := re.match(timestamp_regex, line):
      start_time, end_time, text = time_match.groups()
      
      # convert from hh:mm:ss.ms to hh:mm:ss,ms
      start_time = start_time.replace('.', ',')
      end_time = end_time.replace('.', ',')

      srt_lines.append(f"{index + 1}")
      srt_lines.append(f"{start_time} --> {end_time}")
      srt_lines.append(text)
      srt_lines.append("")
      
  return '\n'.join(srt_lines)


def video_to_srt(vid_path, lang):
  srt_path = Path(vid_path).with_suffix('.srt')

  with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp_wav_file:
    to_wav_16_audio(vid_path, tmp_wav_file.name)
    whisper_txt = transcribe_audio(lang, tmp_wav_file.name)
  
  srt_txt = whisper_txt_to_srt(whisper_txt)
  
  with open(srt_path, 'w') as srt_file:
    srt_file.write(srt_txt)
  
  print(f"\nCreated Subtitles File @ '{srt_path}'\n")


def get_vid_path():
  input_file = input("Drag in a video/audio file! \n > ").strip().strip("'")
  if os.path.isfile(input_file):
    return input_file
  else:
    print(f"Error: File '{input_file}' does not exist.")
    exit(1)


def get_lang():
  lang = input("Choose language: en / he / fr / ...  \n > ").strip()
  supported_langs = { "en", "he", "fr", "es", "de", "it", "ru", "zh", "ja", "ko", "ar", "pt" }
  if lang in supported_langs:
    return lang
  else:
    print(f"Error: Unsupported language '{lang}'. Exiting.")
    exit(1)


def main():
  vid_path = get_vid_path()
  lang = get_lang()
  video_to_srt(vid_path, lang)


if __name__ == "__main__":
  main()
