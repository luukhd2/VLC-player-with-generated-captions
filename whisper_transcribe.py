#!/usr/bin/python
import os
import subprocess, sys
import time
import traceback
import threading 
import io
import pathlib


def get_whisper_command_str(path_to_audio_file, model, language, model_dir):
    """
    python3 whisper_test.py --model 'tiny' --model_dir ./models --audio_path './a.mp3' --lan "ru"
    """
    # -u tells it not to buffer
    return f"python3 -u ./whisper_terminal.py --model {model} --model_dir {model_dir} --audio_path '{path_to_audio_file}' --lan {language}"


def parse_whisper_time_string(time_str):
    """
    16:07.360 -> <int> 16 mins, <int> 7 secs, <int> 360 ms
    """
    hours = 0
    mins = 0
    secs = 0
    ms = 0

    if time_str.count(":") < 2:
        mins, rest = time_str.split(":", 1)
        secs, ms = rest.split(".", 1)
    else:
        hours, rest = time_str.split(":", 1) 
        mins, rest = rest.split(":", 1)
        secs, ms = rest.split(".", 1)

    return int(hours), int(mins), int(secs), int(ms)


def times_to_ms(hours, mins, secs, ms):
    return hours*3600000 + mins*60000 + secs*1000 + ms


def parse_whisper_terminal_line(line):
    """
    input example: <str>
                  "[00:09.320 --> 00:11.600]   test 123 this is a sentence."
    """
    # get text
    text = line.split(']', 1)[1].strip()
    
    # get time segments
    line = line.strip()
    time_segment = "".join(line.partition("]")[0:1])
    time_segment = time_segment.replace("[", "")
    start_str, end_str = time_segment.split("-->")

    # get times
    s_h, s_m, s_s, s_ms = parse_whisper_time_string(start_str)
    e_h, e_m, e_s, e_ms = parse_whisper_time_string(end_str)
    start_time_ms = times_to_ms(s_h, s_m, s_s, s_ms)
    end_time_ms = times_to_ms(e_h, e_m, e_s, e_ms)

    return start_time_ms, end_time_ms, text


def start_live_transcription(list_with_subtitle_text_and_times,  audio_path, model, language, model_dir):
    # get the shell command for the whisper_terminal.py script    
    your_command = get_whisper_command_str(audio_path, model=model, language=language, model_dir=model_dir)

    # start this command in a subprocess
    proc = subprocess.Popen(your_command, stdout=subprocess.PIPE, shell=True)

    # read the output of the subprocess
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        # do something with line if it is a time line
        if "-->" in line and line.startswith("["):
            start_time, end_time, text = parse_whisper_terminal_line(line)
            list_with_subtitle_text_and_times.append((start_time, end_time, text))
    

if __name__ == "__main__":
    # showcase how this can be used in a thread
    GLOBAL_LIST = list(("Starting transcription...", 0, 0))
    NEW_THREAD = threading.Thread(target=start_live_transcription, args=(GLOBAL_LIST,
                                                                         pathlib.Path("./Carl Sagan - Pale Blue Dot.mp4"),
                                                                        "tiny",
                                                                        "en",
                                                                        "./models/",)
                                )
    NEW_THREAD.start()

    # showcase how the thread transcribes in real time
    OLD_OUT = ""
    while True:
        OUT = GLOBAL_LIST[-1]
        if OUT == OLD_OUT:
            continue
        else:
            print(OUT)
            OLD_OUT = OUT
