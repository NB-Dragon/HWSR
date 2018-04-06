import cv2
import numpy as np


class RectChar(object):
    def __init__(self, no_line=False, cut=True, join=True, print=False, threshold_binary=120, threshold_ratio=0.3):
        self.charList = []
        self.no_line  = no_line #Turn to True if you want to delete the meaningless line
        self.cut      = cut     #Turn to True if you need more accurate
        self.join     = join    #Turn to True so that some rectangle can be joined together
        self.print    = print   #Turn to True if you sure that the characters were printed
        self.threshold_binary = threshold_binary
        self.threshold_ratio  = threshold_ratio

    def get_shape(self, image):
        return image.shape

    def get_gray_value(self, bgr):
        return (bgr[2] * 30 + bgr[1] * 59 + bgr[0] * 11) / 100

    def get_gray_image(self,image):
        h, w, channel = self.get_shape(image)
        gray_image = np.zeros((h, w, channel), np.uint8)
        for nY in range(h):
            for nX in range(w):
                gray = self.get_gray_value(image[nY, nX])
                gray_image[nY, nX, :] = [gray, gray, gray]
        return gray_image

    def get_binary_image(self, image):
        h, w, channel = self.get_shape(image)
        binary_image = np.zeros((h, w, channel), np.uint8)
        for nY in range(h):
            for nX in range(w):
                if image[nY, nX, 0] < self.threshold_binary:
                    binary_image[nY, nX, :] = [0, 0, 0]
                else:
                    binary_image[nY, nX, :] = [255, 255, 255]
        return binary_image

    def get_small_size(self, image):
        black_index = np.where(image < 1)
        top         = min(black_index[0])
        bottom      = image.shape[0] - 1 - max(black_index[0])
        left        = min(black_index[1])
        right       = image.shape[1] - 1 - max(black_index[1])
        return [top, bottom, left, right]

    def get_char_list(self, image):
        result_image = image.copy()
        if self.no_line is True:
            kernel       = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4))
            result_image = cv2.morphologyEx(result_image, cv2.MORPH_CLOSE, kernel)
        self.analysis(result_image)
        if self.join is True:
            self.join_image()
        return self.charList

    def analysis(self, image):
        row_list = self.get_row_list(image)
        for i in range(len(row_list)):
            roi_image = image[row_list[i][0]:row_list[i][1], 0:self.get_shape(image)[1]]
            col_list  = self.getColList(roi_image)
            for j in range(len(col_list)):
                if self.cut is True:
                    temp = self.get_small_size(image[row_list[i][0]:row_list[i][1], col_list[j][0]:col_list[j][1]])
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
            if self.print is True and min_k < self.threshold_ratio:
                continue     #The rectangle is probably a word in the print
            while i+1 < len(self.charList):
                rect_temp = self.charList[i+1]
                if rect_temp[2] < rect[0] and rect_temp[1] > rect[3]:
                    break     #The two rectangles are not at the same row
                if rect_temp[0] - rect[2] > length_y:
                    break     #The two rectangles have a long distance
                if self.print is True:
                    l_x = abs(rect_temp[2] - rect_temp[0])
                    l_y = abs(rect_temp[3] - rect_temp[1])
                    if max(l_y, l_x)/min(l_y, l_x)-1 < self.threshold_ratio:
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
    image        = cv2.imread("汉字_手写.jpg")
    from Detect import Detect
    rect_char    = RectChar()
    gray_image   = rect_char.get_gray_image(image)
    binary_image = rect_char.get_binary_image(gray_image)
    result_list  = rect_char.get_char_list(binary_image)
    image_list   = []
    
    rect_temp = None
    for rect in result_list:
        if rect_temp is not None and (rect_temp[2] > rect[0] and rect_temp[1] < rect[3]):
            image_list.append(None)
        image_list.append(image[rect[1]:rect[3], rect[0]:rect[2], :]/255)
        rect_temp = rect
    detect = Detect()
    result = detect.find_class(image_list)
    print(result)
