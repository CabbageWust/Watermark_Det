import cv2
import numpy as np
import os
import glob
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement


class ImgGenerator(object):
    def __init__(self, p_mask='./assets/mask.jpg', p_number = './assets/number', p_fore='./fore', p_back='./back',
                 p_save_pic='imgs', p_save_xml='xmls', num=100):
        super(ImgGenerator, self).__init__()
        self.mask = p_mask
        self.path_fore = p_fore
        self.path_back = p_back
        self.path_number = p_number
        self.path_savepic = p_save_pic
        self.path_savexml = p_save_xml
        if not os.path.exists(self.path_savexml):
            os.mkdir(self.path_savexml)
        if not os.path.exists(self.path_savepic):
            os.mkdir(self.path_savepic)
        self.num = num
        self._make_fore()
        self._merge()

    def _make_fore(self):
        mask_path = self.mask
        logo = cv2.imread(mask_path)
        re = logo.copy()
        path = self.path_fore
        if not os.path.exists(path):
            os.mkdir(path)
        number_list = glob.glob(self.path_number + '/*.jpg')
        ID_length_list = np.random.randint(5, 10, self.num)
        for i, id_len in enumerate(ID_length_list):
            for j in range(id_len):
                number_pic = cv2.imread(number_list[np.random.randint(0, 10)])  # select one pic by rand
                re[-35:, 114 + j*21:114 + (j + 1)*21, :] = number_pic
            PicName = str(i) + ".jpg"
            savepath = os.path.join(path, PicName)
            cv2.imwrite(savepath, re)

        # label for pic

    def _merge(self):
        back_path = self.path_back
        fore_path = self.path_fore
        save_pic_path = self.path_savepic
        save_xml_path = self.path_savexml
        if not os.path.exists(save_pic_path):
            os.mkdir(save_pic_path)
        fore_list = glob.glob(fore_path + "/*.jpg")
        back_list = glob.glob(back_path + "/*.jpg")
        scale = len(fore_list) // len(back_list)
        back_list = (back_list * (scale + 1))[:len(fore_list)]
        count = 0
        for i in range(len(back_list)):
            fore = cv2.imread(fore_list[i])
            h_f, w_f = fore.shape[:2]
            # scale_h, scale_w = 16.13, 3.942
            back = cv2.imread(back_list[i])
            back_resize = cv2.resize(back, (1280, 2020))
            mask = cv2.split(cv2.cvtColor(fore, cv2.COLOR_BGR2HSV))[2]

            re = back_resize.copy()
            for c in range(3):
                re[10:135, 945:1270, c] = np.where(mask[:, :] > 15,
                                                   fore[:, :, c],
                                                   back_resize[10:135, 945:1270, c])

            PicName = str(count) + '_' + os.path.basename(back_list[i])
            count += 1
            print(count)
            savepath = os.path.join(save_pic_path, PicName)

            cv2.imwrite(savepath, re)

            # write xml
            XmlName = PicName.replace('.jpg', '.xml')
            save_xml = os.path.join(save_xml_path, XmlName)
            x_min, y_min, x_max, y_max = 943, 8, 1272, 72
            obj = [x_min, y_min, x_max, y_max]
            self.write_xml([obj], PicName, re, save_xml)

    @staticmethod
    def write_xml(objs,PicName,Image,save_path):

        imagexml = ElementTree()
        annotation = Element("annotation")  # xml title
        SubElement(annotation, "folder").text = "path"
        SubElement(annotation, "filename").text = PicName
        imagexml._setroot(annotation)
        sp = Image.shape
        width, height, pic_depth = sp[1], sp[0], sp[2]
        item1 = Element("size")
        SubElement(item1, "width").text = str(width)
        SubElement(item1, "height").text = str(height)
        SubElement(item1, "depth").text = str(pic_depth)
        annotation.append(item1)

        for obj in objs:
            item2 = Element("object")
            SubElement(item2, "name").text = "11"
            SubElement(item2, "difficult").text = "0"
            annotation.append(item2)
            item3 = Element("bndbox")
            SubElement(item3, "xmin").text = str(int(obj[0]))  # xmin
            SubElement(item3, "ymin").text = str(int(obj[1]))  # ymin
            SubElement(item3, "xmax").text = str(int(obj[2]))  # xmax
            SubElement(item3, "ymax").text = str(int(obj[3]))  # ymax
            item2.append(item3)

        imagexml.write(save_path, "utf-8")






if __name__ == '__main__':

    generator = ImgGenerator()






