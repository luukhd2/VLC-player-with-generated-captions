#!/usr/bin/python
import os
import subprocess, sys
import time
import traceback
import threading 


def get_whisper_string(path_to_audio_file, model="tiny", language="English"):
    """
    'af', 'am', 'ar', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bo', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el',
    'en', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 
    'is', 'it', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lb', 'ln', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 
    'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'nn', 'no', 'oc', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'sa', 'sd', 'si', 'sk', 'sl', 'sn', 
    'so', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 'tt', 'uk', 'ur', 'uz', 'vi', 'yi', 'yo', 
    'zh', 'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Assamese', 'Azerbaijani', 'Bashkir', 'Basque', 
    'Belarusian', 'Bengali', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Castilian', 'Catalan', 'Chinese',
      'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Faroese', 'Finnish', 'Flemish', 'French', '
      Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian', 'Haitian Creole', 'Hausa', 'Hawaiian', 'Hebrew', 
      'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Javanese', 'Kannada', 'Kazakh', 'Khmer', 'Korean', 
      'Lao', 'Latin', 'Latvian', 'Letzeburgesch', 'Lingala', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 
      'Maltese', 'Maori', 'Marathi', 'Moldavian', 'Moldovan', 'Mongolian', 'Myanmar', 'Nepali', 'Norwegian', 'Nynorsk', 'Occitan', 'Panjabi', 
      'Pashto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Pushto', 'Romanian', 'Russian', 'Sanskrit', 'Serbian', 'Shona', 'Sindhi',
        'Sinhala', 'Sinhalese', 'Slovak', 'Slovenian', 'Somali', 'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tagalog', 'Tajik',
          'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uzbek', 'Valencian', 'Vietnamese', 
          'Welsh', 'Yiddish', 'Yoruba'
    """
    return f"whisper '{path_to_audio_file}' --condition_on_previous_text False --fp16 False --model {model} --model_dir /Users/kcd635/Documents/GitHub/CaptionViewerNew/models/ --output_format srt --task transcribe --language {language}"


class FileModified():
    def __init__(self, file_path):
        self.file_path = file_path
        self.callback = self.file_modified
        self.modifiedOn = os.path.getmtime(file_path)
        self.last_line_index = -1

    def start(self):
        while (True):
            time.sleep(5)
            modified = os.path.getmtime(self.file_path)
            if modified != self.modifiedOn:
                self.modifiedOn = modified
                if self.callback():
                    break

    def file_modified(self):
        with open(self.file_path, 'rb') as open_file:
            for line_index, line in enumerate(open_file):
                if line_index > self.last_line_index:
                    STRING_LIST.append(line)
                else:
                    pass
            self.last_line_index = line_index
            print(len(STRING_LIST), STRING_LIST[-1])
        return False

def start_file_modifier(file_path):
    fileModifiedHandler = FileModified(logfile_path)
    fileModifiedHandler.start()


STRING_LIST = list()
logfile_path = "test.log"
#audio_path="/Users/kcd635/Documents/GitHub/CaptionViewerNew/Carl Sagan - Pale Blue Dot.mp4"
audio_path="./a.mp3"

modifier_thread = threading.Thread(target=start_file_modifier, args=(logfile_path, ))
modifier_thread.start()

with open(logfile_path, "ab") as f:
    your_command = get_whisper_string(audio_path, language='Russian')
    process = subprocess.Popen(your_command, stdout=subprocess.PIPE, shell=True)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)
        f.write(c)
