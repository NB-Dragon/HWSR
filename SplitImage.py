import cv2
import numpy as np
from Detect import Detect


def show_picture(image):
    window_name = "Image Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, 0, 0)
    cv2.imshow(window_name, image)
    cv2.waitKey(0)


class RectChar(object):
    def __init__(self, image):
        self.i_image  = image.copy()
        self.charList = []
        self.no_line  = False  #Turn to True if you want to delete the meaningless line
        self.smaller  = True   #Turn to True if you need more accurate
        self.join     = True   #Turn to True so that some rectangle can be joined together
        self.print    = True   #Turn to True if you sure that the characters are printed

    def get_width(self):
        return self.i_image.shape[1]

    def get_height(self):
        return self.i_image.shape[0]

    def get_image(self):
        return self.i_image

    def get_char_list(self, threshold=120):
        self.to_grey()
        self.wb_color(threshold)
        if self.no_line is True:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4))
            self.i_image = cv2.morphologyEx(self.i_image, cv2.MORPH_CLOSE, kernel)
        self.analysis()
        if self.join is True:
            self.join_image()
        return self.charList

    def get_grey_value(self, bgr):
        return (bgr[2] * 30 + bgr[1] * 59 + bgr[0] * 11) / 100

    def get_small_size(self, image):
        black_index = np.where(image < 1)
        top    = min(black_index[0])
        bottom = image.shape[0]-1-max(black_index[0])
        left   = min(black_index[1])
        right  = image.shape[1]-1-max(black_index[1])
        return [top, bottom, left, right]

    def to_grey(self):
        for nY in range(self.get_height()):
            for nX in range(self.get_width()):
                grey = self.get_grey_value(self.i_image[nY, nX])
                self.i_image[nY, nX, 0] = grey
        self.i_image = self.i_image[:, :, 0]

    def wb_color(self, level):
        for nY in range(self.get_height()):
            for nX in range(self.get_width()):
                if self.i_image[nY, nX] < level:
                    self.i_image[nY, nX] = 0
                else:
                    self.i_image[nY, nX] = 255

    def analysis(self):
        row_list = self.get_row_list(self.i_image)
        for i in range(len(row_list)):
            roi_image = self.i_image[row_list[i][0]:row_list[i][1], 0:self.get_width()]
            col_list  = self.getColList(roi_image)
            for j in range(len(col_list)):
                if self.smaller is True:
                    temp = self.get_small_size(self.i_image[row_list[i][0]:row_list[i][1], col_list[j][0]:col_list[j][1]])
                    temp = [col_list[j][0]+temp[2], row_list[i][0]+temp[0], col_list[j][1]-temp[3], row_list[i][1]-temp[1]]
                else:
                    temp = [col_list[j][0], row_list[i][0], col_list[j][1], row_list[i][1]]
                self.charList.append(temp)

    def join_image(self):
        for i in range(len(self.charList)):
            if i >= len(self.charList):
                break         #The length of charList will be getting smaller

            rect     = self.charList[i]
            length_x = abs(rect[2]-rect[0])
            length_y = abs(rect[3]-rect[1])
            min_k    = max(length_y, length_x)/min(length_y, length_x)-1
            while i+1 < len(self.charList):
                rect_temp = self.charList[i+1]
                if rect_temp[2] < rect[0] and rect_temp[1] > rect[3]:
                    break     #The two rectangles are not at the same row
                if rect_temp[0] - rect[2] > length_y:
                    break     #The two rectangles have a long distance
                if self.print is True:
                    l_x = abs(rect_temp[2] - rect_temp[0])
                    l_y = abs(rect_temp[3] - rect_temp[1])
                    if max(l_y, l_x)/min(l_y, l_x)-1 < 0.3:
                        break #The rectangle is probably a word in the print

                top    = min(rect[1], rect_temp[1])
                bottom = max(rect[3], rect_temp[3])
                left   = min(rect[0], rect_temp[0])
                right  = max(rect[2], rect_temp[2])
                l_x    = abs(right-left)
                l_y    = abs(bottom-top)
                temp_k = max(l_x, l_y)/min(l_x, l_y)-1
                if temp_k < min_k :
                    min_k    = temp_k
                    rect     = [left, top, right, bottom]
                    length_y = bottom - top
                    self.charList[i] = rect
                    self.charList.remove(rect_temp)
                else:
                    break

    def get_row_list(self, roi):
        length       = roi.shape[0]
        start_index  = 0
        start        = False
        each_row     = []
        row_list     = []

        for nY in range(length):
            each_row.append(0 in roi[nY, :])

        for nY in range(length):
            if each_row[nY] ^ start:
                if start is False:
                    start = True
                    start_index = nY
                else:
                    start = False
                    row_list.append([start_index, nY])
        return row_list

    def getColList(self, roi):
        length      = roi.shape[1]
        start_index = 0
        start       = False
        each_col    = []
        col_list    = []

        for nX in range(length):
            each_col.append(0 in roi[:, nX])

        for nX in range(length):
            if each_col[nX] ^ start:
                if start is False:
                    start = True
                    start_index = nX
                else:
                    start = False
                    col_list.append([start_index, nX])
        return col_list


if __name__ == '__main__':
    image      = cv2.imread("汉字_印刷.jpg")
    simple     = RectChar(image)
    charList   = simple.get_char_list(120)
    image_list = []
    image_show = True

    if image_show is True:
        for char in charList:
            cv2.rectangle(image, (char[0], char[1]), (char[2], char[3]), (0, 0, 255))
        show_picture(image)
        cv2.imwrite("test_out.jpg", image)
    else:
        for char in charList:
            image_list.append(image[char[1]:char[3], char[0]:char[2], :]/255)
        detect = Detect()
        detect.find_class(image_list)
