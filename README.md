# CaptionViewerNew

A python .mp4 player that automatically transcribes subtitles and translation for these subtitles while watching a video.
```
# run
python3 main.py
```

![alt text](./showcase.png)

Uses whisper to transcribe and googletrans to translate. Uses python-vlc to create the player. Supports 100+ languages (both as input and translation target).

I personally use it to practice languages after downloading the .mp4 of a show I like. Hope you enjoy!

Requirements:
You must have ffmpeg installed!
```
# I used whisper version 20230314
python3 -m pip install openai-whisper
# vlc version 3.0.18122
python3 -m pip install --upgrade python-vlc
# PyQt6 version 6.4.2
python3 -m pip install PyQt6
# googletrans version 4.0.0-rc.1
python3 -m pip install googletrans
```
