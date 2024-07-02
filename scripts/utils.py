from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon


def warningBox(windowTitle: str, message: str, path: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowIcon(QIcon(path))
    msg.setText(message)
    msg.setWindowTitle(windowTitle)
    msg.exec()
