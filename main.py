# main.py (placeholder)
from PyQt6.QtWidgets import QApplication
import sys
from astro_sorter.ui_main import UiAstroSorter

def main():
    app = QApplication(sys.argv)
    w = UiAstroSorter()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
