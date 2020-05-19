# faceswap_test
## 
 `python main.py [--options_lowpass true or false] [--options_coladj true or false] [--swp_rootpath ''] [--ori_rootpath ''] [--maskA_path ''] [--maskB_path ''] [--save_path '']`  
   
其中  
options_lowpass为是否使用低通滤波  
options_coladj为是否使用颜色校正  
--ori_rootpath是原始图片faceB文件夹目录  
--maskB_path为换脸后图片faceB经过3ddfa生成的mask文件夹目录 
--swp_rootpath为换脸后图片faceA文件夹目录  
--maskA_path是原始图片faceA对应3ddfa生成的mask的文件夹目录  
--save_path为存储图片的地址    
  
  
例如:   
`python main.py --options_lowpass true --options_coladj true --ori_root r'../data/raw_fullbody/280' --maskB_path r'../data/3ddfa_faceB_280' --swp_rootpath r'../data/swp-rnr/280/aligned' --maskA_path r'../data/3ddfa_faceA_280' --save_path r'../data/result_lowpass_280'`

### 图片命名示例（与data文件夹里图片的命名规则完全一致）  
swp-img(faceA即换脸后图片):yaw_-0.04_yaw_0.0_10051712212800XXXXHFSD00025rotresize_0314_0.png  
maskA(faceA经过3ddfa输出的mask):yaw_-0.04_yaw_0.0_10051712212800XXXXHFSD00025rotresize_0314_0.png  
ori-img(faceB即原始图片):10051712212800XXXXHFSD00025rotresize_0234.jpg  
maskB(faceB经过3ddfa输出的mask):10051712212800XXXXHFSD00025rotresize_0234.jpg   
  
需要保证:  
1. ori-img和maskB图片名最后是帧序号  
2. swp-img和maskA图片名最后是帧序号_0  
如果不满足也没关系，只需修改utils.py中的matchDir即可，如有问题请及时联系作者  

### pose接口 
```
from pose import getPoses
mask, pose = getPoses(img)
```
其中mask为mask图片，pose为[yaw, pitch, roll]
