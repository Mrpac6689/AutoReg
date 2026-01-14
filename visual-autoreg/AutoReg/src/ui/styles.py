from PyQt6 import QtCore

class Styles:
    @staticmethod
    def apply_styles(widget):
        widget.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056a1;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
            }
        """)