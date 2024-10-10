# source: https://medium.com/gimz/how-to-install-whisper-on-mac-openais-speech-to-text-recognition-system-1f6709db6010

cd ~
git clone https://github.com/ggerganov/whisper.cpp

if ! command -v brew &> /dev/null; then
  # `brew` also installs `make`
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

cd ~/whisper.cpp
make
make large-v3

if ! command -v ffmpeg &> /dev/null; then
  brew install ffmpeg
fi