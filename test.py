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

        self.value = int(100)

        label = QLabel("Contrast")
        label.setStyleSheet("QLabel {color: rgb(144, 144, 144)}")
        label.setAlignment(Qt.AlignCenter)
        label.setMaximumHeight(20)
        label.setFont(QFont("Arial", 18))

        self.slider = QSlider(Qt.Horizontal)
        self.line = QLineEdit()

        self.slider.setMaximum(200)
        self.slider.setMinimum(0)
        self.slider.setValue(self.value)
        self.slider.valueChanged.connect(self.slider_changed)

        self.line.setMaximumWidth(40)
        self.line.setDisabled(True)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setText(str(self.value))

        ok_button = QPushButton("Ok")
        cancel_button = QPushButton("Cancel")

        ok_button.pressed.connect(self.apply_dialog)
        cancel_button.pressed.connect(self.reject)

        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.line)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(label)
        layout.addLayout(slider_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def slider_changed(self):
        self.value = self.slider.value()
        self.line.setText(str(self.value))

    def apply_dialog(self):
        self.enabled = True
        self.accept()

app = QApplication(sys.argv)
window = ContrastDialog()
window.show()
app.exec()