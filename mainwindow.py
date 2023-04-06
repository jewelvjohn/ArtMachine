from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QLabel, QFileDialog, QLayout

import os

class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Artmachine")
        self.setWindowIcon(QIcon("sprites/Icon.png"))
        self.setGeometry(500, 150, 1000, 700)

        self.fpath = ()

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

        self.label = QLabel("Open an image", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(1, 1)

        self.setCentralWidget(self.label)

    def open_file(self):

        self.statusBar().showMessage("Openning a file...")

        self.fpath = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~') + "/Downloads/", "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
        pixmap = QPixmap(self.fpath[0])

        self.img_aspect_ratio = pixmap.width() / pixmap.height() 

        if self.img_aspect_ratio < 1:
            pixmap = pixmap.scaledToHeight(self.height(), Qt.FastTransformation)
            self.statusBar().showMessage("Height scale")
        else:
            pixmap = pixmap.scaledToWidth(self.width(), Qt.FastTransformation)
            self.statusBar().showMessage("width scale")

        #self.statusBar().showMessage("The aspect ratio is "+str(self.img_aspect_ratio))
        self.label.setPixmap(pixmap)

    def save_file(self):
        self.statusBar().showMessage("Saving the file...")

    def draw_image(self):
        self.statusBar().showMessage("Converting the image...")

    def quit_app(self):
        self.app.quit()

    def reset_canvas(self):
        self.statusBar().showMessage("Canvas view Reset")