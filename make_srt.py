from pathlib import Path
import os, re, sys, tempfile
from subprocess import Popen, PIPE, DEVNULL, run as run_subprocess

WHISPER_PATH = '~/whisper.cpp/main'
WHISPER_MODEL_PATH = '~/whisper.cpp/models/ggml-large-v3.bin'


def transcribe_audio(lang, wav_path, srt_writer):
  executable = os.path.expanduser(WHISPER_PATH)
  model_path = os.path.expanduser(WHISPER_MODEL_PATH)
  whisper_argv = [executable, "-l", lang, "-m", model_path, "-f", wav_path]
  with Popen(whisper_argv, stdout=PIPE, stderr=DEVNULL, text=True) as whisper_process:
    for line in whisper_process.stdout:
      sys.stdout.write(line)
      srt_writer.append(line)


class WhisperOutputToSRT:
  def __init__(self, srt_file):
    self.file = srt_file
    self.next_row = 1
  
  # [00:00:14.840 --> 00:00:17.180]   אח, איזו חיפושית זבל
  whisper_regex = r"\[(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\]\s+(.*)"

  def append(self, whisper_line):
    matches = re.match(WhisperOutputToSRT.whisper_regex, whisper_line)
    if not matches: return
    
    start_time, end_time, text = matches.groups()

    # convert timestamps from hh:mm:ss.ms to hh:mm:ss,ms
    start_time = start_time.replace('.', ',')
    end_time = end_time.replace('.', ',')

    self.file.write(f"{self.next_row}\n")
    self.file.write(f"{start_time} --> {end_time}\n")
    self.file.write(f"{text}\n\n")
    
    self.next_row += 1


def video_to_srt(vid_path, lang):
  srt_path = Path(vid_path).with_suffix('.srt')

  with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp_wav_file:
    print(f"\nExtracting audio...")
    to_wav_16_audio(vid_path, tmp_wav_file.name)
    
    with open(srt_path, 'w') as srt_file:
      print(f"Transcribing...\n")
      srt_writer = WhisperOutputToSRT(srt_file)
      transcribe_audio(lang, tmp_wav_file.name, srt_writer)
  
  print(f"Done!\nSubtitles file @ '{srt_path}'\n")


def panic(err_msg):
  print(f"\nError: {err_msg}", file=sys.stderr)
  exit(1)


def to_wav_16_audio(input_path, output_path):
  ffmpeg_argv = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", output_path]
  result = run_subprocess(ffmpeg_argv, text=True, capture_output=True)
  if result.returncode != 0:
    panic(f"`ffmpeg` returned status {result.returncode}.\n" \
          "Did you enter a valid video file?")


def get_vid_path():
  input_file = input("\nDrag in a video file! \n > ").strip().strip("'")
  if not os.path.isfile(input_file):
    panic(f"File '{input_file}' does not exist.")
  return input_file


def get_lang():
  lang = input("\nChoose language: en / he / fr / ...  \n > ").strip()
  supported_langs = { "en", "he", "fr", "es", "de", "it", "ru", "zh", "ja", "ko", "ar", "pt" }
  if lang not in supported_langs:
    panic(f"Language '{lang}' is not supported.")
  return lang


def main():
  vid_path = get_vid_path()
  lang = get_lang()
  video_to_srt(vid_path, lang)


if __name__ == "__main__":
  main()
