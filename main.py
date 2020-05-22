import cv2,os
import torch
import argparse
import face_alignment
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage import io
from scipy import signal
from umeyama import umeyama
from utils.ddfa import str2bool
from util import *
from util import matchDir


def main(args):
    landmarks_A_list = []
    landmarks_B_list = []
    A_size = [0,0]
    B_size = [0,0]
    
    faceAlist,faceBlist,maskAlist,maskBlist = matchDir(args)
    
    for index in range(len(faceAlist)):
        if abs(float(faceAlist[index].split('_')[1])) > 0.8:
            face = io.imread(args.profile_img_path)
            faceA = face[:,:,:3]
        else:
            faceA = io.imread(faceAlist[index])

        faceB = io.imread(faceBlist[index])
        if A_size[0] == 0:
            A_size = [len(faceA[0]),len(faceA)]
            B_size = [len(faceB[0]),len(faceB)]

        faceA = img_resize(faceA,A_size)
        faceB = img_resize(faceB,B_size)

        fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._3D, flip_input=False,device=args.mode)
        try:
            landmarks_A = fa.get_landmarks(faceA)[0][17:]
            landmarks_B = fa.get_landmarks(faceB)[0][17:]
        except:
            print('no face')
            continue

        landmarks_A_list.append(landmarks_A)
        landmarks_B_list.append(landmarks_B)
        

    if args.options_lowpass:
        landmarks_A_tensor = torch.tensor(landmarks_A_list)#[75,68,3]->[68,3,75]
        landmarks_A_tensor = landmarks_A_tensor.permute(1,2,0)
        landmarks_A_array = landmarks_A_tensor.numpy().tolist()
        landmarks_B_tensor = torch.tensor(landmarks_B_list)
        landmarks_B_tensor = landmarks_B_tensor.permute(1,2,0)
        landmarks_B_array = landmarks_B_tensor.numpy().tolist()

        b,a = signal.butter(2,0.1,'lowpass')
        for i in range(len(landmarks_A_array)):
            for j in range(len(landmarks_A_array[0])-1):
                landmarks_A_array[i][j] = signal.filtfilt(b,a,landmarks_A_array[i][j][:])
                landmarks_B_array[i][j] = signal.filtfilt(b,a,landmarks_B_array[i][j][:])

        landmarks_A_tensor = torch.tensor(landmarks_A_array)
        landmarks_A_tensor = landmarks_A_tensor.permute(2,0,1) #[68,3,75]->[75,68,3]
        landmarks_A_list = np.array(landmarks_A_tensor.numpy(),dtype=int)
        landmarks_B_tensor = torch.tensor(landmarks_B_array)
        landmarks_B_tensor = landmarks_B_tensor.permute(2,0,1)
        landmarks_B_list = np.array(landmarks_B_tensor.numpy(),dtype=int)
    

    for index in range(len(faceAlist)):
        faceB = io.imread(faceBlist[index])
        maskimg_rnr_B = io.imread(maskBlist[index])

        if abs(float(faceAlist[index].split('_')[1])) > 0.8:
            face = io.imread(args.profile_img_path)
            faceA = face[:,:,:3]
            maskimg_rnr_A = io.imread(args.profile_mask_path)
        else:
            faceA = io.imread(faceAlist[index])
            maskimg_rnr_A = io.imread(maskAlist[index])

        faceA = img_resize(faceA,A_size)
        faceB = img_resize(faceB,B_size)
        maskimg_rnr_A = img_resize(maskimg_rnr_A,A_size)
        maskimg_rnr_B = img_resize(maskimg_rnr_B,B_size)
       
        landmarks_A = Landmarks_filter(landmarks_A_list[index])
        landmarks_B = Landmarks_filter(landmarks_B_list[index])

        kernel = np.ones((7,7),np.uint8)
        hullA = cv2.convexHull(np.array(landmarks_A)).astype(np.int32)
        mask_fa_A = cv2.drawContours(np.zeros_like(faceA),[hullA],0,(1,1,1),-1)
        mask_fa_A = cv2.dilate(mask_fa_A,kernel)

        hullB = cv2.convexHull(np.array(landmarks_B)).astype(np.int32)
        mask_fa_B = cv2.drawContours(np.zeros_like(faceB),[hullB],0,(1,1,1),-1)
        mask_fa_B = cv2.dilate(mask_fa_B,kernel)
     
        maskA = np.zeros(mask_fa_A.shape,dtype='uint8')
        maskB = np.zeros(mask_fa_B.shape,dtype='uint8')
        for i in range(len(maskA)):
            for j in range(len(maskA[0])):
                if mask_fa_A[i,j,0] == 0 or maskimg_rnr_A[i,j,0] == 0:
                    maskA[i,j] = [0,0,0]
                else:
                    maskA[i,j] = mask_fa_A[i,j]
        for i in range(len(maskB)):
            for j in range(len(maskB[0])):
                if mask_fa_B[i,j,0] == 0 or maskimg_rnr_B[i,j,0] == 0:
                    maskB[i,j] = [0,0,0]
                else:
                    maskB[i,j] = mask_fa_B[i,j]

        M = umeyama(np.array(landmarks_A), np.array(landmarks_B), True)[0:2]

        try:
            if M[0][0] == 1: pass
        except:
            continue

        if args.options_coladj:
            bboxA = getbbox(maskA)
            bboxB = getbbox(maskB)
            aligned_faceA = faceA[bboxA[1]:bboxA[3],bboxA[0]:bboxA[2]]
            aligned_faceB = faceB[bboxB[1]:bboxB[3],bboxB[0]:bboxB[2]]

            matched_faceA = hist_match(aligned_faceA,aligned_faceB)
            matched_faceA = np.array(matched_faceA,dtype='uint8')

            faceA[bboxA[1]:bboxA[3],bboxA[0]:bboxA[2]] = matched_faceA
       
        warp_faceA = cv2.warpAffine(maskA*faceA, M, (faceB.shape[1],faceB.shape[0])) 
        warp_maskA = cv2.warpAffine(maskA, M, (faceB.shape[1],faceB.shape[0]))

        if args.options_coladj:
            hsv_faceA = cv2.cvtColor(warp_faceA,cv2.COLOR_BGR2LAB)
            hsv_faceB = cv2.cvtColor(maskB*faceB,cv2.COLOR_BGR2LAB)
            for i in range(len(hsv_faceA)):
                for j in range(len(hsv_faceA[0])):
                    if maskB[i,j,0] != 0:
                        hsv_faceA[i,j,0] = int(hsv_faceB[i,j,0]*0.5+hsv_faceA[i,j,0]*0.5)
                        hsv_faceA[i,j,1] = int(hsv_faceB[i,j,1]*0.5+hsv_faceA[i,j,1]*0.5)
            col_faceA = cv2.cvtColor(hsv_faceA,cv2.COLOR_LAB2BGR)
        else:
            col_faceA = warp_faceA

        warp_maskA = cv2.erode(warp_maskA,kernel)
        swp_face = cv2.seamlessClone(col_faceA, faceB, 255*warp_maskA, getCenter(warp_maskA), cv2.NORMAL_CLONE)

        wfp_2d_img = os.path.join(args.save_path, faceAlist[index].split('/')[-1])
        print(wfp_2d_img)
        cv2.imwrite(wfp_2d_img, swp_face[:, :, ::-1])
        print(index)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='faceswap inference pipeline')
    parser.add_argument('--options_kalman', default='true', type=str2bool, help='whether to use kalman filter')
    parser.add_argument('--options_lowpass', default='true', type=str2bool, help='whether to use lowpass filter')
    parser.add_argument('--options_coladj', default='true', type=str2bool, help='whether to use color adjustment')
    parser.add_argument('--ori_rootpath', default=r'../data/raw_fullbody/280', type=str, help='dir to origin image')
    parser.add_argument('--swp_rootpath', default=r'../data/swp-rnr/280/aligned', type=str, help='dir to swap image')
    parser.add_argument('--save_path', default=r'../data/result_lowpass_280', type=str, help='dir to save image')
    parser.add_argument('--profile_img_path', default=r'../data/1.png', type=str, help='dir of profile img')
    parser.add_argument('--profile_mask_path', default=r'../data/3ddfamask_1.png', type=str, help='dir of profile mask')
    parser.add_argument('--maskA_path', default=r'../data/3ddfa_faceA_280', type=str)
    parser.add_argument('--maskB_path', default=r'../data/3ddfa_faceB_280', type=str)
    parser.add_argument('--mode', default='cuda', type=str, help='cpu or cuda')

    args = parser.parse_args()
    main(args)
