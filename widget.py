import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Artmachine")

        setButton = QPushButton("Ok")
        setButton.clicked.connect(self.set_image_path)

        runButton = QPushButton("Run")
        runButton.clicked.connect(self.execute_sketch)

        layout = QVBoxLayout()
        layout.addWidget(setButton)
        layout.addWidget(runButton)

        self.setLayout(layout)

    def set_image_path(self):
        print("Ok Button clicked")

    def execute_sketch(self):
        print("Run Button clicked")