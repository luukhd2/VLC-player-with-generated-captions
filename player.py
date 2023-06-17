import platform
import os
import sys
import typing
import pathlib
import threading

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction, QTextCursor
from PyQt6.QtWidgets import QWidget
import vlc

from subtitle_gui import TranslationLabel, SubtitleBrowser, LanguageSettingLabel
from translate import get_languages
from whisper_transcribe import start_live_transcription

class Player(QtWidgets.QMainWindow):
    """A simple Media Player using VLC and Qt
    """

    def __init__(self, settings):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Media Player")

        # store settings dict
        self.settings = settings

        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()
        self.is_paused = False

    def create_ui(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if platform.system() == "Darwin": # for MacOS
            self.videoframe = QOpenGLWidget()
        else:
            self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        # slider window for audio playing progress
        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        # transcription progress bar. User can not interact
        self.transcription_progress_bar = QtWidgets.QProgressBar(self)
        self.transcription_progress_bar.setValue(0)
        self.transcription_progress_bar.setMaximum(100)
        self.transcription_progress_bar.setDisabled(True)
		
        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.playbutton = QtWidgets.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)

        self.stopbutton = QtWidgets.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)


        ### Custom: Link the subtitle part of the player
        self.language_setting_label = LanguageSettingLabel(self.settings['in_lan'], self.settings['out_lan'])
        self.translation_label = TranslationLabel()
        self.subtitle_browser = SubtitleBrowser(self, self.settings['in_lan'], self.settings['out_lan'])
        self.vboxlayout.addWidget(self.language_setting_label)
        self.vboxlayout.addWidget(self.translation_label)
        self.vboxlayout.addWidget(self.subtitle_browser)
        self.vboxlayout.addWidget(self.transcription_progress_bar)
        ###

        self.widget.setLayout(self.vboxlayout)

        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        # Add actions to file menu
        open_action = QAction("Load Video", self)
        close_action = QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        open_action.triggered.connect(self.open_audio_file)
        close_action.triggered.connect(sys.exit)

        # add dropdown menus for input and output languages to the menubar
        language_input_menu = menu_bar.addMenu("InputLanguage")
        language_output_menu = menu_bar.addMenu("OutputLanguage")
        for lan_abbreviation, lan_full in get_languages().items():
            lan_string = f"{lan_abbreviation} ({lan_full})"
            language_input_menu.addAction(lan_string, self.language_input_menu_clicked)
            language_output_menu.addAction(lan_string, self.language_output_menu_clicked)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def language_input_menu_clicked(self):
        action = self.sender()
        self.subtitle_browser.input_language_select(action.text())
        # input changed so transcription changed
        self.start_new_transcription_thread()

    def language_output_menu_clicked(self):
        action = self.sender()
        self.subtitle_browser.output_language_select(action.text())
        # example of action.text() = 'zh-cn (chinese (simplified))'
        
    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_audio_file()
                return

            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.is_paused = False

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def open_audio_file(self):
        """Open a media file in a MediaPlayer
        """

        dialog_txt = "Choose Media File"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))


        while self.media.get_duration() < 0:
            continue
        self.media_duration = self.media.get_duration()

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux": # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows": # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        ### Load subtitles
        audio_file_path = pathlib.Path(filename[0])
        self.audio_file_path = audio_file_path
        subtitle_path = audio_file_path.with_suffix(".srt")
        if os.path.exists(subtitle_path):
            print("Loading subtitles at", subtitle_path)
            self.subtitle_browser.loaded_subtitles = list()
            self.subtitle_browser.load_subtitles(subtitle_path)
        # subtitles do not yet exist
        else:
            print("Automatically transcribing subtitles")
            # create the list of subtitles
            self.start_new_transcription_thread()

        self.play_pause()

    def start_new_transcription_thread(self):
        # stop old thread if it exists
        try:
            self.transcription_thread.stop()
        except Exception as exception:
            print(exception)
        
        # reset the loaded subtitles
        self.subtitle_browser.loaded_subtitles = list()
        self.transcription_progress_bar.setValue(0)
        # start a new thread
        self.transcription_thread = threading.Thread(target=start_live_transcription,
                                                        args=(  self.subtitle_browser.loaded_subtitles,
                                                                self.audio_file_path,
                                                                self.settings['model'],
                                                                self.subtitle_browser.input_language,
                                                                self.settings['model_dir']))
        self.transcription_thread.start()
        
    def set_volume(self, volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position()*100)

        self.positionslider.setValue(media_pos*10)

        try:
            # add subtitles
            time_in_ms = self.media_duration * self.mediaplayer.get_position()
            self.subtitle_browser.update_subtitles(time_in_ms)
            # update transcription progress bar
            if len(self.subtitle_browser.loaded_subtitles) > 0:
                last_caption = self.subtitle_browser.loaded_subtitles[-1]
                last_time = last_caption[1]
                if self.media_duration > 0:
                    relative_transcription_progress = round((last_time / self.media_duration)*100)
                    self.transcription_progress_bar.setValue(relative_transcription_progress)
        except AttributeError as error:
            print("AttributeError", error)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

