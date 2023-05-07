import os
import sys
import shutil
import base64

from io import BytesIO 

from rembg import remove
from PIL import Image, ImageOps, ImageFilter, ImageMath, ImageEnhance

from PySide6.QtCore import Qt, QSize, QPointF, QRectF
from PySide6.QtGui import (QAction, QIcon, QPixmap, 
                           QFont, QDoubleValidator, 
                           QValidator, QBrush, QColor,
                           QFontDatabase, QPen, QMouseEvent)
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QStatusBar, 
                               QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLineEdit, QSlider, QGraphicsView, 
                               QGraphicsScene, QGraphicsPixmapItem, QFrame, 
                               QRadioButton, QGroupBox, QGraphicsRectItem, 
                               QLabel)

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Artmachine")
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setStyleSheet("QMainWindow {background: rgb(50, 50, 50);}")
        self.setGeometry(500, 150, 1000, 700)

        tool_bar = QToolBar("Toolbar")
        status_bar = QStatusBar(self)
        menu_bar = self.menuBar()

        self.viewer = Viewport(self)
        
        self.default_path = os.path.expanduser("~")+"\\Downloads\\"
        self.cache_path = "files\\data.png"

        self.open_path = ()
        self.save_path = ()

        self.canvas_margin = int(100)

        self.uStack = []
        self.rStack = []

        self.pixmap = None
        self.gamma = float(1)
        self.rem_index = int(2)
        self.img_contrast = float(1.5)
        self.img_brightness = float(1.5)

        tool_bar.setIconSize(QSize(32, 32))
        tool_bar.setStyleSheet("""
                                QToolBar {
                                    background-color: #323232;
                                    border: none;
                                }
                                QToolButton {
                                    background-color: transparent;
                                    color: #CCCCCC;
                                    border: none;
                                    padding: 6px 6px;
                                    font-size: 16px;
                                }
                                QToolButton:hover {
                                    background-color: #505050;
                                }
                                QToolButton:pressed {
                                    background-color: #727272;
                                }
                            """)
        
        status_bar.setStyleSheet("QStatusBar {color: rgb(128, 128, 128);}")

        menu_bar.setStyleSheet("""
                                QMenuBar {
                                    background-color: #323232;
                                    color: #CCCCCC;
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
                                    color: #CCCCCC;
                                    padding: 5px 20px;
                                }
                                QMenu::item:selected {
                                    background-color: #363636;
                                }
                            """)

        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        transform_menu = menu_bar.addMenu("Transform")
        image_menu = menu_bar.addMenu("Image")
        filter_menu = menu_bar.addMenu("Filter")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        open_action = file_menu.addAction(QIcon("sprites\\File.png"), "Open")
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip("To open an existing image file")
        open_action.triggered.connect(self.openFileDialog)

        save_action = file_menu.addAction(QIcon("sprites\\Save.png"), "Save")
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip("To save the current file")
        save_action.triggered.connect(self.saveFile)

        quit_action = file_menu.addAction(QIcon("sprites\\Close.png"), "Quit")
        quit_action.setShortcut('Ctrl+W')
        quit_action.triggered.connect(self.quitApp)

        undo_action = edit_menu.addAction(QIcon("sprites\\Undo.png"),"Undo")
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setStatusTip("Undo the last changes")
        undo_action.triggered.connect(self.undoCommand)

        redo_action = edit_menu.addAction(QIcon("sprites\\Redo.png"),"Redo")
        redo_action.setShortcut('Ctrl+Shift+Z')
        redo_action.setStatusTip("Redo the undo changes")
        redo_action.triggered.connect(self.redoCommand)

        settings_action = edit_menu.addAction(QIcon("sprites\\Settings.png"), "Settings")
        settings_action.setStatusTip("Enter application settings")

        rotate_clockwise_action = transform_menu.addAction(QIcon("sprites\\Forward.png"), "Rotate 90 Clockwise") 
        rotate_clockwise_action.setStatusTip("Rotate the image 90 clockwise")
        rotate_clockwise_action.triggered.connect(self.rotateClockwise)

        rotate_anticlockwise_action = transform_menu.addAction(QIcon("sprites\\Backward.png"), "Rotate 90 Anti-Clockwise")
        rotate_anticlockwise_action.setStatusTip("Rotate the image 90 Anti-Clockwise")
        rotate_anticlockwise_action.triggered.connect(self.rotateAnticlockwise)

        flip_horizontal_action = transform_menu.addAction(QIcon("sprites\\Horizontal.png"), "Flip Horizontal") 
        flip_horizontal_action.setStatusTip("Flip the image horizontally")
        flip_horizontal_action.triggered.connect(self.flipHorizontal)

        flip_verical_action = transform_menu.addAction(QIcon("sprites\\Vertical.png"), "Flip Vertical")
        flip_verical_action.setStatusTip("Flip the image vertically")
        flip_verical_action.triggered.connect(self.flipVertical)

        crop_image_action = transform_menu.addAction(QIcon("sprites\\Crop.png"), "Crop Image")
        crop_image_action.setStatusTip("Dialog for cropping the image")
        crop_image_action.triggered.connect(self.cropDialog)

        gray_action = image_menu.addAction("Grayscale")
        gray_action.setStatusTip("Converts the image into Grayscale")
        gray_action.triggered.connect(self.imageGray)

        invert_action = image_menu.addAction("Invert")
        invert_action.setStatusTip("Inverts the image colors")
        invert_action.triggered.connect(self.imageInvert)

        contrast_action = image_menu.addAction("Contrast")
        contrast_action.setStatusTip("Allows you to modify the image contrast")
        contrast_action.triggered.connect(self.contrastDialog)

        brightness_action = image_menu.addAction("Brightness")
        brightness_action.setStatusTip("Allows you to modify the image brightness")
        brightness_action.triggered.connect(self.brightnessDialog)

        draw_action = filter_menu.addAction(QIcon("sprites\\Pencil.png"), "Draw")
        draw_action.setStatusTip("Applies a drawing filter to the picture")
        draw_action.triggered.connect(self.drawImage)

        rembg_action = filter_menu.addAction(QIcon("sprites\\Remove.png"), "Remove Background")
        rembg_action.setStatusTip("Tries to remove the background of the picture")
        rembg_action.triggered.connect(self.rem_bgDialog)

        zoomIn_action = view_menu.addAction(QIcon("sprites\\ZoomIn.png"), "Zoom In")
        zoomIn_action.setShortcut('Ctrl+]')
        zoomIn_action.setStatusTip("Zooms into the canvas view")
        zoomIn_action.triggered.connect(self.viewer.zoomIn)

        zoomOut_action = view_menu.addAction(QIcon("sprites\\ZoomOut.png"), "Zoom Out")
        zoomOut_action.setShortcut('Ctrl+[')
        zoomOut_action.setStatusTip("Zooms out of the canvas view")
        zoomOut_action.triggered.connect(self.viewer.zoomOut)
        
        reset_action = view_menu.addAction(QIcon("sprites\\Reset.png"), "Reset")
        reset_action.setShortcut('Ctrl+R')
        reset_action.setStatusTip("Resets the image to fit the canvas")
        reset_action.triggered.connect(self.setImage)

        about_action = help_menu.addAction("About")

        self.addToolBar(Qt.RightToolBarArea, tool_bar)
        self.setStatusBar(status_bar)

        tool_bar.addAction(crop_image_action)
        tool_bar.addAction(draw_action)
        tool_bar.addAction(rembg_action)

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

    def openFileDialog(self):
        self.statusBar().showMessage("Openning a file..." ,3000)

        path = QFileDialog.getOpenFileName(self, "Open File", self.default_path, "All Files (*);; PNG Files (*.png);; JPG Files (*.jpg)")
        
        if path[0] == "":
            self.statusBar().showMessage("File dialog closed" ,3000)
        else:
            self.open_path = path
            self.openFile(self.open_path[0])

    def openFile(self, path):
        shutil.copy(path, self.cache_path)

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

            if self.rem_index == 1:
                height, width = input.size
                white = Image.new("RGB", (height, width), (255, 255, 255))

                white.paste(output, (0,0), mask = output)
                white.save(self.cache_path)
                
            elif self.rem_index == 2:
                height, width = input.size
                white = Image.new("RGB", (height, width), (0, 0, 0))

                white.paste(output, (0,0), mask = output)
                white.save(self.cache_path)

            self.statusBar().showMessage("Image filter successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def contrastDialog(self):
        if self.viewer.hasPhoto():
            contrast = ApplicationDialogs()
            i, ok = contrast.sliderDialog(50, 0, 100, "Set Contrast", 300, 120, True)

            if ok:
                self.img_contrast = i/50
                self.imageContrast()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def brightnessDialog(self):
        if self.viewer.hasPhoto():
            brightness = ApplicationDialogs()
            i, ok = brightness.sliderDialog(50, 0, 100, "Set Brightness", 300, 120, True)

            if ok:
                self.img_brightness = i/50
                self.imageBrightness()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def rem_bgDialog(self):
        if self.viewer.hasPhoto():
            rem_bg = ApplicationDialogs()
            buttonNames = [ "Trasparent", "White", "Black"]
            i, ok = rem_bg.radioDialog("Choose background color", 3, buttonNames, "Remove Background", 300, 200, True)

            if ok:
                self.rem_index = i
                self.removeBackground()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def cropDialog(self):
        if self.viewer.hasPhoto():
            crop_widget = CropWidget()
            cropped = crop_widget.callCropDialog("Crop Image", 900, 600, True)

            if cropped:
                self.statusBar().showMessage("Image successfully cropped" ,3000)
                self.addCommand()
                self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def rotateClockwise(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            rotated_img = img.rotate(-90)

            rotated_img.save(self.cache_path)

            self.statusBar().showMessage("Image rotation successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def rotateAnticlockwise(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            rotated_img = img.rotate(90)

            rotated_img.save(self.cache_path)

            self.statusBar().showMessage("Image rotation successfully applied" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def flipHorizontal(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)

            flipped_img.save(self.cache_path)

            self.statusBar().showMessage("Image successfully flipped" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def flipVertical(self):
        if self.viewer.hasPhoto():
            img = Image.open(self.cache_path)
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)

            flipped_img.save(self.cache_path)

            self.statusBar().showMessage("Image successfully flipped" ,3000)
            self.addCommand()
            self.setImage()

        else:
            self.statusBar().showMessage("No image currently open!" ,3000)

    def cropTool(self):
        self.editMode = True

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
        self.ok_button = QPushButton("Ok")

        self.initialValue = initialValue

        self.slider.setMinimum(minimumValue)
        self.slider.setMaximum(maximumValue)
        self.slider.setValue(initialValue)
        self.slider.valueChanged.connect(self.changeValue)

        self.line.setMaximumWidth(40)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setText(str(initialValue))
        self.line.editingFinished.connect(self.integerValidating)

        self.ok_button.clicked.connect(self.setSliderValue)

        self.slider.setStyleSheet(
                                    "QSlider::groove:horizontal {"
                                    "height: 8px;"
                                    "background: #404040;"
                                    "border-radius: 8px;}"

                                    "QSlider::handle:horizontal {"
                                    "background-color: #929292;"
                                    "width: 20px;"
                                    "height: 20px;"
                                    "margin-top: -6px;"
                                    "margin-bottom: -6px;"
                                    "border-radius: 20px;}"
                                )
        
        self.line.setStyleSheet(
                                    "background-color: #404040; border: none; color: #CCCCCC; border-radius: 20px;"
                                )
        
        self.ok_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }
                                        """
                                    )

        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.line)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(slider_layout)
        layout.addSpacing(5)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.return_value = False

        self.show()
        self.exec()

        if self.return_value:
            return self.slider.value(), True
        else:
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

    def setSliderValue(self):
        self.return_value = True
        self.accept()

    def radioDialog(self, caption, count, buttonNames, windowTitle, windowWidth, windowHeight, modal):
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setWindowTitle(windowTitle)
        self.setGeometry(700, 300, windowWidth, windowHeight)
        self.setFixedSize(QSize(windowWidth, windowHeight))
        self.setModal(modal)

        self.radioValue = 0
        self.radioCount = count

        self.radioButtons = []
        radioLayout = QVBoxLayout()
        self.radioButtonGroup = QGroupBox(caption)
        radioLayout.addSpacing(15)

        for i in range(0, count):
            radioButton = QRadioButton(buttonNames[i])
            radioButton.setStyleSheet(
                                        """
                                        QRadioButton {
                                            color: #CCCCCC;
                                        }
                                        """
                                    )
            self.radioButtons.append(radioButton)
            radioLayout.addWidget(self.radioButtons[i])
        self.radioButtons[0].setChecked(True)

        self.radioButtonGroup.setLayout(radioLayout)
        self.radioButtonGroup.setStyleSheet(
                                                """
                                                QGroupBox {
                                                    color: #CCCCCC;
                                                    border: 2px solid #CCCCCC
                                                }
                                                """
                                            )

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.setRadioValue)
        self.ok_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }
                                        """
                                    )
        
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)

        layout.addWidget(self.radioButtonGroup)
        layout.addSpacing(5)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.return_value = False

        self.show()
        self.exec()

        if self.return_value:
            return self.radioValue, True
        else:
            return 0, False

    def setRadioValue(self):
        self.return_value = True

        for i in range(0, self.radioCount):
            if self.radioButtons[i].isChecked():
                self.radioValue = i

        self.accept()

class Viewport(QGraphicsView):
    def __init__(self, parent):
        super(Viewport, self).__init__(parent)
        pixmap = QPixmap("files\\Openning.png")
        pixmap = pixmap.scaled(pixmap.width()/1.6, pixmap.height()/1.6, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._photo.setPixmap(pixmap)
        self._scene.addItem(self._photo)

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.setAcceptDrops(True)

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
            self._size = self.size() 
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                self.zoomFactor = 1.1
                self._zoom += 1
            else:
                self.zoomFactor = 0.9
                self._zoom -= 1
            
            self.zoomCheck()


    def zoomIn(self):
        self.zoomFactor = 1.1
        self._zoom += 1
        self.zoomCheck()

    def zoomOut(self):
        self.zoomFactor = 0.9
        self._zoom -= 1
        self.zoomCheck()

    def zoomCheck(self):
        if self._zoom > 0:
            if self._zoom < 20:
                self.scale(self.zoomFactor, self.zoomFactor)
            else:
                self._zoom = 20
        elif self._zoom == 0:
            self.fitInView()
        else:
            if self._zoom > -20:
                self.scale(self.zoomFactor, self.zoomFactor)
            else:
                self._zoom = -20

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event: QMouseEvent):
        super(Viewport, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            # Get the file path of the dropped image
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.parent().openFile(file_path)
            self.setAcceptDrops(False)
        else:
            event.ignore()
    
class CropView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.rect_item = None
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)


    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.pixmap_item.setPixmap(pixmap)
            self._size = self.size() 
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self.pixmap_item.setPixmap(QPixmap())
        self.fitInView()

    def fitInView(self, scale=True):
        rect = QRectF(self.pixmap_item.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)

            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                            viewrect.height() / scenerect.height())
            self.scale(factor, factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            
            pos = self.mapToScene(event.position().toPoint())

            self.rect_item = QGraphicsRectItem(pos.x(), pos.y(), 0, 0)
            pen = QPen(QColor(255, 255, 255, 0))
            pen.setWidth(2)
            self.rect_item.setPen(pen)
            brush = QBrush(QColor(255, 255, 255, 130))
            self.rect_item.setBrush(brush)
            self.scene.addItem(self.rect_item)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.rect_item is not None:
            rect = self.rect_item.rect()

            rect.setBottomRight(self.mapToScene(event.position().toPoint()))
            self.rect_item.setRect(rect.normalized())
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        if self.rect_item is not None:
            pen = QPen(Qt.white)
            pen.setWidth(2)
            self.rect_item.setPen(pen)
            brush = QBrush(QColor(255, 255, 255, 50))
            self.rect_item.setBrush(brush)

            self.parent().crop_button.setEnabled(True)
            self.parent().reset_button.setEnabled(True)

    def cropImage(self):
        rect = self.rect_item.rect().toRect()
        cropped_pixmap = self.pixmap_item.pixmap().copy(rect)
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(cropped_pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(cropped_pixmap.rect()))
        self.rect_item = None

        self.parent().crop_button.setEnabled(False)
        self.parent().reset_button.setEnabled(False)

    def cropReset(self):
        pixmap = self.pixmap_item.pixmap()
        self.scene.clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.rect_item = None

        self.parent().crop_button.setEnabled(False)
        self.parent().reset_button.setEnabled(False)

    def saveCrop(self):
        pixmap = self.pixmap_item.pixmap()
        pixmap.save("files\\data.png")

class CropWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QDialog {background: rgb(25, 25, 25);}")
        self.crop_view = CropView()

        self.crop_button = QPushButton("Crop")
        self.reset_button = QPushButton("Reset")
        self.apply_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")

        self.crop_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                            width: 100px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }

                                        QPushButton:disabled {
                                            background-color: #111111;
                                            border: 1px solid #333333;
                                        }
                                        """
                                    )
        self.reset_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                            width: 100px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }

                                        QPushButton:disabled {
                                            background-color: #111111;
                                            border: 1px solid #333333;
                                        }
                                        """
                                    )
        self.apply_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                            width: 100px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }

                                        QPushButton:disabled {
                                            background-color: #111111;
                                            border: 1px solid #333333;
                                        }
                                        """
                                    )
        self.cancel_button.setStyleSheet(
                                        """
                                        QPushButton {
                                            background-color: #222222;
                                            border: 2px solid #555555;
                                            border-radius: 5px;
                                            color: #CCCCCC;
                                            padding: 8px 8px;
                                            width: 100px;
                                        }
                                        
                                        QPushButton:hover {
                                            background-color: #333333;
                                        }
                                        
                                        QPushButton:pressed {
                                            background-color: #444444;
                                            border: 2px solid #777777;
                                        }

                                        QPushButton:disabled {
                                            background-color: #111111;
                                            border: 1px solid #333333;
                                        }
                                        """
                                    )
        
        self.reset_button.setEnabled(False)
        self.reset_button.clicked.connect(self.resetCrop)

        self.crop_button.setEnabled(False)
        self.crop_button.clicked.connect(self.applyCrop)

        self.apply_button.clicked.connect(self.acceptCrop)

        self.cancel_button.clicked.connect(self.rejectCrop)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.crop_button)
        vlayout.addWidget(self.reset_button)
        vlayout.addSpacing(100)
        vlayout.addWidget(self.apply_button)
        vlayout.addWidget(self.cancel_button)
        vlayout.setAlignment(Qt.AlignCenter)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.crop_view)
        hlayout.addLayout(vlayout)

        self.setLayout(hlayout)

    def callCropDialog(self, windowTitle, windowWidth, windowHeight, modal):
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setWindowTitle(windowTitle)
        self.setGeometry(700, 300, windowWidth, windowHeight)
        self.setFixedSize(QSize(windowWidth, windowHeight))
        self.setModal(modal)

        self.return_value = False

        self.show()
        self.crop_view.setPhoto(QPixmap("files\\data.png"))
        self.exec()

        if self.return_value:
            return True
        else:
            return False

    def applyCrop(self):
        self.crop_view.cropImage()
        self.return_value = True

    def resetCrop(self):
        self.crop_view.cropReset()

    def acceptCrop(self):
        self.crop_view.saveCrop()
        self.accept()

    def rejectCrop(self):
        self.return_value = False
        self.reject()

app = QApplication(sys.argv)
window = MainWindow(app)
window.show()
app.exec()