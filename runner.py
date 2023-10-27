import re
import sys
import platform
from PySide6 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
from searchbin import search_loop

PLATFORM = platform.system()


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
                "color: #FF8E19; font-size: 20pt; font-weight: 700;"
            )
            self.subtitlelabel.setStyleSheet(
                "color: #FF8E19; font-size: 14pt; font-weight: 300;"
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
            self.openGame(dialog.selectedUrls()[0].toLocalFile())


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
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].toLocalFile().endswith(".t3"):
            event.acceptProposedAction()
            self.child.showDropIsValid(True)

    def dragLeaveEvent(self, event):
        self.child.showDropIsValid(False)

    def dropEvent(self, event):
        path = event.mimeData().urls()[0].toLocalFile()
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
        self.setStyleSheet("background: #300030; color: white;")

        self.openGameWidget = DragAndDropButtonWidget(
            PromptWidget(openGameHandler=self.openGame), openGameHandler=self.openGame
        )

        self.playerWidget = QtWebEngineWidgets.QWebEngineView()
        self.playerWidget.load("http://tads.org")

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.openGameWidget)
        self.stack.addWidget(self.playerWidget)
        self.stack.setCurrentIndex(0)

        self.serverProcess = None
        self.foundGame = False
        self.isWebUI = False
        self.serverFinished = True

        self.setCentralWidget(self.stack)

    def processFinished(self):
        self.serverFinished = True
        if self.foundGame:
            self.close()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Uh oh!",
                "Failed to start Web UI server process.",
                buttons=QtWidgets.QMessageBox.StandardButton.Ok,
            )

    def closeEvent(self, event, accepted=False):
        if self.serverProcess is not None and not self.serverFinished:
            button = QtWidgets.QMessageBox.question(
                self,
                "Close game?",
                "Are you sure you want to close your game while it's still running?",
            )
            if button == QtWidgets.QMessageBox.StandardButton.Yes:
                if (
                    PLATFORM == "Windows"
                ):  # windows doesn't have a proper way to end terminal applications lmfao
                    self.serverProcess.kill()
                else:
                    self.serverProcess.terminate()
                self.serverProcess.waitForFinished()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def processStdout(self):
        data = self.serverProcess.readAllStandardOutput()
        line = bytes(data).decode("utf8")
        if self.isWebUI:
            urls = findUrl(line)
            if len(urls) > 0:
                print(urls)
                self.foundGame = True
                self.playerWidget.load(urls[0])
                self.stack.setCurrentIndex(1)
        else:
            matches = re.search(r"^WinId: ([0-9]+)$", line)
            if matches is not None:
                print(matches.group(1))
                window = QtGui.QWindow.fromWinId(int(matches.group(1)))
                window.setFlags(QtCore.Qt.WindowType.FramelessWindowHint)
                self.playerWidget = QtWidgets.QWidget.createWindowContainer(window)
                self.stack.insertWidget(1, self.playerWidget)
                self.stack.setCurrentIndex(1)

    def processTimeout(self):
        if not self.foundGame:
            QtWidgets.QMessageBox.critical(
                self,
                "Uh oh!",
                "It looks like the frobTADS server didn't start in a reasonable amount of time. Something's wrong.",
                buttons=QtWidgets.QMessageBox.StandardButton.Ok,
            )
            self.serverProcess.kill()

    def openGame(self, path):
        global PLATFORM

        self.foundGame = False
        self.isWebUI = False

        with open(path, "rb") as fh:
            if search_loop(["tads-net".encode("utf-8")], fh.name, fh.read, fh.seek):
                self.isWebUI = True

        self.serverProcess = QtCore.QProcess()
        self.serverProcess.finished.connect(self.processFinished)
        self.serverProcess.readyReadStandardOutput.connect(self.processStdout)

        if not self.isWebUI:
            if PLATFORM == "Linux":
                self.serverProcess.start("./qtads/qtads", [path])
            elif PLATFORM == "Darwin":
                pass
            elif PLATFORM == "Windows":
                self.serverProcess.start("./qtads/qtads.exe", [path])
            self.foundGame = True
            self.serverFinished = False
        else:
            if PLATFORM == "Linux" or PLATFORM == "Darwin":
                self.serverProcess.start(
                    "./frobtads/build/frob", ["-i", "plain", "-N", "0", path]
                )
            elif PLATFORM == "Windows":
                self.serverProcess.start(
                    "./t3run.exe", ["-plain", "-ns0", "-webhost", "localhost", path]
                )

            self.serverFinished = False
            QtCore.QTimer.singleShot(1300, self.processTimeout)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    if PLATFORM not in ["Windows", "Linux", "Darwin"]:
        QtWidgets.QMessageBox.critical(
            app,
            "Uh oh!",
            "It looks like you're running this on an unsupported platform. At the moment, we only support Linux, macOS, and Windows.",
        )
    window = RunnerWindow()
    window.show()

    if len(sys.argv) > 1:
        window.openGame(sys.argv[1], None)

    sys.exit(app.exec())
