import re
import sys
import subprocess
from PySide6 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets


class PromptWidget(QtWidgets.QWidget):
    def __init__(self, openGameHandler):
        super().__init__()

        self.openGame = openGameHandler

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.mainlabel = QtWidgets.QLabel(
            "Play a T3 File", alignment=QtCore.Qt.AlignCenter
        )
        self.mainlabel.setStyleSheet("font-size: 20pt; font-weight: 700;")
        self.mainlabel.installEventFilter(self)
        layout.addWidget(self.mainlabel)

        self.subtitlelabel = QtWidgets.QLabel(
            "Drag and drop the file into this window or click the button below",
            margin=5,
            alignment=QtCore.Qt.AlignCenter,
        )
        self.subtitlelabel.setStyleSheet(
            "font-size: 14pt; color: #ddd; font-weight: 300;"
        )
        self.subtitlelabel.installEventFilter(self)
        layout.addWidget(self.subtitlelabel)

        self.button = QtWidgets.QPushButton("Open game")
        self.button.clicked.connect(self.openChooseGameDialog)
        self.button.setStyleSheet(
            "QPushButton { height: 40px; background: #400040 } QPushButton:hover { background: #300030; }"
        )
        self.button.installEventFilter(self)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def showDropIsValid(self, valid):
        if valid:
            self.mainlabel.setStyleSheet(
                "color: rgb(225, 142, 25); font-size: 20pt; font-weight: 700;"
            )
            self.subtitlelabel.setStyleSheet(
                "color: rgb(225, 142, 25); font-size: 14pt; font-weight: 300;"
            )
        else:
            self.mainlabel.setStyleSheet(
                "color: white; font-size: 20pt; font-weight: 700;"
            )
            self.subtitlelabel.setStyleSheet(
                "color: #ddd; font-size: 14pt; font-weight: 300;"
            )

    def openChooseGameDialog(self, event):
        dialog = QtWidgets.QFileDialog()
        dialog.setAcceptDrops(True)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("TADS 3 Game Files (*.t3)")
        if dialog.exec():
            self.openGame(dialog.selectedUrls()[0].path())


class DragAndDropButtonWidget(QtWidgets.QWidget):
    def __init__(self, child: QtWidgets.QWidget, openGameHandler):
        super().__init__()

        self.openGame = openGameHandler

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.setAcceptDrops(True)

        self.child = child
        self.child.installEventFilter(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.child)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if (
            event.mimeData().hasFormat("application/vnd.portal.filetransfer")
            or event.mimeData().hasFormat("application/vnd.portal.files")
        ) and event.mimeData().urls()[0].path().endswith(".t3"):
            event.acceptProposedAction()
            self.child.showDropIsValid(True)

    def dragLeaveEvent(self, event):
        self.child.showDropIsValid(False)

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].path()
        self.openGame(path)
        event.acceptProposedAction()
        self.child.showDropIsValid(False)


def findUrl(string):
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


class RunnerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        title = "TADS 3 Runner"

        self.setWindowTitle(title)
        self.setStyleSheet("background: #300030;")

        self.openGameWidget = DragAndDropButtonWidget(
            PromptWidget(openGameHandler=self.openGame), openGameHandler=self.openGame
        )

        self.webWidget = QtWebEngineWidgets.QWebEngineView()
        self.webWidget.load("http://tads.org")

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.openGameWidget)
        self.stack.addWidget(self.webWidget)
        self.stack.setCurrentIndex(0)

        self.setCentralWidget(self.stack)

    def openGame(self, path):
        popen = subprocess.Popen(
            ["frob", "-N", "0", path], shell=False, stdout=subprocess.PIPE
        )
        lines = 0
        while popen.poll() is None:
            line = popen.stdout.readline().decode()
            if len(line) > 0:
                lines += 1
                urls = findUrl(line)
                if len(urls) > 0:
                    print(urls)
                    self.webWidget.load(urls[0])
                    break
                elif lines > 2:
                    break
        self.stack.setCurrentIndex(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = RunnerWindow()
    window.show()

    sys.exit(app.exec())
