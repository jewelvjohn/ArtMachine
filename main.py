import os
import sys
import shutil
import base64

from io import BytesIO 

from rembg import remove
from PIL import Image, ImageOps, ImageFilter, ImageMath, ImageEnhance

from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import (QAction, QIcon, QPixmap, 
                           QFont, QDoubleValidator, 
                           QValidator, QBrush, QColor)
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QStatusBar, 
                               QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLineEdit, QSlider, QGraphicsView, 
                               QGraphicsScene, QGraphicsPixmapItem, QFrame)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Artmachine")
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setStyleSheet("QMainWindow {background: rgb(50, 50, 50);}")
        self.setGeometry(500, 150, 1000, 700)

        self.viewer = Viewport(self)
        
        self.default_path = "X:\\Documents\\Assets\\Stuff\\References"
        self.cache_path = "files\\data.png"

        self.open_path = ()
        self.save_path = ()

        self.canvas_margin = int(100)

        self.uStack = []
        self.rStack = []

        self.pixmap = None
        self.rem_index = int(2)
        self.img_contrast = float(1.5)
        self.img_brightness = float(1.5)

        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
                                QMenuBar {
                                    background-color: #323232;
                                    color: #ffffff;
                                    font-size: 16px;
                                }
                                QMenuBar::item {
                                    background-color: transparent;
                                    padding: 4px 10px;
                                }
                                QMenuBar::item:selected {
                                    background-color: #505050;
                                }
                                QMenu {
                                    background-color: #2f2f2f;
                                    border: 1px solid #3a3a3a;
                                }
                                QMenu::item {
                                    color: #ffffff;
                                    padding: 5px 20px;
                                }
                                QMenu::item:selected {
                                    background-color: #363636;
                                }
                            """)

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        image_menu = menu_bar.addMenu("Image")
        filter_menu = menu_bar.addMenu("Filter")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        open_action = file_menu.addAction(QIcon("sprites\\File.png"), "Open")
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip("To open an existing image file")
        open_action.triggered.connect(self.openFile)

        save_action = file_menu.addAction(QIcon("sprites\\Save.png"), "Save")
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip("To save the current file")
        save_action.triggered.connect(self.saveFile)

        quit_action = file_menu.addAction(QIcon("sprites\\Close.png"), "Quit")
        quit_action.setShortcut('Ctrl+W')
        quit_action.triggered.connect(self.quitApp)

        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setStatusTip("Undo the last changes")
        undo_action.triggered.connect(self.undoCommand)

        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut('Ctrl+Shift+Z')
        redo_action.setStatusTip("Redo the undo changes")
        redo_action.triggered.connect(self.redoCommand)

        settings_action = edit_menu.addAction(QIcon("sprites\\Settings.png"), "Settings")
        settings_action.setStatusTip("Enter application settings")

        gray_action = image_menu.addAction("Grayscale")
        gray_action.setStatusTip("Converts the image into Grayscale")
        gray_action.triggered.connect(self.imageGray)

        invert_action = image_menu.addAction("Invert")
        invert_action.setStatusTip("Inverts the image colors")
        invert_action.triggered.connect(self.imageInvert)

        contrast_action = image_menu.addAction("Contrast")
        contrast_action.setStatusTip("Always you to modify the image contrast")
        contrast_action.triggered.connect(self.contrastDialog)

        brightness_action = image_menu.addAction("Brightness")
        brightness_action.setStatusTip("Always you to modify the image brightness")
        brightness_action.triggered.connect(self.brightnessDialog)

        draw_action = filter_menu.addAction(QIcon("sprites\\Draw.png"), "Draw")
        draw_action.setStatusTip("Applies a drawing filter to the picture")
        draw_action.triggered.connect(self.drawImage)

        rembg_action = filter_menu.addAction(QIcon("sprites\\Remove.png"), "Remove Background")
        rembg_action.setStatusTip("Tries to remove the background of the picture")
        rembg_action.triggered.connect(self.removeBackground)
        
        reset_action = view_menu.addAction(QIcon("sprites\\Reset.png"), "Reset")
        reset_action.setShortcut('Ctrl+R')
        reset_action.setStatusTip("Resets the image to fit the canvas")
        reset_action.triggered.connect(self.setImage)

        about_action = help_menu.addAction("About")

        tool_bar = QToolBar("Toolbar")
        tool_bar.setIconSize(QSize(30, 30))

        self.addToolBar(Qt.LeftToolBarArea, tool_bar)
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet("QStatusBar {color: rgb(128, 128, 128);}")
        self.setStatusBar(status_bar)

        tool_bar.addAction(open_action)
        tool_bar.addAction(save_action)


        self.setCentralWidget(self.viewer)

    def addCommand(self):
        with open(self.cache_path, "rb") as file:
            img = base64.b64encode(file.read())
            self.uStack.append(base64.b64decode(img))

    def undoCommand(self):
        if len(self.uStack) > 1:
            self.rStack.append(self.uStack.pop())
            self.setImage()
        else:
            self.statusBar().showMessage("Undo not available" ,3000)

    def redoCommand(self):
        if len(self.rStack) > 0:
            self.uStack.append(self.rStack.pop())
            self.setImage()
        else:
            self.statusBar().showMessage("Redo not available" ,3000)

    def openFile(self):
        self.statusBar().showMessage("Openning a file..." ,3000)

        path = QFileDialog.getOpenFileName(self, "Open File", self.default_path, "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
        
        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.open_path = path
            shutil.copy(self.open_path[0], self.cache_path)

            self.addCommand()          
            self.setImage()

    def saveFile(self):
        self.statusBar().showMessage("Saving the file..." ,3000)
        path = QFileDialog.getSaveFileName(self, "Save File", os.path.dirname(self.open_path[0], ), "PNG Files (*.png)")

        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.save_path = path
            shutil.copy(self.cache_path, self.save_path[0])

    def imageGray(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            output = img.convert('L')
            output.save(self.cache_path)
            
            self.statusBar().showMessage("Image adjustment successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def imageInvert(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            output = ImageOps.invert(img)
            output.save(self.cache_path)
            
            self.statusBar().showMessage("Image adjustment successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def imageContrast(self):
            img = Image.open(self.cache_path)
            enhancer = ImageEnhance.Contrast(img)
            output = enhancer.enhance(self.img_contrast)
            output.save(self.cache_path)

            self.statusBar().showMessage("Image contrast changed" ,3000)
            self.addCommand()
            self.setImage()

    def imageBrightness(self):
            img = Image.open(self.cache_path)
            enhancer = ImageEnhance.Brightness(img)
            output = enhancer.enhance(self.img_brightness)

            output.save(self.cache_path)

            self.statusBar().showMessage("Image brightness changed" ,3000)
            self.addCommand()
            self.setImage()

    def contrastDialog(self):
        if self.viewer.hasPhoto():
            contrast = ApplicationDialogs()
            i, ok = contrast.sliderDialog(50, 0, 100, "Set Contrast", 300, 100, True)

            if ok:
                self.img_contrast = i/50
                self.imageContrast()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def brightnessDialog(self):
        if self.viewer.hasPhoto():
            brightness = ApplicationDialogs()
            i, ok = brightness.sliderDialog(50, 0, 100, "Set Brightness", 300, 100, True)

            if ok:
                self.img_brightness = i/50
                self.imageBrightness()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)
            
    def drawImage(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            img_grey = img.convert('L')
            img_blur = img_grey.filter(ImageFilter.GaussianBlur(radius = 2.5))
            image = ImageMath.eval("convert(a * 256/b, 'L')", a=img_grey, b=img_blur)

            image.save(self.cache_path)

            self.statusBar().showMessage("Image filter successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def removeBackground(self):
        if self.viewer.hasPhoto():
            input = Image.open(self.cache_path)
            output = remove(input)
            output.save(self.cache_path)

            if self.rem_index == 0:
                width, height = input.size
                white = Image.new("RGB", (height, width), (255, 255, 255))

                white.paste(output, (0,0), mask = output)
                white.save(self.cache_path)
                
            elif self.rem_index == 1:
                width, height = input.size
                white = Image.new("RGB", (height, width), (0, 0, 0))

                white.paste(output, (0,0), mask = output)
                white.save(self.cache_path)

            self.statusBar().showMessage("Image filter successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)


    def setImage(self):
        im_file = BytesIO(self.uStack[-1])
        img = Image.open(im_file)
        img.save(self.cache_path)
        self.viewer.setPhoto(QPixmap(self.cache_path))

    def quitApp(self):
        self.app.quit()

    def closeEvent(self, event):
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)

class ApplicationDialogs(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QDialog {background: rgb(25, 25, 25);}")

    def sliderDialog(self, initialValue, minimumValue, maximumValue, windowTitle, windowWidth, windowHeight, modal):
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setWindowTitle(windowTitle)
        self.setGeometry(700, 300, windowWidth, windowHeight)
        self.setFixedSize(QSize(windowWidth, windowHeight))
        self.setModal(modal)

        self.slider = QSlider(Qt.Horizontal)
        self.line = QLineEdit()

        self.initialValue = initialValue

        self.slider.setMinimum(minimumValue)
        self.slider.setMaximum(maximumValue)
        self.slider.setValue(initialValue)
        self.slider.valueChanged.connect(self.changeValue)

        self.line.setMaximumWidth(40)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setText(str(initialValue))
        self.line.editingFinished.connect(self.integerValidating)

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.setValue)

        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.line)

        button_layout.addWidget(self.ok_button)

        layout.addLayout(slider_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.show()
        self.exec()

        if self.return_value:
            return self.slider.value(), bool(True)
        
        return 0, False
        
    def integerValidating(self):
        validation_rule = QDoubleValidator(self.slider.minimum(), self.slider.maximum(), 0)
        if validation_rule.validate(self.line.text(), 3)[0] == QValidator.Acceptable:
            self.line.setFocus()
            self.slider.setValue(int(self.line.text()))
        else:
            self.line.setText(str(self.initialValue))
            self.slider.setValue(int(self.line.text()))

    def changeValue(self):
        self.line.setText(str(self.slider.value()))

    def setValue(self):
        self.return_value = True
        self.accept()

class Viewport(QGraphicsView):
    def __init__(self, parent):
        super(Viewport, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        super(Viewport, self).mousePressEvent(event)
    
app = QApplication(sys.argv)
window = MainWindow(app)
window.show()
app.exec()