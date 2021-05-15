from PIL import Image
import cv2
import numpy as np
import os

def draw_circle_center(dir):
    path = dir + 'fake_B_.png'                  #原图
    p_path = dir + 'plant.png'
    p_path2 = dir + 'plant2.png'
    img = Image.open(path)
    img_p = img.crop((512, 0, 1024, 512))
    img_p.save(p_path)
    img_p.save(p_path2)
    blur(p_path)                                 #模糊

    img_p = Image.open(p_path)
    img_o = img.crop((0,0,512,512))
    im_1 = np.array(img_o)
    im_2 = np.array(img_p)
    im = np.concatenate((im_1, im_2), axis=1)
    image = Image.fromarray(im)
    image.save(dir + 'fake_B_p.png', quality=100)   #模糊后的图像贴到原图上

    img1 = cv2.imread(dir + 'plant.png')
    img2 = cv2.imread(dir + 'plant2.png')
    sp = img1.shape
    for x in range(sp[0]):
        for y in range(sp[1]):
            rgb = img1[x, y]
            if (rgb[1] > 60 and rgb[1] < 150) :  #点植
                img1[x, y] = (0,0,0)
            else:
                img1[x, y] = (255, 255, 255)
            rgb2 = img2[x,y]
            if (rgb2[2] < 110):                  #群植
                img2[x, y] = (0,0,0)
            else:
                img2[x, y] = (255, 255, 255)
    os.remove(dir + 'plant2.png')
    cv2.imwrite(dir + 'plant_2' + '.png', img2)             #群植 灰度图
    cv2.imwrite(dir + 'plant_1' + '.png', img1)             #点植 灰度图

    con2 = cv2.imread(dir + 'plant_1' + '.png')
    con3 = cv2.imread(dir + 'plant_2' + '.png')
    for i, con in enumerate([con2, con3]):              #遍历点植和群植图
        p = cv2.imread(dir+'fake_B'+'_p.png')           #读模糊后的平面图
        gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cont in contours[1:]:
            area = cv2.contourArea(cont, False)         #计算轮廓面积
            if (area < 50) :
                continue                                #面积过小，忽略
            box = min_box(cont)
            cv2.polylines(con, [box], True, (0, 0, 0), 1)
            rect = cv2.minAreaRect(cont)
            width = rect[1][0]; height = rect[1][1]     #宽、高
            x_ = int(rect[0][0]); y_ = int(rect[0][1])  #中心点坐标
            b = p[y_, x_, 0]                          # opencv颜色顺序是BGR
            g = p[y_, x_, 1]
            r = p[y_, x_, 2]
            rgb = (r, g, b)                             #中心点坐标处的rgb
            if (i == 0):                                #点植
                width_ = int(width / 40) + 1            #width方向的网格数
                height_ = int(height / 40) + 1          #height方向的网格数
            elif (i == 1):                              #群植
                width_ = int(width / 24) + 1            #width方向的网格数
                height_ = int(height / 24) + 1          #height方向的网格数
            for m in range(1, width_ + 1):
                for n in range(1, height_ + 1):                                             #遍历mxn网格，求中心点
                    if (width_ == 1) and (height_ == 1):
                        x_0 = x_ ; y_0 = y_
                        cv2.circle(con, (x_0, y_0), 1, (0, 0, 255), -1)                     # 植物图都画圆
                        if (i== 0):                                                         # 点植
                            p[y_0, x_0+512] = (0,255,0)
                        elif (i == 1):                                                      # 群植
                            p[y_0, x_0 + 512] = (0, 0, 255)
                    else:
                        x_1 = (box[1][0][0] - box[0][0][0])//height_ *(n-1) + box[0][0][0]  # 辅助点
                        x_2 = (box[1][0][0] - box[0][0][0])//height_ *n + box[0][0][0]      # 辅助点
                        x_3 = (box[3][0][0] - box[0][0][0])//width_ *(m-1) + box[0][0][0]   # 辅助点
                        x_4 = (box[3][0][0] - box[0][0][0]) //width_ * m + box[0][0][0]     # 辅助点
                        x_5 = x_1 + (x_3 - box[0][0][0])                                    # 辅助点
                        x_6 = x_2 + (x_4 - box[0][0][0])                                    # 辅助点
                        y_1 = box[0][0][1] - (box[0][0][1] - box[1][0][1])//height_ *(n-1)  # 辅助点
                        y_2 = box[0][0][1] - (box[0][0][1] - box[1][0][1]) //height_ * n    # 辅助点
                        y_3 = box[0][0][1] + (box[3][0][1] - box[0][0][1]) //width_ * (m-1) # 辅助点
                        y_4 = box[0][0][1] + (box[3][0][1] - box[0][0][1]) //width_ * m     # 辅助点
                        y_5 = y_3 - (box[0][0][1] - y_2)                                    # 辅助点
                        y_6 = y_4 - (box[0][0][1] - y_2)                                    # 辅助点
                        x_0 = (x_5 + x_6)//2
                        y_0 = (y_5 + y_6)//2                                                      #（x_0,y_0）为第（m,n）网格的中心点
                        if ((p[y_0,x_0,1]>60 and p[y_0,x_0,1]<140) or (p[y_0,x_0,2]<110)):        #(m,n)网格中心点色块是否符合点植或孤植rgb
                            cv2.circle(con, (x_0, y_0), 1, (0, 0, 255), -1)                       #圆大小标为1
                            if (i == 0):  # 点植
                                p[y_0, x_0 + 512] = (0, 255, 0)
                            elif (i == 1):  # 群植
                                p[y_0, x_0 + 512] = (0, 0, 255)
            cv2.imwrite(dir + 'plant_'+str(i+1)+'.png', con)                                # 分布存储点植和群植灰度图
            cv2.imwrite(dir+'fake_B'+'_p.png', p)                                           # 存储修改后的原图
