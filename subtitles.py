import platform
import os
import sys
import typing

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction, QTextCursor
from PyQt6.QtWidgets import QWidget
import vlc


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
    def __init__(self, player):
        super().__init__()
        self.setMaximumHeight(40)
        self.setText("test if the words are shown as separate or not")

        # SETTINGS
        self.word_adjust_x = -25
        self.word_adjust_y = -25

        self.player = player

    def mouseMoveEvent(self, mouse_event) -> None:
        """
        https://stackoverflow.com/questions/69380860/wordundercursor-not-working-as-it-should-word-being-detected-when-not-on-top-of
        """
        # if cursor hovering over the subtitlebrowser
        if self.underMouse():
            print("under")
            text_cursor = self.cursorForPosition(mouse_event.pos())
            text_cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            word_under_cursor = text_cursor.selectedText()
            
            self.player.translation_label.set_translation_text(word_under_cursor)

            # relative_x = mouse_event.pos().x()
            # relative_y = mouse_event.pos().y()
            # global_pos = self.mapFromGlobal(QtCore.QPoint(0, 0))
            # word_x = -1*global_pos.x() + relative_x
            # word_y = -1*global_pos.y() + relative_y
            # self.translation_label.setGeometry(word_x+self.word_adjust_x, word_y+self.word_adjust_y, 5, 5)
            # self.translation_label.setText(word_under_cursor)
            # self.translation_label.adjustSize()
            # self.translation_label.show()


        return super().mouseMoveEvent(mouse_event)

