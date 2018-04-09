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
        self.pix_map        = None
        self.start          = False
        self.start_point    = None
        self.end_point      = None

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        self.lbl_resize_event()

    def eventFilter(self, a0: 'QObject', a1: 'QEvent'):
        if a0 == self.lbl_image_origin:
            if self.original_image is None or self.start is False:
                return False
            if a1.type()   == QtCore.QEvent.MouseButtonPress and a1.button() == 1:
                self.start_point = a1.pos()
                return True
            elif a1.type() == QtCore.QEvent.MouseMove and self.start_point is not None:
                self.end_point   = a1.pos()
                self.draw_rect(a0, self.pix_map, a0.size(), self.pix_map.size(), self.start_point, self.end_point)
                return True
            elif a1.type() == QtCore.QEvent.MouseButtonPress and a1.button() == 2:
                self.start_point = None
                a0.setToolTip("")
                a0.setCursor(QtCore.Qt.ArrowCursor)
                a0.setPixmap(self.pix_map)
                return True
            elif a1.type() == QtCore.QEvent.MouseButtonRelease and a1.button() == 1:
                if self.start_point is not None:
                    self.end_point      = a1.pos()
                    distance = self.start_point - self.end_point
                    if abs(distance.y() * distance.x()) < 50: return True
                    location            = self.draw_rect(a0, self.pix_map, a0.size(), self.pix_map.size(), self.start_point, self.end_point)
                    self.original_image = self.original_image[location[1]:location[3], location[0]:location[2], :]
                    self.pix_map        = self.get_pix_from_mat(self.original_image, a0.width(), a0.height())
                    self.start_point    = None
                    self.end_point      = None
                    self.start          = False
                    a0.setToolTip("")
                    a0.setCursor(QtCore.Qt.ArrowCursor)
                    a0.setPixmap(self.pix_map)
                return True
            else:
                return False
        else:
            return self.eventFilter(a0, a1)

    def draw_rect(self, q_object, pix_map, out_size, in_size, start_x_y, end_x_y):
        distance = start_x_y-end_x_y
        min_x    = min(start_x_y.x(), end_x_y.x())
        min_y    = min(start_x_y.y(), end_x_y.y())
        width    = abs(distance.x())
        height   = abs(distance.y())
        temp     = pix_map.copy()
        painter  = QtGui.QPainter(temp)
        painter.setPen(QtGui.QColor(255, 0, 0))
        v_space, h_space = self.clac_space(out_size, in_size)
        ratio_x  = self.original_image.shape[1]/pix_map.width()
        ratio_y  = self.original_image.shape[0]/pix_map.height()
        painter.drawRect(min_x - h_space, min_y - v_space, width, height)
        painter.end()
        q_object.setPixmap(temp)
        return [int((min_x - h_space)*ratio_x), int((min_y - v_space)*ratio_y), int((min_x - h_space+width)*ratio_x), int((min_y - v_space+height)*ratio_y)]

    def clac_space(self, out_size, in_size):
        v_space = (out_size.height()-in_size.height())//2
        h_space = (out_size.width()-in_size.width())//2
        return v_space, h_space

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
        file_name           = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Image File(*.jpeg *.jpg *.png *.bmp)")
        if file_name[0] == "": return
        self.original_image = cv2.imread(file_name[0])
        self.pix_map        = self.get_pix_from_mat(self.original_image, target.width(), target.height())
        target.setPixmap(self.pix_map)

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

        if object_origin_name == "btn_split":
            if self.original_image is None: return
            self.start = True
            self.lbl_image_origin.setCursor(QtCore.Qt.CrossCursor)
            self.lbl_image_origin.setToolTip("通过鼠标左键拖动即可完成裁剪，中途可右键取消")
            return

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

        if object_origin_name   == "btn_gray":
            self.after_image = gray_image
            result_image     = self.get_pix_from_mat(gray_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_brinary":
            self.after_image = binary_image
            result_image     = self.get_pix_from_mat(binary_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_location":
            result_image     = self.original_image.copy()
            for char in result_list:
                cv2.rectangle(result_image, (char[0], char[1]), (char[2], char[3]), (0, 0, 255))
            self.after_image = result_image
            result_image     = self.get_pix_from_mat(result_image, object_target.width(), object_target.height())
        elif object_origin_name == "btn_recognize":
            image_list       = []
            rect_temp        = None
            for rect in result_list:
                if rect_temp is not None and (rect_temp[2] > rect[0] and rect_temp[1] < rect[3]):
                    image_list.append(None)
                image_list.append(gray_image[rect[1]:rect[3], rect[0]:rect[2], :] / 255)
                rect_temp = rect
            result_str       = self.detect.find_class(image_list)
            self.text_result.setText(result_str)

        if result_image is not None:
            object_target.setPixmap(result_image)

    def lbl_resize_event(self):
        lbl = [self.lbl_image_origin, self.lbl_image_after]
        img = [self.original_image, self.after_image]

        for index in range(len(lbl)):
            if img[index] is None: continue
            target = lbl[index]
            image  = self.get_pix_from_mat(img[index], target.width(), target.height())
            if index == 0: self.pix_map = image
            target.setPixmap(image)


if __name__ == '__main__':
    app    = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
