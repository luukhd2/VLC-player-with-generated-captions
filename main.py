from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog

import vlc

from settings import STATE, CONFIG

import sys
import os
import pathlib
import warnings



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_path):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(ui_path, self) # Load the .ui file

        # link menubar
        self.actionAudio.triggered.connect(select_audio)
        self.actionSubtitles.triggered.connect(select_subtitles)

        self.playButton.pressed.connect(pressed_play_button)


def select_audio():
    print("audio selection")
    file_dialog = QFileDialog()
    file_dialog.setNameFilters(["Audio files (*.mp3 *.wav, *.mp4)"])
    file_dialog.exec()

    fname = file_dialog.selectedFiles()[0]
    file_path = pathlib.Path(fname)

    set_audio(fname)
    load_audio() # automatically load audio when selected


def set_audio(file_path):
    """
    """
    if os.path.exists(file_path):
        STATE['audio_file'] = file_path
    else:
        warnings.warn(f"Audio file does not exist: {file_path}")
        STATE['audio_file'] = None 

def reset_audio():
    """
    """
    STATE['active_time'] = 0
    STATE['player'] = None 
    STATE['audio_file'] = None 
    STATE['media'] = None 
    STATE['audio_duration'] = None 
    reset_progress_bar()
    
def load_audio():
    if STATE['audio_file'] is None:
        reset_progress_bar()
    else:
        player = vlc.MediaPlayer()
        media = vlc.Media(STATE['audio_file'])
        media.parse_with_options(1, 0)
        while media.get_duration() < 0:
            continue
        player.set_media(media)

        STATE['audio_duration'] = media.get_duration()
        STATE['player'] = player
        STATE['media'] = media
        
        print("Audio duration", STATE["audio_duration"])
        set_progress_bar_maximum()
        update_progress_bar()


def pressed_play_button():
    """
    """
    # only play if player exists
    player = STATE['player']
    if player is None:
        warnings.warn("Tried to play but player is None")
        return 

    # if pressed and audio was already playing.
    current_state = player.get_state()
    
    if current_state == vlc.State.Playing:
        pause_audio()
    elif current_state == vlc.State.Ended:
        load_audio()
        play_audio()
    elif current_state == vlc.State.Paused or current_state == vlc.State.NothingSpecial:
        play_audio()
    else:
        warnings.warn(f"Unaccounted vlc.State {current_state}")

def play_audio():
    print("playing audio")
    player = STATE['player']
    player.play()

def pause_audio():
    player = STATE['player']
    player.pause()

def select_subtitles():
    print("subtitle selection")
    file_dialog = QFileDialog()
    file_dialog.setNameFilters(["Subtitles files (*.srt)"])
    file_dialog.exec()

    fname = file_dialog.selectedFiles()[0]
    file_path = pathlib.Path(fname)

    set_subtitles(file_path=file_path)
 
    load_subtitles() # automatically load subtitles after selecting

def set_subtitles(file_path):
    if os.path.exists(file_path):
        STATE['subtitle_file'] = file_path
    else:
        warnings.warn(f"Subtitle path does not exist {file_path}")
        STATE['subtitle_file'] = None 

def load_subtitles():
    """ # TODO: all load subtitle function
    """

def reset_progress_bar():
    """ TODO: implement
    """

def set_progress_bar_maximum():
    window.progressBar.setMaximum(STATE["audio_duration"])

def update_progress_bar():
    window.progressBar.setValue(int(STATE["audio_duration"]))


def debug():
    """
    Load audio into the window so it doesn't have to be done manually
    """
    audio_path = pathlib.Path("/Users/kcd635/Documents/GitHub/CaptionViewerNew/Carl Sagan - Pale Blue Dot.mp4")
    set_audio(audio_path)
    load_audio()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow("mainwindow.ui")
    debug()
    window.show()
    app.exec()

