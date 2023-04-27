from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                               QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, 
                               QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QVBoxLayout)
from PySide6.QtGui import QPixmap, QMouseEvent, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QRectF, QPointF

class CropView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.rect_item = None
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

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
            pen = QPen(Qt.white)
            pen.setWidth(2)
            self.rect_item.setPen(pen)
            brush = QBrush(QColor(255, 255, 255, 100))
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
            rect = self.rect_item.rect().toRect()
            cropped_pixmap = self.pixmap_item.pixmap().copy(rect)
            self.scene.clear()
            self.pixmap_item = QGraphicsPixmapItem(cropped_pixmap)
            self.scene.addItem(self.pixmap_item)
            self.setSceneRect(QRectF(cropped_pixmap.rect()))
            self.rect_item = None

class CropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.crop_view = CropView()
        label = QLabel("Crop Image")
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")

        vlayout = QVBoxLayout()
        vlayout.addWidget(label)
        vlayout.addWidget(apply_button)
        vlayout.addWidget(cancel_button)
        vlayout.setAlignment(Qt.AlignCenter)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.crop_view)
        hlayout.addLayout(vlayout)

        self.setLayout(hlayout)

app = QApplication([])
window = QMainWindow()
window.setGeometry(400, 300, 1000, 600)
window.setFixedSize(1000, 600)

crop_widget = CropWidget()
window.setCentralWidget(crop_widget)

window.show()
crop_widget.crop_view.setPhoto(QPixmap('image.jpg'))
app.exec()
