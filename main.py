import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon


def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(500, 300, 700, 500)
    win.setWindowTitle("ArtMachine")
    win.setWindowIcon(QIcon("Icon.png"))
    win.show()
    sys.exit(app.exec_())

window()