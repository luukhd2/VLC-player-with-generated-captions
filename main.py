import platform
import os
import sys
import typing

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction, QTextCursor
from PyQt6.QtWidgets import QWidget
import vlc


from player import Player
from settings import SETTINGS


if __name__ == "__main__":
    """Entry point for our simple vlc player
    """
    APP = QtWidgets.QApplication(sys.argv)

    PLAYER = Player(SETTINGS)
    
    PLAYER.show()

    PLAYER.resize(640, 480)
    sys.exit(APP.exec())
