from re import T
import numpy as np
import cv2
import os
from PIL import Image
from analyze import process
from analyze import calculation
# import process
# import calculation
from scipy.spatial import distance as dist


# 算出建筑中心坐标，长宽高和旋转的角度和长度等
def point(only_p, picdir, unitydir, gh=False):
    dir = picdir
    path = dir+'arcs.png'
    con = cv2.imread(path)
    p = cv2.imread(dir+'plan.png')
    # p = cv2.imread(dir+'p.jpg')
    h = cv2.imread(dir+'height.png') if gh else cv2.imread(dir+'plan.png')
    datas = []

    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cont in contours[1:]:
        data = []
        area = cv2.contourArea(cont, False)  # 计算轮廓面积
        if area < 50:
            continue
        M = cv2.moments(cont)
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        b = p[center_y, center_x, 0]  # opencv颜色顺序是BGR
        g = p[center_y, center_x, 1]
        r = p[center_y, center_x, 2]
        height = h[center_y, center_x, 0]
        rgb = (r, g, b)
        # 计算角度
        box = process.min_box(cont)
        # 如果最左边是长边,就是计算顺时针第一个轮廓点和最后一个轮廓点
        x = dist.euclidean(box[0][0], box[1][0])
        y = dist.euclidean(box[1][0], box[2][0])
        # print(box[0][0], box[1][0], box[1][0], box[2][0])
        trans = False
        if x >= y:
            x1 = box[0][0][0]
            y1 = box[0][0][1]
            x2 = box[3][0][0]
            y2 = box[3][0][1]
        # 相反,就是计算最后一个轮廓点和顺时针第二个轮廓点
        else:
            if box[0][0][1] < box[1][0][1]:
                x1 = box[3][0][0]
                y1 = box[3][0][1]
                x2 = box[2][0][0]
                y2 = box[2][0][1]
            else:
                x1 = box[1][0][0]
                y1 = box[1][0][1]
                x2 = box[0][0][0]
                y2 = box[0][0][1]
            t = y
            y = x
            x = t
            # 代表旋转过
            trans = True
        if y1 == y2:
            angle = 90 if trans else 0
        else:
            angle = calculation.angle((x1, y1), (x2, y2), (x1, y2), True)

            angle = 0-angle if x2 > x1 else angle
        if process.define_ele('main', rgb, only_p):
            data.append("main")
        elif process.define_ele('landscape', rgb, only_p):
            data.append("landscape")
        else:
            data.append("other")
        data.append(center_x)
        data.append(center_y)
        data.append(x)
        data.append(y)
        data.append(height)
        data.append(angle)
        datas.append(data)

    print(len(datas))
    # print(datas)
    f = open(unitydir+"_arcs.txt", 'w')
    for s in datas:
        for j in range(7):
            content = str(s[j])
            f.writelines(content)
            # print(content)
            f.write('\n')
    f.close()


# 通过圆心算出植物冠幅半径和高度
def trees_info(x, y, ifdot, p_map):
    plant = {'radius': 0, 'height': 0}
    tree = 'dot' if ifdot else 'group'
    left = 0
    right = 0
    top = 0
    bottom = 0
    left_end = False
    right_end = False
    top_end = False
    bottom_end = False
    # 求中心点周边数点高度的平均值
    for i in range(0, 3):
        for j in range(0, 3):
            seq = 1 if ifdot else 0
            plant['height'] += p_map[x+i-1, y+j-1][seq]
    plant['height'] = int(plant['height']/9)

    for i in range(1, 512):
        # 判断左边边界
        if x-i > 0 and not left_end:
            rgb_l = p_map[x-i, y]
            if process.define_ele(tree, rgb_l):
                left += 1
            else:
                left_end = True
        # 判断右边边界
        if x+i < 512 and not right_end:
            rgb_r = p_map[x+i, y]
            if process.define_ele(tree, rgb_r):
                right += 1
            else:
                right_end = True
        # 判断下边边界
        if y-i > 0 and not bottom_end:
            rgb_b = p_map[x, y-i]
            if process.define_ele(tree, rgb_b):
                bottom += 1
            else:
                bottom_end = True
        # 判断上边边界
        if y+i < 512 and not top_end:
            rgb_t = p_map[x, y+i]
            if process.define_ele(tree, rgb_t):
                top += 1
            else:
                top_end = True
        # 如果所有边界都判断完了就退出
        if left_end and right_end and bottom_end and top_end:
            break

    # 扩大点植和种植的冠幅半径
    expand = 6 if ifdot else 2
    plant['radius'] = int((left+right+top+bottom)/4)+expand

    # 返回半径及高度
    return plant


