try:
    # PySide6
    from PySide6 import QtGui, QtWidgets, QtCore, QtPrintSupport, QtQml
    from PySide6.QtCore import Signal, Slot
except ImportError:
    # PyQt6
    from PyQt6 import QtGui, QtWidgets, QtCore, QtPrintSupport, QtQml
    from PyQt6.QtCore import pyqtSignal as Signal, pyqtSlot as Slot