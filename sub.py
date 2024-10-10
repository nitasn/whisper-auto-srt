import os
import re
import tempfile
import subprocess

WHISPER_PATH = '~/whisper.cpp/main'
WHISPER_MODEL_PATH = '~/whisper.cpp/models/ggml-large-v3.bin'


def get_input_file():
  input_file = input("Drag in an audio file! \n > ")
  input_file = input_file.strip().strip('"').strip("'")
  if os.path.isfile(input_file):
    return input_file
  else:
    print(f"Error: File '{input_file}' does not exist.")
    exit(1)


def get_lang():
  lang = input("Choose language: en / he / fr / ...  \n > ")
  supported_langs = { "en", "he", "fr", "es", "de", "it", "ru", "zh", "ja", "ko", "ar", "pt" }
  if lang in supported_langs:
    return lang
  else:
    print(f"Error: Unsupported language '{lang}'. Exiting.")
    exit(1)


def convert_audio(input_file, temp_file_name):
  print(f"Converting into 16kHz wav format @ '{temp_file_name}'...")
  ffmpeg_argv = ["ffmpeg", "-y", "-i", input_file, "-ar", "16000", temp_file_name]
  result = subprocess.run(ffmpeg_argv, text=True, capture_output=True)
  if result.returncode != 0:
    print("Error: couldn't convert the file into wav format.")
    print(f"ffmpeg command failed with exit status {result.returncode}")
    exit(1)


def transcribe_audio(lang, temp_file_name, output_file):
  print(f"Transcribing '{temp_file_name}' using whisper...\n")
  executable = os.path.expanduser(WHISPER_PATH)
  model_path = os.path.expanduser(WHISPER_MODEL_PATH)
  with open(output_file, 'w') as out_file:
    whisper_argv = [executable, "-l", lang, "-m", model_path, "-f", temp_file_name]
    print(whisper_argv)
    subprocess.run(whisper_argv, text=True, stdout=out_file)


def whisper_to_srt(whisper_output):
  lines = whisper_output.strip().split('\n')
  srt_lines = []

  for index, line in enumerate(lines):
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
  

def main():
  input_file = get_input_file()
  lang = get_lang()

  output_file = f"{os.path.splitext(input_file)[0]}.txt"
  with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
    convert_audio(input_file, temp_file.name)
    transcribe_audio(lang, temp_file.name, output_file)
    
  print(f"\nTranscribed Audio @ '{output_file}'")
    
  srt_path = f"{os.path.splitext(input_file)[0]}.srt"
  with open(output_file) as txt_file:
    srt = whisper_to_srt(txt_file.read())
  with open(srt_path, 'w') as srt_file:
    srt_file.write(srt)

  print(f"\nCreated Subtitles File @ '{srt_path}'\n")


if __name__ == "__main__":
  main()
