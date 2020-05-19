# faceswap_test
## 
 `python main.py [--options_lowpass true or false] [--option_coladj true or false] [--ori_rootpath ] [--swp_rootpath ] [--maskA_path] [--maskB_path ] [--save_path ]`  
   
其中  
options_lowpass为是否使用低通滤波  
option_coladj为是否使用颜色校正  
--ori_rootpath是原始图片faceA文件夹目录  
--maskA_path是原始图片faceA对应3ddfa生成的mask的文件夹目录  
--swp_rootpath为换脸后图片faceB文件夹目录  
--maskB_path为换脸后图片经过3ddfa生成的mask文件夹目录  
--save_path为存储图片的地址    
  
  
例如:   
`python main.py --options_lowpass true --optino_coladj true --ori_root r'../data/raw_fullbody/280' --maskA_path r'../data/3ddfa_faceA_280' --swp_rootpath r'../data/swp-rnr/280/aligned' --maskB_path r'../data/3ddfa_faceB_280' --save_path r'../data/result_lowpass_280'`
