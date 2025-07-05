import sys
import os
import matplotlib
from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtWidgets import QApplication

matplotlib.use("Agg")
from view.main_window import MainWindow

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/lib/qt/plugins"

print("Qt version :", QT_VERSION_STR)
print("PyQt version :", PYQT_VERSION_STR)


def main():
    app = QApplication(["pointcloud_viewer"])
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
