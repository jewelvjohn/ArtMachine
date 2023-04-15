from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtGui import QPixmap, QMouseEvent, QPen, QBrush, QColor
from PySide6.QtCore import Qt, QRectF

class CropView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.rect_item = None
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    
    def setPixmap(self, pixmap):
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(pixmap.rect()))
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            pos = event.position()
            self.rect_item = QGraphicsRectItem(pos.x(), pos.y(), 0, 0)
            pen = QPen(Qt.white)
            pen.setWidth(4)
            self.rect_item.setPen(pen)
            brush = QBrush(QColor(255, 255, 255, 100))
            self.rect_item.setBrush(brush)
            self.scene.addItem(self.rect_item)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.rect_item is not None:
            rect = self.rect_item.rect()
            rect.setBottomRight(event.position())
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


app = QApplication([])
main_window = QMainWindow()
main_window.setGeometry(100, 100, 640, 480)
crop_view = CropView()
pixmap = QPixmap('image.jpg')
crop_view.setPixmap(pixmap)
main_window.setCentralWidget(crop_view)
main_window.show()
app.exec()