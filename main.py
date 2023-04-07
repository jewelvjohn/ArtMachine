import os
import cv2
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, QLabel, QFileDialog, QCheckBox

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
        self.cpath = ()
        self.pixmap = None

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

        remove_bg = QCheckBox()

        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)

        draw_action = QAction(QIcon("sprites\\Draw.png"), "Draw", self)
        draw_action.setStatusTip("Starts converting the picture into drawing")
        draw_action.triggered.connect(self.draw_image)

        tool_bar.addAction(draw_action)
        tool_bar.addAction(reset_action)

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
            self.cpath = path
            self.reset_canvas()

    def save_file(self):
        self.statusBar().showMessage("Saving the file..." ,3000)
        path = QFileDialog.getSaveFileName(self, "Save File", os.path.dirname(self.fpath[0], ), "PNG Files (*.png)")

        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.spath = path
            cv2.imwrite(self.spath[0], self.sketch)
            

    def draw_image(self):
        if len(self.fpath) < 0:
            self.statusBar().showMessage("No image currently open!" ,3000)
        else:
            if self.drawn:
                self.statusBar().showMessage("Image already drawn!" ,3000)
            else:
                self.drawn = True
                image = cv2.imread(self.fpath[0])

                grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                invert = cv2.bitwise_not(grey_img)
                blur = cv2.GaussianBlur(invert, (21,21), 0)
                inverted_blur = cv2.bitwise_not(blur)
                self.sketch = cv2.divide(grey_img, inverted_blur, scale=256.0)

                cv2.imwrite("files\\temp.png", self.sketch)

                self.statusBar().showMessage("Image successfully converted" ,3000)
                self.cpath = "files\\temp.png"
                self.reset_canvas()

    def reset_canvas(self):
        if len(self.cpath) == 0:
            self.statusBar().showMessage("No image currently open!" ,3000)
        else:
            self.pixmap = QPixmap(self.cpath[0])
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