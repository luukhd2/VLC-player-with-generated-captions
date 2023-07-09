import platform
import os
import sys
import typing
import httpcore 


from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction, QTextCursor
from PyQt6.QtWidgets import QWidget

import vlc
from load_subtitles import load_srt_file, find_text_and_index_at_time
from translate import translate_text, get_translator

class LanguageSettingLabel(QtWidgets.QLabel):
    def __init__(self, in_lan, out_lan):
        super().__init__()
        self.setMaximumHeight(20)
        self.setMaximumWidth(200)
        self.set_language_option_text(in_lan, out_lan)

    def set_language_option_text(self, in_lan, out_lan):
        self.setText(f"{in_lan} -> {out_lan}")

class TranslationLabel(QtWidgets.QLabel):
    def __init__(self, player):
        super().__init__()
        self.setMaximumHeight(20)
        self.setMaximumWidth(200)
        #self.setStyleSheet("border: 1px solid white; background-color: rgba(0, 0, 0, 200);")
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        self.reset_translation_text()
        self.player = player 
        self.translator = get_translator()
        self.saved_words = set()
        
    def reset_translation_text(self):
        self.setText("")

    def set_translation_text(self, s, in_lan, out_lan):
        try:
            if len(self.s) < 1:
                return
            translation = self.player.subtitle_browser.translation_dict[s]
        except Exception as exception:
            print("Set trans text", exception)
            try:
                translation = translate_text(self.translator, text=s, src=in_lan, dest=out_lan)
            except Exception as different_error:
                print("\tSet trans text different: ", different_error)
                translation = None 
                
        if translation is None:
            return
        self.s = s
        self.translation = translation
        self.setText(f"{self.s} = {self.translation}")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            try:
                if self.player.audio_file_path is not None:
                    original_audio = self.player.audio_file_path
                else:
                    return
            except Exception as e:
                print("mouse event except", e)
                return
        
        save_file = original_audio.with_name(f"{original_audio.name}_words").with_suffix(".txt")
        if self.s not in self.saved_words:
            self.saved_words.add(self.s)
            with open(save_file, 'a') as open_save_file:

                open_save_file.write(f"{self.s},{self.translation}\n")


class SubtitleBrowser(QtWidgets.QTextEdit):
    def __init__(self, player, input_language, output_language):
        """
        input_language: short letter code (af, sq, am, ar, ....)
        output_language: short letter code (af, sq, am, ar, ....)
        """
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(60)
        self.setText("Welcome, please select an audio file...")

        # SETTINGS
        self.word_adjust_x = -25
        self.word_adjust_y = -25

        # VARS
        self.player = player
        self.input_language = input_language
        self.output_language = output_language
        self.loaded_subtitles = None
        self.subtitle_index = -1
        
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
            
            self.player.translation_label.set_translation_text(word_under_cursor, self.input_language,
                                                               self.output_language)


        return super().mouseMoveEvent(mouse_event)

    def load_subtitles(self, pathlib_to_srt_file):
        """
        """
        print("loading subtitles")
        self.subtitle_index = -1
        self.loaded_subtitles = load_srt_file(pathlib_to_srt_file)

    def update_subtitles(self, time_in_ms):
        """
        media_pos = time in seconds
        """
        if self.loaded_subtitles is not None:
            
            subtitle_text, subtitle_index = find_text_and_index_at_time(loaded_subtitles=self.loaded_subtitles,
                                                      time=time_in_ms, start_index=self.subtitle_index)
            # no subtitles were found. Either due to not existing (transcription still going) or not existing at this timepoint
            if subtitle_text is None and subtitle_index is None:
                self.subtitle_index = -1 # restart looking cause it hasnt been found from the starting point used
                self.setText("")
                self.update()
            # set the subtitles found
            elif self.subtitle_index != subtitle_index:
                self.subtitle_index = subtitle_index
                self.setText(subtitle_text)
                self.update()