try:
    # PySide2
    from PySide2 import QtGui, QtWidgets, QtCore, QtPrintSupport, QtQml
    from PySide2.QtCore import Signal, Slot
except ImportError:
    # PyQt5
    from PyQt5 import QtGui, QtWidgets, QtCore, QtPrintSupport, QtQml
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot