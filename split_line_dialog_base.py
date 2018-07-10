# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'split_line_dialog_base.ui'
#
# Created: Sun Jul 08 10:23:29 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SplitLineDialogBase(object):
    def setupUi(self, SplitLineDialogBase):
        SplitLineDialogBase.setObjectName(_fromUtf8("SplitLineDialogBase"))
        SplitLineDialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(SplitLineDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))

        self.retranslateUi(SplitLineDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), SplitLineDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), SplitLineDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(SplitLineDialogBase)

    def retranslateUi(self, SplitLineDialogBase):
        SplitLineDialogBase.setWindowTitle(_translate("SplitLineDialogBase", "Split Line", None))

