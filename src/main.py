import sys
from view.main_window import MainWindow
from controller.controller import Controller
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication([])

    controller = Controller()
    window = MainWindow(controller)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
