import platform
import os
import sys
import typing

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction, QTextCursor
from PyQt6.QtWidgets import QWidget

import vlc
from load_subtitles import load_srt_file, find_text_and_index_at_time


class LanguageSettingLabel(QtWidgets.QLabel):
    def __init__(self, in_lan, out_lan):
        super().__init__()
        self.setMaximumHeight(20)
        self.setMaximumWidth(200)
        self.set_language_option_text(in_lan, out_lan)

    def set_language_option_text(self, in_lan, out_lan):
        self.setText(f"{in_lan} -> {out_lan}")

class TranslationLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(20)
        self.setMaximumWidth(200)
        #self.setStyleSheet("border: 1px solid white; background-color: rgba(0, 0, 0, 200);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        self.set_translation_text(" ")

    def set_translation_text(self, s):
        self.setText(s)

class SubtitleBrowser(QtWidgets.QTextEdit):
    def __init__(self, player, input_language, output_language):
        """
        input_language: short letter code (af, sq, am, ar, ....)
        output_language: short letter code (af, sq, am, ar, ....)
        """
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(60)
        self.setText("test 123 test 123")

        # SETTINGS
        self.word_adjust_x = -25
        self.word_adjust_y = -25

        # VARS
        self.player = player
        self.input_language = input_language
        self.output_language = output_language
        self.loaded_subtitles = None

    def input_language_select(self, action_text):
        """
        example of action.text() = 'bs (bosnian)'
        """
        abbreviation, full_text = action_text.split(" ", 1)
        self.input_language = abbreviation
        # update language setting label
        self.player.language_setting_label.set_language_option_text(self.input_language, self.output_language)

    def output_language_select(self, action_text):
        """
        example of action_text = 'zh-cn (chinese (simplified))'
        """
        abbreviation, full_text = action_text.split(" ", 1)
        self.output_language = abbreviation
        self.player.language_setting_label.set_language_option_text(self.input_language, self.output_language)

    def mouseMoveEvent(self, mouse_event) -> None:
        """
        https://stackoverflow.com/questions/69380860/wordundercursor-not-working-as-it-should-word-being-detected-when-not-on-top-of
        """
        # if cursor hovering over the subtitlebrowser
        if self.underMouse():
            text_cursor = self.cursorForPosition(mouse_event.pos())
            text_cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            word_under_cursor = text_cursor.selectedText()
            
            self.player.translation_label.set_translation_text(word_under_cursor)


        return super().mouseMoveEvent(mouse_event)

    def load_subtitles(self, pathlib_to_srt_file):
        """
        """
        print("loading subtitles")
        self.subtitle_index = -1
        self.loaded_subtitles = load_srt_file(pathlib_to_srt_file)
        print(self.loaded_subtitles)

    def update_subtitles(self, time_in_ms):
        """
        media_pos = time in seconds
        """
        if self.loaded_subtitles is not None:
            
            subtitle_text, subtitle_index = find_text_and_index_at_time(loaded_subtitles=self.loaded_subtitles,
                                                      time=time_in_ms, start_index=self.subtitle_index)
            if self.subtitle_index != subtitle_index:
                self.subtitle_index = subtitle_index
                self.setText(subtitle_text)
                self.update()