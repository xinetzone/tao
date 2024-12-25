try:
    from .qt5 import QtCore, QtGui, QtWidgets, Signal, Slot, QtPrintSupport, QtQml
except:
    from .qt6 import QtCore, QtGui, QtWidgets, Signal, Slot, QtPrintSupport, QtQml


def run(window_type, *args, **kwargs):
    '''运行 GUI'''
    #import sys
    # 实例化一个QApplication对象，用于GUI的初始化
    app = QtWidgets.QApplication([]) # QtWidgets.QApplication(sys.argv)
    # 实例化一个 Window 对象，用于定义一个图形窗口
    window = window_type(*args, **kwargs)
    # # 适配 Retina 显示屏（选写）.
    # app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window.show() # 显示主窗口
    app.exec_()  # 当GUI产生退出信号时Python程序结束
    # 利用内置模块sys的exit()方法侦听GUI的退出信号，以便关闭Python程序。
    #sys.exit(app.exec_())  
    