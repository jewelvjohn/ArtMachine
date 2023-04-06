import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

app = QApplication(sys.argv)

window = MainWindow(app)
window.setStyleSheet("QMainWindow {background: rgb(25, 25, 25);}")
window.show()

app.exec()