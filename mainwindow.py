from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QLabel, QFileDialog
from sketch import *

import os
import shutil

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Artmachine")
        self.setWindowIcon(QIcon("sprites/Icon.png"))
        self.setGeometry(500, 150, 1000, 700)

        self.fpath = ()
        self.spath = ()
        self.pixmap = None
        self.sketch = None

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = file_menu.addAction(QIcon("sprites/File.png"), "Open")
        open_action.setStatusTip("To open an existing image file")
        open_action.triggered.connect(self.open_file)

        save_action = file_menu.addAction(QIcon("sprites/Save.png"), "Save")
        save_action.setStatusTip("To save the current file")
        save_action.triggered.connect(self.save_file)

        quit_action = file_menu.addAction(QIcon("sprites/Close.png"), "Quit")
        quit_action.triggered.connect(self.quit_app)


        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Cut")
        edit_menu.addAction("Paste")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Contact")

        view_menu = menu_bar.addMenu("View")
        reset_action = view_menu.addAction(QIcon("sprites/Reset.png"), "Reset")
        reset_action.setStatusTip("Resets the image to fit the canvas")
        reset_action.triggered.connect(self.reset_canvas)

        tool_bar = QToolBar("Toolbar")
        tool_bar.setIconSize(QSize(24, 24))

        self.addToolBar(tool_bar)
        self.setStatusBar(QStatusBar(self))

        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)

        draw_action = QAction(QIcon("sprites/Draw.png"), "Draw", self)
        draw_action.setStatusTip("Starts converting the picture into drawing")
        draw_action.triggered.connect(self.draw_image)

        tool_bar.addAction(draw_action)
        tool_bar.addAction(reset_action)

        self.label = QLabel("Open an image", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(1, 1)

        self.setCentralWidget(self.label)

    def open_file(self):
        self.statusBar().showMessage("Openning a file...")
        self.fpath = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~') + "/Downloads/", "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
        self.reset_canvas()

    def save_file(self):
        self.statusBar().showMessage("Saving the file...")
        self.spath = QFileDialog.getSaveFileName(self, "Save File", os.path.dirname(self.fpath[0], ), "PNG Files (*.png)")
        shutil.copy(self.fpath[0], self.spath[0])

    def draw_image(self):
        if len(self.fpath) < 0:
            self.statusBar().showMessage("No image currently open!")

        else:
            self.sketch = sketchify(self.fpath[0])
            self.statusBar().showMessage("Image successfully converted")
            self.load_sketch()

    def load_sketch(self):
        fpath = list(self.fpath)
        fpath[0] = self.fpath[0] + "~"
        self.fpath = tuple(fpath)
        self.reset_canvas()

    def quit_app(self):
        self.app.quit()

    def reset_canvas(self):
        if len(self.fpath) == 0:
            self.statusBar().showMessage("No image currently open!")
        else:
            self.pixmap = QPixmap(self.fpath[0])
            self.canvas_aspect_ratio = self.width() / self.height()
            self.img_aspect_ratio = self.pixmap.width() / self.pixmap.height() 

            if self.img_aspect_ratio > self.canvas_aspect_ratio:
                self.pixmap = self.pixmap.scaledToWidth(self.width())
            else:
                self.pixmap = self.pixmap.scaledToHeight(self.height())

            self.label.setPixmap(self.pixmap)
            self.label.resize(self.width(), self.height())
            self.statusBar().showMessage("Canvas view reset")