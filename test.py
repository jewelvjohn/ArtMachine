from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap, QFont, QPainter, QTextOption, QDesktopServices
from PySide6.QtCore import Qt, QUrl

class AboutUsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About Us")
        self.setGeometry(100, 100, 550, 250)
        self.setStyleSheet("QMainWindow {background: rgb(25, 25, 25);}")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        about_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        link_layout = QHBoxLayout()

        image_label = QLabel()
        pixmap = QPixmap("files\\Profile.png")  # Replace "image.jpg" with your image file path
        pixmap = pixmap.scaledToWidth(128)  # Adjust the width of the image

        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setFixedSize(128, 128)


        header_label = QLabel()
        header_label.setText("Hello, ")
        header_label.setFont(QFont("Arial", 26))
        header_label.setStyleSheet("""QLabel {
                                                color: #DDDDDD;
                                            }""")

        text_label = QLabel()
        text_label.setText("        My name is Jewel John, I'm a computer science student & this application was developed just for the fun of it. It's built using PySide6 and other Python libraries. Thanks for trying it out. If you wanna contact me feel free to do so. Links to my website and socials are given below.")
        text_label.setAlignment(Qt.AlignLeft)
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Arial", 12))
        text_label.setStyleSheet("""QLabel {
                                                color: #CCCCCC;
                                            }""")
        text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        text_layout.addWidget(header_label)
        text_layout.addWidget(text_label)
        text_layout.setAlignment(Qt.AlignCenter)

        about_layout.addSpacing(20)
        about_layout.addWidget(image_label)
        about_layout.addSpacing(10)
        about_layout.addLayout(text_layout)
        about_layout.addSpacing(20)
        about_layout.setAlignment(Qt.AlignCenter)

        website = QLabel()
        website.setText('<a href="https://jewelvjohn.github.io">Website</a>')
        website.setStyleSheet("""QLabel {
                                                border: 1px solid #444444;
                                                background: #444444;
                                                border-radius: 8px;
                                            }""")
        website.setAlignment(Qt.AlignCenter)
        website.setFont(QFont("Impact", 12))
        website.setOpenExternalLinks(True)
        website.setMinimumHeight(30)

        instagram = QLabel()
        instagram.setText('<a href="https://www.instagram.com/jewelvjohn">Instagram</a>')
        instagram.setStyleSheet("""QLabel {
                                                border: 1px solid #444444;
                                                background: #444444;
                                                border-radius: 8px;
                                            }""")
        instagram.setAlignment(Qt.AlignCenter)
        instagram.setFont(QFont("Impact", 12))
        instagram.setOpenExternalLinks(True)
        instagram.setMinimumHeight(30)

        github = QLabel()
        github.setText('<a href="https://github.com/jewelvjohn">Github</a>')
        github.setStyleSheet("""QLabel {
                                                border: 1px solid #444444;
                                                background: #444444;
                                                border-radius: 8px;
                                            }""")
        github.setAlignment(Qt.AlignCenter)
        github.setFont(QFont("Impact", 12))
        github.setOpenExternalLinks(True)
        github.setMinimumHeight(30)

        link_layout.addSpacing(30)
        link_layout.addWidget(website)
        link_layout.addSpacing(30)
        link_layout.addWidget(instagram)
        link_layout.addSpacing(30)
        link_layout.addWidget(github)
        link_layout.addSpacing(30)

        layout.addSpacing(10)
        layout.addLayout(about_layout)
        layout.addSpacing(20)
        layout.addLayout(link_layout)
        layout.addSpacing(10)

        main_widget.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])

    about_us_window = AboutUsWindow()
    about_us_window.show()

    app.exec()
