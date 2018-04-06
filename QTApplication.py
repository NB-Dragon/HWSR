import sys
import cv2
from SplitImage import RectChar
from Detect import Detect
from PyQt5 import QtWidgets, QtCore, QtGui
from QTApplication.mainwindow import Ui_MainWindow


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.detect         = Detect()
        self.original_image = None
        self.after_image    = None

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        self.lbl_resize_event()

    def get_pix_from_mat(self, image, width, height):
        h, w, channel = image.shape
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(image, w, h, w * channel, QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(image)
        image = image.scaled(width-4, height-4, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        return image

    def get_boolean(self, check_state):
        return True if check_state != 0 else False

    def open_image(self):
        target              = self.lbl_image_origin
        file_name           = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files(*.jpeg *.png *.jpg)")
        self.original_image = cv2.imread(file_name[0])
        image               = self.get_pix_from_mat(self.original_image, target.width(), target.height())
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

    def btn_click(self):
        object_target      = self.lbl_image_after
        object_origin_name = self.sender().objectName()

        no_line = self.get_boolean(self.ck_noline.checkState())
        cut     = self.get_boolean(self.ck_cut.checkState())
        join    = self.get_boolean(self.ck_join.checkState())
        p_font  = self.get_boolean(self.ck_print.checkState())
        threshold_binary = int(self.sb_binary_value.text())
        threshold_ratio  = float(self.sb_ratio_value.text())

        rect_char    = RectChar(no_line, cut, join, p_font, threshold_binary, threshold_ratio)
        gray_image   = rect_char.get_gray_image(self.original_image)
        binary_image = rect_char.get_binary_image(gray_image)
        result_list  = rect_char.get_char_list(binary_image)
        result_image = None

        if object_origin_name == "btn_split":
            print("123")
        elif object_origin_name == "btn_gray":
            self.after_image = gray_image
            result_image = self.get_pix_from_mat(gray_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_brinary":
            self.after_image = binary_image
            result_image = self.get_pix_from_mat(binary_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_location":
            result_image = self.original_image.copy()
            for char in result_list:
                cv2.rectangle(result_image, (char[0], char[1]), (char[2], char[3]), (0, 0, 255))
            self.after_image = result_image
            result_image = self.get_pix_from_mat(result_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_recognize":
            image_list = []
            rect_temp  = None
            for rect in result_list:
                if rect_temp is not None and (rect_temp[2] > rect[0] and rect_temp[1] < rect[3]):
                    image_list.append(None)
                image_list.append(binary_image[rect[1]:rect[3], rect[0]:rect[2], :] / 255)
                rect_temp = rect
            result_str = self.detect.find_class(image_list)
            self.text_result.setText(result_str)
            print(result_str)

        if result_image is not None:
            object_target.setPixmap(result_image)

    def lbl_resize_event(self):
        lbl = [self.lbl_image_origin, self.lbl_image_after]
        img = [self.original_image, self.after_image]

        for index in range(len(lbl)):
            if img[index] is None: continue
            target = lbl[index]
            image  = self.get_pix_from_mat(img[index],target.width(),target.height())
            target.setPixmap(image)


if __name__ == '__main__':
    app    = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
