import os
import numpy as np
from PIL import Image

def getCenter(mask):
    ##获取mask的中心点坐标
    up, down, left ,right = 0, 0, len(mask[0]), 0
    up_flag = False
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            if mask[i][j][0] != 0:
                if not up_flag and i > up:
                    up = i
                    up_flag = True
                if i > down:  down = i
                if j < left:  left = j
                if j > right: right = j
    #print(left,right,up,down)
    return ((left+right)//2,(up+down)//2)

def getbbox(mask):
    ##获取mask的坐标
    up, down, left ,right = 0, 0, len(mask[0]), 0
    up_flag = False
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            if mask[i][j][0] != 0:
                if not up_flag and i > up:
                    up = i
                    up_flag = True
                if i > down:  down = i
                if j < left:  left = j
                if j > right: right = j
    return left, up, right, down

def hist_match(source, template):
    # Code borrow from:
    # https://stackoverflow.com/questions/32655686/histogram-matching-of-two-images-in-python-2-x
    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()
    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                            return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    return interp_t_values[bin_idx].reshape(oldshape)

def img_resize(img,size):
    tmp_img = Image.fromarray(img)
    tmp = tmp_img.resize(size)
    result = np.array(tmp,dtype='uint8')
    return result

def Landmarks_filter(landmarks):
    lmk = landmarks.tolist()
    result = []
    for i in range(len(lmk)):
        #if lmk[i][2] > -10:
        result.append([lmk[i][0],lmk[i][1]])
    result = np.array(result,dtype=int)
    return result

def matchDir(args):
    faceAlist = []
    faceBlist = []
    maskAlist = []
    maskBlist = []
    
    files = os.listdir(args.ori_rootpath)
    files.sort()
    
    for orifile in files:
        faceB_path = os.path.join(args.ori_rootpath, orifile)
        if os.path.splitext(faceB_path)[1] != '.jpg' and os.path.splitext(faceB_path)[1] != '.png': 
            continue

        faceA_flag = False
        for swpfile in os.listdir(args.swp_rootpath): 
            faceA_path = os.path.join(args.swp_rootpath, swpfile)
            if os.path.splitext(faceA_path)[1] != '.jpg' and os.path.splitext(faceA_path)[1] != '.png': 
                continue
            elif swpfile.split('_')[-2] != orifile.split('.')[0].split('_')[-1]:
                continue
            else:
                faceA_flag = True
                break

        dfa_faceA_flag = False
        for dfa_faceA_file in os.listdir(args.maskA_path): 
            dfa_faceA_path = os.path.join(args.maskA_path, dfa_faceA_file)
            if os.path.splitext(dfa_faceA_path)[1] != '.jpg' and os.path.splitext(dfa_faceA_path)[1] != '.png': 
                continued
            elif swpfile.split('_')[-2] != dfa_faceA_file.split('_')[-2]:
                continue
            else:
                dfa_faceA_flag = True
                break

        dfa_faceB_flag = False
        for dfa_faceB_file in os.listdir(args.maskB_path): 
            dfa_faceB_path = os.path.join(args.maskB_path, dfa_faceB_file)
            if os.path.splitext(dfa_faceB_path)[1] != '.jpg' and os.path.splitext(dfa_faceB_path)[1] != '.png': 
                continue
            elif swpfile.split('_')[-2] != dfa_faceB_file.split('.')[0].split('_')[-1]:
                continue
            else:
                dfa_faceB_flag = True
                break


        if faceA_flag and dfa_faceA_flag and dfa_faceB_flag:
            faceAlist.append(faceA_path)
            faceBlist.append(faceB_path)
            maskAlist.append(dfa_faceA_path)
            maskBlist.append(dfa_faceB_path)
            
    return faceAlist,faceBlist,maskAlist,maskBlist