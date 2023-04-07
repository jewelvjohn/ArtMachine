import os
import sys
import shutil

from rembg import remove
from PIL import Image, ImageOps, ImageFilter, ImageMath
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, QLabel, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Artmachine")
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setGeometry(500, 150, 1000, 700)

        self.canvas_margin = 100
        self.fpath = ()
        self.spath = ()
        self.cpath = "files\\temp.png"

        self.pixmap = None
        self.rem_index = 2

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = file_menu.addAction(QIcon("sprites\\File.png"), "Open")
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip("To open an existing image file")
        open_action.triggered.connect(self.open_file)

        save_action = file_menu.addAction(QIcon("sprites\\Save.png"), "Save")
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip("To save the current file")
        save_action.triggered.connect(self.save_file)

        quit_action = file_menu.addAction(QIcon("sprites\\Close.png"), "Quit")
        quit_action.setShortcut('Ctrl+W')
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

        reset_action = view_menu.addAction(QIcon("sprites\\Reset.png"), "Reset")
        reset_action.setShortcut('Ctrl+R')
        reset_action.setStatusTip("Resets the image to fit the canvas")
        reset_action.triggered.connect(self.reset_canvas)

        tool_bar = QToolBar("Toolbar")
        tool_bar.setIconSize(QSize(24, 24))

        self.addToolBar(tool_bar)
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet("QStatusBar {color: rgb(128, 128, 128);}")
        self.setStatusBar(status_bar)

        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)

        rembg_action = QAction(QIcon("sprites\\Remove.png"), "Remove Background", self)
        rembg_action.setShortcut('Ctrl+B')
        rembg_action.setStatusTip("Removes the background of an image")
        rembg_action.triggered.connect(self.rem_bg)

        draw_action = QAction(QIcon("sprites\\Draw.png"), "Draw", self)
        draw_action.setStatusTip("Starts converting the picture into drawing")
        draw_action.triggered.connect(self.draw_image)

        tool_bar.addAction(draw_action)
        tool_bar.addAction(rembg_action)
        tool_bar.addAction(reset_action)
        tool_bar.addSeparator()

        self.label = QLabel("Open an image(Ctrl + O)", self)
        self.label.setFont(QFont("Poppins", 24))
        self.label.setStyleSheet("QLabel {color: rgb(72, 72, 72);}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(1, 1)

        self.default_path = os.path.expanduser('~') + "\\Downloads\\"

        self.setCentralWidget(self.label)

    def open_file(self):
        self.drawn = False
        self.statusBar().showMessage("Openning a file..." ,3000)

        path = QFileDialog.getOpenFileName(self, "Open File", self.default_path, "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
        
        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.fpath = path
            shutil.copy(self.fpath[0], self.cpath)
            self.reset_canvas()

    def save_file(self):
        self.statusBar().showMessage("Saving the file..." ,3000)
        path = QFileDialog.getSaveFileName(self, "Save File", os.path.dirname(self.fpath[0], ), "PNG Files (*.png)")

        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.spath = path
            shutil.copy(self.cpath, self.spath[0])
            

    def draw_image(self):
        if len(self.fpath) < 0:
            self.statusBar().showMessage("No image currently open!" ,3000)
        else:
            if self.drawn:
                self.statusBar().showMessage("Image already drawn!" ,3000)
            else:
                self.drawn = True

                img = Image.open(self.cpath)
                img_grey = img.convert('L')
                img_blur = img_grey.filter(ImageFilter.GaussianBlur(radius = 2.5))
                image = ImageMath.eval("convert(a * 256/b, 'L')", a=img_grey, b=img_blur)

                image.save(self.cpath)

                self.statusBar().showMessage("Image successfully converted" ,3000)
                self.reset_canvas()

    def rem_bg(self):
        input = Image.open(self.cpath)
        output = remove(input)
        output.save(self.cpath)

        if self.rem_index == 0:
            width, height = input.size
            white = Image.new("RGB", (height, width), (255, 255, 255))

            white.paste(output, (0,0), mask = output)
            white.save(self.cpath)
            
        elif self.rem_index == 1:
            width, height = input.size
            white = Image.new("RGB", (height, width), (0, 0, 0))

            white.paste(output, (0,0), mask = output)
            white.save(self.cpath)

        self.reset_canvas()

    def reset_canvas(self):
        if len(self.fpath) == 0:
            self.statusBar().showMessage("No image currently open!" ,3000)
        else:
            self.pixmap = QPixmap(self.cpath)
            self.canvas_aspect_ratio = self.width() / self.height()
            self.img_aspect_ratio = self.pixmap.width() / self.pixmap.height() 

            if self.img_aspect_ratio > self.canvas_aspect_ratio:
                self.pixmap = self.pixmap.scaledToWidth(self.width() - self.canvas_margin // 4)
            else:
                self.pixmap = self.pixmap.scaledToHeight(self.height() - self.canvas_margin)

            self.label.setPixmap(self.pixmap)
            self.label.resize(self.width(), self.height())
            self.statusBar().showMessage("Canvas view reset" ,3000)

    def quit_app(self):
        self.app.quit()

app = QApplication(sys.argv)
window = MainWindow(app)
window.setStyleSheet("QMainWindow {background: rgb(25, 25, 25);}")
window.show()
app.exec()