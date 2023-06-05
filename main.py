from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog

import vlc

from settings import STATE, CONFIG

import sys
import os
import pathlib


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_path):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(ui_path, self) # Load the .ui file

        # link menubar
        self.actionAudio.triggered.connect(select_audio)
        self.actionSubtitles.triggered.connect(select_subtitles)


def select_audio():
    print("audio selection")
    file_dialog = QFileDialog()
    file_dialog.setNameFilters(["Audio files (*.mp3 *.wav, *.mp4)"])
    file_dialog.exec()
    fname = file_dialog.selectedFiles()[0]
    print(fname, os.path.exists(fname))
    if os.path.exists(fname):
        file_path = pathlib.Path(fname)
        STATE['audio_file'] = file_path
    else:
        STATE['audio_file'] = None 

    load_audio()


def select_subtitles():
    print("subtitle selection")
    file_dialog = QFileDialog()
    file_dialog.setNameFilters(["Subtitles files (*.srt)"])
    file_dialog.exec()
    fname = file_dialog.selectedFiles()[0]

    if os.path.exists(fname):
        file_path = pathlib.Path(fname)
        STATE['subtitle_file'] = file_path
    else:
        STATE['subtitle_file'] = None 


def load_audio():
    STATE['active_time'] = 0
    if STATE['audio_file'] is None:
        reset_audio()
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


def reset_audio():
    """ TODO: implement reset audio
    """

def reset_progress_bar():
    """ TODO: implement
    """


def set_progress_bar_maximum():
    window.progressBar.setMaximum(STATE["audio_duration"])

def update_progress_bar():
    window.progressBar.setValue(int(STATE["audio_duration"]))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow("mainwindow.ui")
    window.show()
    app.exec()

