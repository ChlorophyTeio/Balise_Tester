# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'map.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_Map_MainWindow(object):
    def setupUi(self, Map_MainWindow):
        if not Map_MainWindow.objectName():
            Map_MainWindow.setObjectName(u"Map_MainWindow")
        Map_MainWindow.resize(1080, 620)
        Map_MainWindow.setMinimumSize(QSize(1080, 620))
        Map_MainWindow.setMaximumSize(QSize(1080, 620))
        self.centralwidget = QWidget(Map_MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        Map_MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Map_MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1080, 33))
        self.menu_edit = QMenu(self.menubar)
        self.menu_edit.setObjectName(u"menu_edit")
        self.menu_undo = QMenu(self.menubar)
        self.menu_undo.setObjectName(u"menu_undo")
        self.menu_redo = QMenu(self.menubar)
        self.menu_redo.setObjectName(u"menu_redo")
        self.menu_save = QMenu(self.menubar)
        self.menu_save.setObjectName(u"menu_save")
        self.menu_new = QMenu(self.menubar)
        self.menu_new.setObjectName(u"menu_new")
        self.menu_import = QMenu(self.menubar)
        self.menu_import.setObjectName(u"menu_import")
        Map_MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Map_MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        Map_MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_new.menuAction())
        self.menubar.addAction(self.menu_import.menuAction())
        self.menubar.addAction(self.menu_edit.menuAction())
        self.menubar.addAction(self.menu_undo.menuAction())
        self.menubar.addAction(self.menu_redo.menuAction())
        self.menubar.addAction(self.menu_save.menuAction())

        self.retranslateUi(Map_MainWindow)

        QMetaObject.connectSlotsByName(Map_MainWindow)
    # setupUi

    def retranslateUi(self, Map_MainWindow):
        Map_MainWindow.setWindowTitle(QCoreApplication.translate("Map_MainWindow", u"\u8fd0\u884c\u56fe", None))
        self.menu_edit.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u7f16\u8f91", None))
        self.menu_undo.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u64a4\u9500", None))
        self.menu_redo.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u91cd\u505a", None))
        self.menu_save.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u4fdd\u5b58", None))
        self.menu_new.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u65b0\u5efa", None))
        self.menu_import.setTitle(QCoreApplication.translate("Map_MainWindow", u"\u5bfc\u5165", None))
    # retranslateUi

