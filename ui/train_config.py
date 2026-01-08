# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'train_config.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            QSize, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QPushButton, QWidget)


class Ui_train_config_form(object):
    def setupUi(self, train_config_form):
        if not train_config_form.objectName():
            train_config_form.setObjectName(u"train_config_form")
        train_config_form.resize(480, 640)
        train_config_form.setMinimumSize(QSize(480, 640))
        train_config_form.setMaximumSize(QSize(480, 640))
        self.train_name_label = QLabel(train_config_form)
        self.train_name_label.setObjectName(u"train_name_label")
        self.train_name_label.setGeometry(QRect(0, 20, 481, 61))
        font = QFont()
        font.setPointSize(20)
        self.train_name_label.setFont(font)
        self.train_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line = QFrame(train_config_form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 90, 461, 16))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.comboBox_setmap = QComboBox(train_config_form)
        self.comboBox_setmap.addItem("")
        self.comboBox_setmap.setObjectName(u"comboBox_setmap")
        self.comboBox_setmap.setGeometry(QRect(260, 150, 141, 41))
        font1 = QFont()
        font1.setPointSize(12)
        self.comboBox_setmap.setFont(font1)
        self.comboBox_setmap.setModelColumn(0)
        self.label_2 = QLabel(train_config_form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(270, 110, 121, 41))
        font2 = QFont()
        font2.setPointSize(16)
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comboBox_setdelay = QComboBox(train_config_form)
        self.comboBox_setdelay.addItem("")
        self.comboBox_setdelay.setObjectName(u"comboBox_setdelay")
        self.comboBox_setdelay.setGeometry(QRect(40, 250, 141, 41))
        self.comboBox_setdelay.setFont(font1)
        self.comboBox_setdelay.setFrame(True)
        self.label_3 = QLabel(train_config_form)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 210, 181, 41))
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutWidget = QWidget(train_config_form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 560, 461, 71))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_save = QPushButton(self.layoutWidget)
        self.pushButton_save.setObjectName(u"pushButton_save")
        self.pushButton_save.setMaximumSize(QSize(300, 300))
        font3 = QFont()
        font3.setPointSize(14)
        self.pushButton_save.setFont(font3)

        self.horizontalLayout.addWidget(self.pushButton_save)

        self.pushButton_del = QPushButton(self.layoutWidget)
        self.pushButton_del.setObjectName(u"pushButton_del")
        self.pushButton_del.setMaximumSize(QSize(300, 300))
        self.pushButton_del.setFont(font3)

        self.horizontalLayout.addWidget(self.pushButton_del)

        self.pushButton_cancel = QPushButton(self.layoutWidget)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")
        self.pushButton_cancel.setMaximumSize(QSize(300, 300))
        self.pushButton_cancel.setFont(font3)

        self.horizontalLayout.addWidget(self.pushButton_cancel)

        self.comboBox_set_start = QComboBox(train_config_form)
        self.comboBox_set_start.addItem("")
        self.comboBox_set_start.addItem("")
        self.comboBox_set_start.setObjectName(u"comboBox_set_start")
        self.comboBox_set_start.setGeometry(QRect(40, 350, 141, 41))
        self.comboBox_set_start.setFont(font1)
        self.comboBox_set_start.setFrame(True)
        self.label_4 = QLabel(train_config_form)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(40, 310, 141, 41))
        self.label_4.setFont(font2)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_6 = QLabel(train_config_form)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(260, 210, 141, 41))
        self.label_6.setFont(font2)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_speed = QLineEdit(train_config_form)
        self.lineEdit_speed.setObjectName(u"lineEdit_speed")
        self.lineEdit_speed.setGeometry(QRect(270, 250, 121, 41))
        self.lineEdit_speed.setFont(font1)
        self.lineEdit_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_7 = QLabel(train_config_form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(250, 310, 161, 41))
        self.label_7.setFont(font2)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comboBox_set_end = QComboBox(train_config_form)
        self.comboBox_set_end.addItem("")
        self.comboBox_set_end.addItem("")
        self.comboBox_set_end.setObjectName(u"comboBox_set_end")
        self.comboBox_set_end.setGeometry(QRect(260, 350, 141, 41))
        self.comboBox_set_end.setFont(font1)
        self.comboBox_set_end.setFrame(True)
        self.lineEdit_name = QLineEdit(train_config_form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setGeometry(QRect(50, 150, 121, 41))
        self.lineEdit_name.setFont(font1)
        self.lineEdit_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_turnout_6 = QLabel(train_config_form)
        self.label_turnout_6.setObjectName(u"label_turnout_6")
        self.label_turnout_6.setGeometry(QRect(60, 110, 101, 41))
        self.label_turnout_6.setFont(font2)
        self.label_turnout_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_opt = QLabel(train_config_form)
        self.label_opt.setObjectName(u"label_opt")
        self.label_opt.setGeometry(QRect(30, 410, 161, 41))
        self.label_opt.setFont(font2)
        self.label_opt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comboBox_opt = QComboBox(train_config_form)
        self.comboBox_opt.addItem("")
        self.comboBox_opt.addItem("")
        self.comboBox_opt.addItem("")
        self.comboBox_opt.setObjectName(u"comboBox_opt")
        self.comboBox_opt.setGeometry(QRect(40, 450, 141, 41))
        self.comboBox_opt.setFont(font1)
        self.comboBox_opt.setFrame(True)

        self.retranslateUi(train_config_form)

        QMetaObject.connectSlotsByName(train_config_form)

    # setupUi

    def retranslateUi(self, train_config_form):
        train_config_form.setWindowTitle(
            QCoreApplication.translate("train_config_form", u"\u5217\u8f66\u914d\u7f6e\u7a97\u53e3", None))
        # if QT_CONFIG(accessibility)
        train_config_form.setAccessibleName("")
        # endif // QT_CONFIG(accessibility)
        self.train_name_label.setText(
            QCoreApplication.translate("train_config_form", u"\u5217\u8f66\u914d\u7f6e", None))
        self.comboBox_setmap.setItemText(0,
                                         QCoreApplication.translate("train_config_form", u"\u4e0d\u4f7f\u7528", None))

        self.label_2.setText(QCoreApplication.translate("train_config_form", u"\u8fd0\u884c\u56fe\u9009\u62e9", None))
        self.comboBox_setdelay.setItemText(0, QCoreApplication.translate("train_config_form",
                                                                         u"\u8fd0\u884c\u4eff\u771f\u5373\u65f6", None))

        self.label_3.setText(QCoreApplication.translate("train_config_form", u"\u542f\u52a8\u65f6\u95f4", None))
        self.pushButton_save.setText(QCoreApplication.translate("train_config_form", u"\u4fdd\u5b58", None))
        self.pushButton_del.setText(QCoreApplication.translate("train_config_form", u"\u5220\u9664", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("train_config_form", u"\u53d6\u6d88", None))
        self.comboBox_set_start.setItemText(0, QCoreApplication.translate("train_config_form", u"\u4e0a\u6d77\u5357",
                                                                          None))
        self.comboBox_set_start.setItemText(1, QCoreApplication.translate("train_config_form", u"\u4e0a\u6d77\u7ad9",
                                                                          None))

        self.label_4.setText(QCoreApplication.translate("train_config_form", u"\u8d77\u59cb\u7ad9", None))
        self.label_6.setText(QCoreApplication.translate("train_config_form", u"\u521d\u59cb\u901f\u5ea6", None))
        self.lineEdit_speed.setText(QCoreApplication.translate("train_config_form", u"0", None))
        self.label_7.setText(QCoreApplication.translate("train_config_form", u"\u7ec8\u70b9\u7ad9", None))
        self.comboBox_set_end.setItemText(0,
                                          QCoreApplication.translate("train_config_form", u"\u4e0a\u6d77\u5357", None))
        self.comboBox_set_end.setItemText(1,
                                          QCoreApplication.translate("train_config_form", u"\u4e0a\u6d77\u7ad9", None))

        self.lineEdit_name.setText(QCoreApplication.translate("train_config_form", u"XXX", None))
        self.label_turnout_6.setText(QCoreApplication.translate("train_config_form", u"\u540d\u79f0", None))
        self.label_opt.setText(QCoreApplication.translate("train_config_form", u"\u5230\u7ad9\u64cd\u4f5c", None))
        self.comboBox_opt.setItemText(0, QCoreApplication.translate("train_config_form", u"\u505c\u6b62", None))
        self.comboBox_opt.setItemText(1, QCoreApplication.translate("train_config_form", u"\u6298\u8fd4", None))
        self.comboBox_opt.setItemText(2, QCoreApplication.translate("train_config_form", u"\u91cd\u5934\u8fd0\u884c",
                                                                    None))

    # retranslateUi
