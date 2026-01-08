# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QTextBrowser,
    QWidget)

class Ui_aboutForm(object):
    def setupUi(self, aboutForm):
        if not aboutForm.objectName():
            aboutForm.setObjectName(u"aboutForm")
        aboutForm.resize(640, 480)
        aboutForm.setMaximumSize(QSize(640, 480))
        self.label = QLabel(aboutForm)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 621, 31))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textBrowser = QTextBrowser(aboutForm)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(20, 60, 601, 381))

        self.retranslateUi(aboutForm)

        QMetaObject.connectSlotsByName(aboutForm)
    # setupUi

    def retranslateUi(self, aboutForm):
        aboutForm.setWindowTitle(QCoreApplication.translate("aboutForm", u"\u5173\u4e8e", None))
        self.label.setText(QCoreApplication.translate("aboutForm", u"\u5173\u4e8e About", None))
        self.textBrowser.setHtml(QCoreApplication.translate("aboutForm", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span"
                        " style=\" font-size:14pt;\">\u672c\u9879\u76ee\u57fa\u4e8e PyQT6 \u5f00\u53d1</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">GITHUB\uff1a</span><a href=\"https://github.com/ChlorophyTeio\"><span style=\" font-size:14pt; text-decoration: underline; color:#28497c;\">https://github.com/ChlorophyTeio</span></a></p></body></html>", None))
    # retranslateUi