# 处理种植设计，画出植物圆心
def draw_circle_center(dir, name, input_dir):
    path = dir + name  # 原图
    p_path = dir + 'plant.png'
    p_path2 = dir + 'plant2.png'
    img = Image.open(path)
    img_p = img.crop((512, 0, 1024, 512))
    img_p.save(p_path)
    img_p.save(p_path2)
    process.blur(p_path)  # 模糊
    img.save(dir+'ori.png')  # 原图备份

    # 模糊后的植载原生成图
    img_p = Image.open(p_path)

    img1 = cv2.imread(dir + 'plant.png')
    img2 = cv2.imread(dir + 'plant2.png')
    sp = img1.shape
    for x in range(sp[0]):
        for y in range(sp[1]):
            rgb = img1[x, y]
            if (rgb[1] > 60 and rgb[1] < 150):  # 点植
                img1[x, y] = (0, 0, 0)
            else:
                img1[x, y] = (255, 255, 255)
            rgb2 = img2[x, y]
            if (rgb2[2] < 110):  # 群植
                img2[x, y] = (0, 0, 0)
            else:
                img2[x, y] = (255, 255, 255)
    os.remove(dir + 'plant2.png')
    cv2.imwrite(dir + 'plant_2' + '.png', img2)  # 群植 灰度图
    cv2.imwrite(dir + 'plant_1' + '.png', img1)  # 点植 灰度图

    con2 = cv2.imread(dir + 'plant_1' + '.png')
    con3 = cv2.imread(dir + 'plant_2' + '.png')

    # 新建一个白色图片画处理过后的植载方案
    new_plant = np.zeros((512, 512, 3), np.uint8)
    new_dot = np.zeros((512, 512, 3), np.uint8)
    new_group = np.zeros((512, 512, 3), np.uint8)
    # fill the image with white
    new_dot.fill(255)
    new_group.fill(255)

    p_map = img_p.load()

    for i, con in enumerate([con2, con3]):  # 遍历点植和群植图
        gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cont in contours[1:]:
            area = cv2.contourArea(cont, False)  # 计算轮廓面积
            if (area < 50):
                continue  # 面积过小，忽略
            box = process.min_box(cont)
            cv2.polylines(con, [box], True, (0, 0, 0), 1)
            rect = cv2.minAreaRect(cont)

            width = dist.euclidean(box[0][0], box[1][0])  # x0到x1的距离
            height = dist.euclidean(box[0][0], box[3][0])  # x0到x3的距离
            p_0 = box[0][0]
            p_1 = box[1][0]
            p_3 = box[3][0]

            x_0 = int(rect[0][0])
            y_0 = int(rect[0][1])  # 中心点坐标

            seg_scale = 40 if i == 0 else 28
            width_ = int(width / seg_scale) + 1  # width方向的网格数
            height_ = int(height / seg_scale) + 1  # height方向的网格数

            if width_ < 3 and height_ < 3 and ((width >= height and width < 1.3*height) or (width < height and 1.3*width > height)):
                width_ = 1
                height_ = 1

            if (width_ == 1) and (height_ == 1):
                '''在新图上画出植物圆'''
                plant = trees_info(x_0, y_0, True if i == 0 else False, p_map)
                color = (255, plant['height'], 255) if i == 0 else (255, 255,
                                                                    plant['height'])
                canvas = new_dot if i == 0 else new_group
                # 画出冠幅圆圈
                cv2.circle(canvas, (x_0, y_0), plant['radius'], color, -1)
                # 画出圆心
                canvas[y_0, x_0] = (
                    255, 0, 255) if i == 0 else (255, 255, 0)

                '''在对应灰度图上画出圆心'''
                cv2.circle(con, (x_0, y_0), 1,
                           (0, 0, 255), -1)

            else:
                direction01 = {'x': (p_1[0]-p_0[0]) /
                               width_, 'y': (p_1[1]-p_0[1])/width_}
                direction03 = {'x': (p_3[0]-p_0[0]) /
                               height_, 'y': (p_3[1]-p_0[1])/height_}
                # 求出x0第一个网格的第一个基准点坐标
                base_x = (p_0[0]+direction01['x']+p_0[0]+direction03['x'])/2
                base_y = (p_0[1]+direction01['y']+p_0[1]+direction03['y'])/2
                canvas = new_dot if i == 0 else new_group
                color = (255, plant['height'], 255) if i == 0 else (
                    255, 255, plant['height'])

                for m in range(width_):
                    for n in range(height_):
                        center_x = int(
                            base_x+m*direction01['x']+n*direction03['x'])
                        center_y = int(
                            base_y+m*direction01['y']+n*direction03['y'])
                        plant_rgb = p_map[center_x, center_y]
                        # 所有网格点画绿
                        cv2.circle(con, (center_x, center_y), 1,
                                   (0, 255, 0), -1)
                        if process.define_ele('dot' if i == 0 else 'group', plant_rgb):
                            '''命中在新图上画出植物圆'''
                            plant = trees_info(
                                center_x, center_y, True if i == 0 else False, p_map)
                            # 画出冠幅圆圈
                            cv2.circle(canvas, (center_x, center_y),
                                       plant['radius'], color, -1)
                            # 画出圆心
                            canvas[center_y, center_x] = (
                                255, 0, 255) if i == 0 else (255, 255, 0)

                            '''命中就在原轮廓图上画出圆心，红色表示'''
                            cv2.circle(con, (center_x, center_y), 1,
                                       (0, 0, 255), -1)  # 圆大小标为1
        # 分别存储点植和群植灰度图
        cv2.imwrite(dir + 'plant_'+str(i+1)+'.png', con)

    # 合并点植和群植，并借助输入图片在第三通道画上边界
    input = cv2.imread(input_dir+name)
    new_plant[:, :, 0] = input[:, :, 1]
    new_plant[:, :, 1] = new_dot[:, :, 1]
    new_plant[:, :, 2] = new_group[:, :, 2]
    cv2.imwrite(dir+'plant'+'.png', new_plant)

    img_plan = img.crop((0, 0, 512, 512))
    img_plan = np.array(img_plan)
    for x in range(512):
        for y in range(512):
            if input[x, y, 0] > 250:
                img_plan[x, y, 2] = 255
    # 不知道为啥存储的图片r,b会通道互换？新建一个图片帮助img_plan交换r与b通道信息
    new_img = np.zeros((512, 512, 3), np.uint8)
    new_img[:, :, 2] = img_plan[:, :, 0]
    img_plan[:, :, 0] = img_plan[:, :, 2]
    img_plan[:, :, 2] = new_img[:, :, 2]
    cv2.imwrite(dir+name, img_plan)
    # combine = np.concatenate((img_plan, new_plant), axis=1)
    # # 存储修改后的原图
    # cv2.imwrite(dir+name, combine)


if __name__ == "__main__":

    # picdir = "E:\\PYTHON\\datasets\\plants\\test"
    # unitydir = "E:\\Bigsoftware\\unity\\project\\garden\\Assets\\Demo\\test_"
    # process.find_cont(picdir+'plan.png', ['arcs'], picdir, False, if256=False)
    # point(False, picdir, unitydir)

    dir = "E:/PYTHON/datasets/plants/test1/"
    draw_circle_center(dir)
