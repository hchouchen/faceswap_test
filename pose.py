#!/usr/bin/env python3
# coding: utf-8

__author__ = 'cleardusk'

"""
The pipeline of 3DDFA prediction: given one image, predict the 3d face vertices, 68 landmarks and visualization.

[todo]
1. CPU optimization: https://pmchojnacki.wordpress.com/2018/10/07/slow-pytorch-cpu-performance
"""

import torch
import torchvision.transforms as transforms
import mobilenet_v1
import numpy as np
import cv2
import face_alignment
from utils.ddfa import ToTensorGjz, NormalizeGjz
import scipy.io as sio
from utils.inference import parse_roi_box_from_landmark, crop_img, predict_68pts, predict_dense, get_colors, get_aligned_param
from utils.estimate_pose import parse_pose
from utils.render import crender_colors
import torch.backends.cudnn as cudnn

STD_SIZE = 120
def getPoses(img_ori):
    # 1. load pre-tained model
    checkpoint_fp = 'models/phase1_wpdc_vdc.pth.tar'
    arch = 'mobilenet_1'

    checkpoint = torch.load(checkpoint_fp, map_location=lambda storage, loc: storage)['state_dict']
    model = getattr(mobilenet_v1, arch)(num_classes=62)  # 62 = 12(pose) + 40(shape) +10(expression)

    model_dict = model.state_dict()
    # because the model is trained by multiple gpus, prefix module should be removed
    for k in checkpoint.keys():
        model_dict[k.replace('module.', '')] = checkpoint[k]
    model.load_state_dict(model_dict)
    cudnn.benchmark = True
    model = model.cuda()
    model.eval()

    tri = sio.loadmat('visualize/tri.mat')['tri']
    transform = transforms.Compose([ToTensorGjz(), NormalizeGjz(mean=127.5, std=128)])

    alignment_model = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False,device='cuda')

    # face alignment model use RGB as input, result is a tuple with landmarks and boxes
    preds = alignment_model.get_landmarks(img_ori[:, :, ::-1])
    pts_2d_68 = preds[0]
    roi_box = parse_roi_box_from_landmark(pts_2d_68.T)

    img = crop_img(img_ori, roi_box)
    # import pdb; pdb.set_trace()

    # forward: one step
    img = cv2.resize(img, dsize=(STD_SIZE, STD_SIZE), interpolation=cv2.INTER_LINEAR)
    input = transform(img).unsqueeze(0)
    with torch.no_grad():
        input = input.cuda()
        param = model(input)
        param = param.squeeze().cpu().numpy().flatten().astype(np.float32)

    # 68 pts
    pts68 = predict_68pts(param, roi_box)

    roi_box = parse_roi_box_from_landmark(pts68)
    img_step2 = crop_img(img_ori, roi_box)
    img_step2 = cv2.resize(img_step2, dsize=(STD_SIZE, STD_SIZE), interpolation=cv2.INTER_LINEAR)
    input = transform(img_step2).unsqueeze(0)
    with torch.no_grad():
        input = input.cuda()
        param = model(input)
        param = param.squeeze().cpu().numpy().flatten().astype(np.float32)

    P, pose = parse_pose(param)        
    # dense face 3d vertices
    vertices = predict_dense(param, roi_box)
    colors = get_colors(img_ori, vertices)
    # aligned_param = get_aligned_param(param)
    # vertices_aligned = predict_dense(aligned_param, roi_box)
    # h, w, c = 120, 120, 3
    h, w, c = img_ori.shape
    img_2d = crender_colors(vertices.T, (tri - 1).T, colors[:, ::-1], h, w)
    img_2d = img_2d[:,:,::-1]
        
    return img_2d, pose