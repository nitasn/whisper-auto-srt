#!/usr/bin/env sh

echo "Drag in an audio file!"

read input

if [ ! -f "$input" ]; then
    echo "Error: File '$input' does not exist."
    exit 1
fi

echo "Choose language: en / he / fr / ... "

read lang

supported_langs=("en" "he" "fr" "es" "de" "it" "ru" "zh" "ja" "ko" "ar" "pt")

if [[ ! " ${supported_langs[@]} " =~ " ${lang} " ]]; then
    echo "Error: Unsupported language '$lang'. Exiting."
    exit 1
fi


output="${input%.*}.txt"

tmp=$(mktemp .tmp.XXXXXX)
mv $tmp "$tmp.wav"
tmp="$tmp.wav"

trap "rm -f $tmp" EXIT

echo "\n Converting into 16kHz wav format @ '$tmp'... \n"
ffmpeg -y -i "$input" -ar 16000 "$tmp"

if [ $? -ne 0 ]; then
    echo "Error: couldn't convert the file into wav format."
    echo "ffmpeg command failed with exit status $?"
    exit 1
fi

echo "\n Transcribing '$tmp' using whisper... \n"
~/whisper.cpp/main -nt -l $lang -m ~/whisper.cpp/models/ggml-large-v3.bin -f "$tmp" | tee "$output"

echo "\n Done! Created '$output'. \n"
