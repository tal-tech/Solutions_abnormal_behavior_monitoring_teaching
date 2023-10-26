# -*- coding: utf-8 -*-
import os
import glob
import tensorflow as tf
import torchvision.transforms as transforms
import cv2
from utils import *
import torchvision.models as models
import torch
import time
import torch.nn as nn
from resnet import ResNetLW,Bottleneck
from parse_model import Body_parsing
from urllib.request import urlretrieve
import urllib
import cv2

import random

class Nudity_process(object):

    def __init__(self):
        #body parse model
        self.IMG_SCALE = 1. / 255
        self.IMG_MEAN = np.array([0.485, 0.456, 0.406]).reshape((1, 1, 3))
        self.IMG_STD = np.array([0.229, 0.224, 0.225]).reshape((1, 1, 3))
        self.sess, self.graph = self.get_bodyparse_sess()
        self.parse_obj = Body_parsing(self.sess,self.graph)
        # #lower arm mask model

        self.lowermask_models = ResNetLW(Bottleneck, [3, 8, 36, 3], num_classes=7)
        state_dict = torch.load(os.path.join(os.path.dirname(__file__),'models/rf_lw152_person.pth.tar'))
        self.lowermask_models.load_state_dict(state_dict)
        self.lowermask_models.eval().cuda()
        #binary classify model
        self.bin_model = models.resnet18(pretrained=False)
        fc_features = self.bin_model.fc.in_features
        # 替换最后的全连接层， 改为训练2类
        self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        self.local_transforms = transforms.Compose([
            transforms.Scale(256),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            self.normalize,
        ])
        self.bin_model.fc = nn.Linear(fc_features, 2)
        checkpoint = torch.load(os.path.join(os.path.dirname(__file__),'models/model_best_8_22.pth.tar'))
        self.bin_model.load_state_dict(checkpoint['state_dict'], strict=False)
        self.bin_model.eval().cuda()

    def sigmoid(self,x):
        return 1 / (1 + np.exp(-x))


    def get_bodyparse_sess(self):
        tmp_graph = tf.Graph()
        gpu_options1 = tf.GPUOptions(per_process_gpu_memory_fraction=0.1)
        config1 = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options1)
        config1.gpu_options.allow_growth = True
        sess = tf.Session(config=config1, graph=tmp_graph)
        return sess, tmp_graph

    def get_all_images(self,path):
        filelist = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(('.jpg', '.png', 'jpeg')):
                    filelist.append(os.path.join(root, name))
        print('There are %d images' % (len(filelist)))
        return filelist

    def binary_classify(self,image):

        bin_classinput = self.local_transforms(image)
        outputs = self.bin_model(bin_classinput.expand([1, 3, 224, 224]).cuda())
        outputs = outputs.cpu().detach().numpy()
        outputs_list = self.sigmoid(outputs)[0].tolist()
        pred = outputs_list.index(max(outputs_list))

        return pred, outputs_list

    def prepare_img(self,img):
        return (img * self.IMG_SCALE - self.IMG_MEAN) / self.IMG_STD

    def lower_arm_mask(self,image):
        image = cv2.resize(image,(320,240))
        orig_size = image.shape[:2][::-1]
        img_inp = torch.tensor(self.prepare_img(image).transpose(2, 0, 1)[None]).float().cuda()
        segm = self.lowermask_models(img_inp)[0].data.cpu().numpy().transpose(1, 2, 0)
        segm = cv2.resize(segm, orig_size, interpolation=cv2.INTER_CUBIC)
        segm = segm.argmax(axis=2).astype(np.uint8)
        bin_segm = segm == 4
        bin_segm = (bin_segm * 1) == False
        lowerarm_bin_segm = (bin_segm * 1)

        return lowerarm_bin_segm

    def body_parse(self,image):

        ori_image = cv2.resize(image, (320, 240))

        # Run detection
        parsing_ = self.parse_obj.parse(ori_image)

        return parsing_[0][0, :, :, 0]

    def inference(self,image,h,w,c):
        raw_data = np.array(image)
        raw_image = raw_data.reshape(h, w, c)
        ori_image = raw_image.astype('uint8')
        ori_image = cv2.cvtColor(ori_image, cv2.COLOR_BGR2RGB)

        ori_image = Image.fromarray(np.array(ori_image))
        pred, outputs_list = self.binary_classify(ori_image)


        lowerarm_bin_segm = self.lower_arm_mask(np.array(ori_image))
        parsing = self.body_parse(np.array(ori_image))

        tmp = np.array(parsing * lowerarm_bin_segm)


        flag = pixel_count_v2(tmp)


        # 二分类判定为非裸露的再使用凯哥的方法计算一遍
        if pred == 0 and outputs_list[pred] <= 0.8:
            if flag == 1:
                final_flag = 1
            else:
                final_flag = 0
        elif pred == 0 and outputs_list[pred] > 0.8:
            final_flag = 0
        elif pred == 1 and outputs_list[pred] >= 0.6:
            final_flag = 1
        elif pred == 1 and outputs_list[pred] < 0.6:
            if flag == 1:
                final_flag = 1
            else:
                final_flag = 0

        #final_flag == 0 代表裸露，final_flag == 1代表不裸露
        final_flag = int(final_flag == 0)

        return final_flag


if __name__ == '__main__':

    img_dir = '/workspace/nudity/qingqing/data'
    imgs = glob.glob('{}/**/**.jpg'.format(img_dir))
    start = time.time()
    nudity_process = Nudity_process()
    end = time.time()
    print ('load model cost:',end-start)


    while True:
        #img = random.choice(imgs)
        image_url = 'http://dawn.shareurl.facethink.com/asr-mp4/asr-mp46m.jpg?AWSAccessKeyId=X6V5Q9VB9FEUBKJQOMJ3&Expires=1711953251&Signature=gwyrip8IGUEFv0xE7BBRDp%2F5VGA%3D'

        start = time.time()
        resp =  urllib.request.urlopen(image_url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        #image = cv2.imread('/workspace/nudity/nudity_qingqing_code/asr-mp46m.jpg')

        shape = image.shape
        pred = nudity_process.inference(image.flatten(),shape[0],shape[1],shape[2])
        end = time.time()

        print ('inference time:',end-start)
        print (pred)





