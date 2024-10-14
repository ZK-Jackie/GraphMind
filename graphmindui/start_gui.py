import sys
from PyQt5.QtWidgets import QApplication
from graphmindui.graphmind_ui import MainWindow

def start_ui(**kwargs):
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
