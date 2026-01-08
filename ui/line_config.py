# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'line_config.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QWidget)


class Ui_train_config_form(object):
    def setupUi(self, train_config_form):
        if not train_config_form.objectName():
            train_config_form.setObjectName(u"train_config_form")
        train_config_form.resize(480, 640)
        train_config_form.setMinimumSize(QSize(480, 640))
        train_config_form.setMaximumSize(QSize(480, 640))
        self.station_name_label = QLabel(train_config_form)
        self.station_name_label.setObjectName(u"station_name_label")
        self.station_name_label.setGeometry(QRect(0, 20, 481, 61))
        font = QFont()
        font.setPointSize(20)
        self.station_name_label.setFont(font)
        self.station_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line = QFrame(train_config_form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 90, 461, 16))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layoutWidget = QWidget(train_config_form)
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

        self.lineEdit_line_total_length = QLineEdit(train_config_form)
        self.lineEdit_line_total_length.setObjectName(u"lineEdit_line_total_length")
        self.lineEdit_line_total_length.setGeometry(QRect(140, 220, 191, 61))
        font2 = QFont()
        font2.setPointSize(16)
        self.lineEdit_line_total_length.setFont(font2)
        self.lineEdit_line_total_length.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2 = QLabel(train_config_form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(150, 160, 181, 61))
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_3 = QLabel(train_config_form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(120, 310, 231, 61))
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_line_total_speed = QLineEdit(train_config_form)
        self.lineEdit_line_total_speed.setObjectName(u"lineEdit_line_total_speed")
        self.lineEdit_line_total_speed.setGeometry(QRect(140, 370, 191, 61))
        self.lineEdit_line_total_speed.setFont(font2)
        self.lineEdit_line_total_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.retranslateUi(train_config_form)

        QMetaObject.connectSlotsByName(train_config_form)

    # setupUi

    def retranslateUi(self, train_config_form):
        train_config_form.setWindowTitle(
            QCoreApplication.translate("train_config_form", u"\u7ebf\u8def\u914d\u7f6e\u7a97\u53e3", None))
        # if QT_CONFIG(accessibility)
        train_config_form.setAccessibleName("")
        # endif // QT_CONFIG(accessibility)
        self.station_name_label.setText(
            QCoreApplication.translate("train_config_form", u"\u7ebf\u8def\u914d\u7f6e", None))
        self.pushButton_save.setText(QCoreApplication.translate("train_config_form", u"\u4fdd\u5b58", None))
        self.pushButton_del.setText(QCoreApplication.translate("train_config_form", u"\u5220\u9664", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("train_config_form", u"\u53d6\u6d88", None))
        self.label_2.setText(QCoreApplication.translate("train_config_form", u"\u603b\u957f\u5ea6\uff08km\uff09", None))
        self.label_3.setText(
            QCoreApplication.translate("train_config_form", u"\u7ebf\u8def\u901f\u5ea6\uff08km/h\uff09", None))
    # retranslateUi
