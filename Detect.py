#coding=utf-8
import numpy as np
import os
import caffe


class Detect(object):
    def __init__(self, image_path=None):
        self.unicode_path = "util/character.txt"
        self.net_file     = "caffeNet/GoogleNet_HCCR.prototxt"
        self.caffe_model  = "caffeModel/GoogleNet_HCCR.caffemodel"
        self.image_path   = image_path
        self.net          = caffe.Net(self.net_file, self.caffe_model, caffe.TEST)
        self.classList    = list()
        self.read_class(self.unicode_path)

    def get_crop_image(self, image_path, img_name):
        image = caffe.io.load_image(os.path.join(image_path, img_name))
        black_index = np.where(image < 1)
        min_x = min(black_index[0])
        max_x = max(black_index[0])
        min_y = min(black_index[1])
        max_y = max(black_index[1])
        return image[min_x:max_x, min_y:max_y, :]

    def read_class(self, filename):
        file  = open(filename)
        lines = file.readlines()
        for line in lines:
            self.classList.append(line[line.find(" ") + 1:-1])

    def find_class(self, image_list=list(), top_k=1):
        transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2, 0, 1))
        transformer.set_raw_scale('data', 255)

        if len(image_list) == 0:
            if self.image_path is None:
                return "识别错误：找不到识别区域，请重新调整"
            image_names = os.listdir(self.image_path)
            for img_name in image_names:
                image_list.append(self.get_crop_image(self.image_path, img_name))

        result = ""
        assert len(image_list) > 0
        for image in image_list:
            if image is None:
                result = result+"\n"
                continue
            self.net.blobs['data'].data[...] = transformer.preprocess('data', image)
            self.net.forward()
            label_index = self.net.blobs['loss'].data[0].flatten().argsort()[-1:-top_k-1:-1]
            result = result+self.classList[int(label_index)]
        return result


if __name__ == '__main__':
    detect = Detect("images")  #A directoy which contains all of the single character
    detect.find_class()
