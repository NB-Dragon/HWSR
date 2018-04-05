import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from mainwindow import Ui_MainWindow


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

    def open_image(self):
        target    = self.lbl_image_origin
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files(*.jpeg *.png *.jpg)")
        image     = QtGui.QPixmap(file_name[0])
        image     = image.scaled(target.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        target.setPixmap(image)

    def sb_value_change(self):
        object_origin = {
            "sb_binary": self.sb_binary,
            "sb_ratio" : self.sb_ratio
        }
        object_target = {
            "sb_binary": self.sb_binary_value,
            "sb_ratio" : self.sb_ratio_value
        }
        object_ratio  = {
            "sb_binary": 1,
            "sb_ratio" : 0.01
        }
        origin = object_origin[self.sender().objectName()]
        target = object_target[self.sender().objectName()]
        value  = origin.value()*object_ratio[self.sender().objectName()]
        target.setText("{}".format(value) if value % 1 == 0 else "{:.2f}".format(value))

    def ck_value_change(self):
        object_origin = {
            "ck_print": self.ck_print
        }
        object_target = {
            "ck_print": self.sb_ratio
        }
        origin = object_origin[self.sender().objectName()]
        target = object_target[self.sender().objectName()]
        target.setEnabled(origin.checkState())


if __name__ == '__main__':
    app    = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
