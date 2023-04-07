import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, QLabel, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLineEdit, QSizePolicy

class ContrastDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QDialog {background: rgb(25, 25, 25);}")
        self.setWindowIcon(QIcon("sprites\\Icon.png"))
        self.setWindowTitle("Set Contrast")
        self.setGeometry(700, 300, 300, 150)
        self.setFixedSize(QSize(300, 150))

        label = QLabel("Contrast:")
        label.setStyleSheet("QLabel {color: rgb(144, 144, 144)}")
        label.setAlignment(Qt.AlignCenter)
        label.setMaximumHeight(20)
        label.setFont(QFont("Arial", 18))

        slider = QSlider(Qt.Horizontal)
        line = QLineEdit()
        line.setMaximumWidth(40)

        ok_button = QPushButton("Ok")
        cancel_button = QPushButton("Cancel")

        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        slider_layout.addWidget(slider)
        slider_layout.addWidget(line)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(label)
        layout.addLayout(slider_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

app = QApplication(sys.argv)
window = ContrastDialog()
window.show()
app.exec()