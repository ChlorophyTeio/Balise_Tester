# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'balise_config.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QWidget)

class Ui_balise_config_form(object):
    def setupUi(self, balise_config_form):
        if not balise_config_form.objectName():
            balise_config_form.setObjectName(u"balise_config_form")
        balise_config_form.resize(480, 640)
        balise_config_form.setMinimumSize(QSize(480, 640))
        balise_config_form.setMaximumSize(QSize(480, 640))
        self.balise_name_label = QLabel(balise_config_form)
        self.balise_name_label.setObjectName(u"balise_name_label")
        self.balise_name_label.setGeometry(QRect(0, 20, 481, 61))
        font = QFont()
        font.setPointSize(20)
        self.balise_name_label.setFont(font)
        self.balise_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line = QFrame(balise_config_form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 90, 461, 16))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layoutWidget = QWidget(balise_config_form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 560, 461, 71))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_save = QPushButton(self.layoutWidget)
        self.pushButton_save.setObjectName(u"pushButton_save")
        self.pushButton_save.setMaximumSize(QSize(300, 300))
        font1 = QFont()
        font1.setPointSize(14)
        self.pushButton_save.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButton_save)

        self.pushButton_del = QPushButton(self.layoutWidget)
        self.pushButton_del.setObjectName(u"pushButton_del")
        self.pushButton_del.setMaximumSize(QSize(300, 300))
        self.pushButton_del.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButton_del)

        self.pushButton_cancel = QPushButton(self.layoutWidget)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")
        self.pushButton_cancel.setMaximumSize(QSize(300, 300))
        self.pushButton_cancel.setFont(font1)

        self.horizontalLayout.addWidget(self.pushButton_cancel)

        self.comboBox_balise_type = QComboBox(balise_config_form)
        self.comboBox_balise_type.addItem("")
        self.comboBox_balise_type.addItem("")
        self.comboBox_balise_type.setObjectName(u"comboBox_balise_type")
        self.comboBox_balise_type.setGeometry(QRect(340, 150, 121, 41))
        font2 = QFont()
        font2.setPointSize(12)
        self.comboBox_balise_type.setFont(font2)
        self.label_turnout_2 = QLabel(balise_config_form)
        self.label_turnout_2.setObjectName(u"label_turnout_2")
        self.label_turnout_2.setGeometry(QRect(30, 210, 101, 41))
        font3 = QFont()
        font3.setPointSize(16)
        self.label_turnout_2.setFont(font3)
        self.label_turnout_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_father_balise = QLineEdit(balise_config_form)
        self.lineEdit_father_balise.setObjectName(u"lineEdit_father_balise")
        self.lineEdit_father_balise.setGeometry(QRect(20, 250, 121, 41))
        self.lineEdit_father_balise.setFont(font2)
        self.lineEdit_father_balise.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_subid = QLineEdit(balise_config_form)
        self.lineEdit_subid.setObjectName(u"lineEdit_subid")
        self.lineEdit_subid.setGeometry(QRect(150, 250, 121, 41))
        self.lineEdit_subid.setFont(font2)
        self.lineEdit_subid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_turnout_3 = QLabel(balise_config_form)
        self.label_turnout_3.setObjectName(u"label_turnout_3")
        self.label_turnout_3.setGeometry(QRect(160, 210, 101, 41))
        self.label_turnout_3.setFont(font3)
        self.label_turnout_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_location = QLineEdit(balise_config_form)
        self.lineEdit_location.setObjectName(u"lineEdit_location")
        self.lineEdit_location.setGeometry(QRect(180, 150, 121, 41))
        self.lineEdit_location.setFont(font2)
        self.lineEdit_location.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_name = QLineEdit(balise_config_form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setGeometry(QRect(20, 150, 121, 41))
        self.lineEdit_name.setFont(font2)
        self.lineEdit_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_turnout_4 = QLabel(balise_config_form)
        self.label_turnout_4.setObjectName(u"label_turnout_4")
        self.label_turnout_4.setGeometry(QRect(350, 110, 101, 41))
        self.label_turnout_4.setFont(font3)
        self.label_turnout_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_turnout_5 = QLabel(balise_config_form)
        self.label_turnout_5.setObjectName(u"label_turnout_5")
        self.label_turnout_5.setGeometry(QRect(190, 110, 101, 41))
        self.label_turnout_5.setFont(font3)
        self.label_turnout_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_turnout_6 = QLabel(balise_config_form)
        self.label_turnout_6.setObjectName(u"label_turnout_6")
        self.label_turnout_6.setGeometry(QRect(30, 110, 101, 41))
        self.label_turnout_6.setFont(font3)
        self.label_turnout_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textEdit_config = QTextEdit(balise_config_form)
        self.textEdit_config.setObjectName(u"textEdit_config")
        self.textEdit_config.setGeometry(QRect(20, 310, 441, 241))
        font4 = QFont()
        font4.setPointSize(10)
        self.textEdit_config.setFont(font4)
        self.comboBox_balise_add_config = QComboBox(balise_config_form)
        self.comboBox_balise_add_config.setObjectName(u"comboBox_balise_add_config")
        self.comboBox_balise_add_config.setGeometry(QRect(280, 250, 171, 41))
        font5 = QFont()
        font5.setPointSize(8)
        self.comboBox_balise_add_config.setFont(font5)
        self.label_turnout_7 = QLabel(balise_config_form)
        self.label_turnout_7.setObjectName(u"label_turnout_7")
        self.label_turnout_7.setGeometry(QRect(310, 210, 111, 41))
        self.label_turnout_7.setFont(font3)
        self.label_turnout_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.retranslateUi(balise_config_form)

        QMetaObject.connectSlotsByName(balise_config_form)
    # setupUi

    def retranslateUi(self, balise_config_form):
        balise_config_form.setWindowTitle(QCoreApplication.translate("balise_config_form", u"\u5e94\u7b54\u5668\u914d\u7f6e\u7a97\u53e3", None))
#if QT_CONFIG(accessibility)
        balise_config_form.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.balise_name_label.setText(QCoreApplication.translate("balise_config_form", u"\u5e94\u7b54\u5668\u914d\u7f6e", None))
        self.pushButton_save.setText(QCoreApplication.translate("balise_config_form", u"\u4fdd\u5b58", None))
        self.pushButton_del.setText(QCoreApplication.translate("balise_config_form", u"\u5220\u9664", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("balise_config_form", u"\u53d6\u6d88", None))
        self.comboBox_balise_type.setItemText(0, QCoreApplication.translate("balise_config_form", u"\u65e0\u6e90", None))
        self.comboBox_balise_type.setItemText(1, QCoreApplication.translate("balise_config_form", u"\u6709\u6e90", None))

        self.label_turnout_2.setText(QCoreApplication.translate("balise_config_form", u"\u7236\u5e94\u7b54\u5668", None))
        self.label_turnout_3.setText(QCoreApplication.translate("balise_config_form", u"\u5b50\u7f16\u53f7", None))
        self.lineEdit_name.setText(QCoreApplication.translate("balise_config_form", u"XXX", None))
        self.label_turnout_4.setText(QCoreApplication.translate("balise_config_form", u"\u7c7b\u578b", None))
        self.label_turnout_5.setText(QCoreApplication.translate("balise_config_form", u"\u4f4d\u7f6e", None))
        self.label_turnout_6.setText(QCoreApplication.translate("balise_config_form", u"\u540d\u79f0", None))
        self.textEdit_config.setHtml(QCoreApplication.translate("balise_config_form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Microsoft YaHei UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.label_turnout_7.setText(QCoreApplication.translate("balise_config_form", u"\u6dfb\u52a0\u62a5\u6587", None))
    # retranslateUi

