from PIL import Image
# from analyze import config
# import util
import numpy as np
import cv2
from analyze import process
# import process
from scipy.spatial import distance as dist
import math

# 返回除水和建筑以外不同要素面积


def area(dir, ele):
    path = dir+ele+'.png'
    img = Image.open(path)
    img_map = img.load()
    w, h = img.size

    area = 0
    for x in range(w):
        for y in range(h):
            img_rgb = img_map[x, y]
            r = img_rgb[0]
            g = img_rgb[1]
            b = img_rgb[2]
            if r != 255 and g != 255 and b != 255:
                area += 1

    return area

# 返回水和建筑的面积


def cvarea(dir, ele, only_p):
    pass


# 返回计算区域中心点横纵坐标
def centerpoint(dir, ele, only_p):
    max = {'water': [0, 0, 0], 'mountain': [0, 0, 0],
           'main': [0, 0, 0], 'landscape': [0, 0, 0]}
    if ele == 'main' or ele == 'other' or ele == 'landscape':
        path = dir+'arcs.png'
    else:
        path = dir+ele+'.png'

    con = cv2.imread(path)
    p = cv2.imread(dir+'plan.png')

    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours[1:]:
        area = cv2.contourArea(cont, False)  # 计算轮廓面积
        M = cv2.moments(cont)  # 计算第一条轮廓的各阶矩,字典形式
        if M['m00'] == 0:
            continue
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        b = p[center_y, center_x, 0]  # opencv颜色顺序是BGR
        g = p[center_y, center_x, 1]
        r = p[center_y, center_x, 2]
        rgb = (r, g, b)
        if process.define_ele(ele, rgb, only_p) or ele == 'water' or ele == 'mountain':
            if area > max[ele][0]:
                max[ele][0] = area
                max[ele][1] = center_x
                max[ele][2] = center_y

    # cv2.circle(con, (max[ele][1], max[ele][2]), 1, (255, 0, 255), -1)  # 绘制出中心点

    return (int(max[ele][1]), int(max[ele][2]))


# 返回要素边界中心点横纵坐标
def center_bound(dir, only_p):
    path = dir+'arcs.png'
    con = cv2.imread(path)
    p = cv2.imread(dir+'plan.png')

    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    boun = contours[0]
    for cont in contours[1:]:
        area = cv2.contourArea(cont, False)  # 计算轮廓面积
        if area < 50:
            continue
        M = cv2.moments(cont)
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        b = p[center_y, center_x, 0]  # opencv颜色顺序是BGR
        g = p[center_y, center_x, 1]
        r = p[center_y, center_x, 2]
        rgb = (r, g, b)
        if process.define_ele('main', rgb, only_p):
            if area > max_area:
                max_area = area
                boun = cont

    box = process.min_box(boun)
    if dis(box[0][0], box[1][0]) > dis(box[1][0], box[2][0]):
        return ((box[0][0][0]+box[1][0][0])//2, (box[0][0][1]+box[1][0][1])//2)
    else:
        return ((box[1][0][0]+box[2][0][0])//2, (box[1][0][1]+box[2][0][1])//2)


# 返回主峰最高点
def top_mountain(dir, only_p, ifmulti):
    p_path = dir+'mountain.png'
    # h_path = dir+'gh.png' if only_p else dir+'plan.png'
    h_path = dir+'gh.png' if ifmulti else dir+'plan.png'
    process.blur(p_path, 9)
    p = Image.open(p_path)
    h = Image.open(h_path)
    p_map = p.load()
    h_map = h.load()

    w, hei = p.size

    top_h = 0
    top_x = 0
    top_y = 0

    for x in range(w-2):
        for y in range(hei-2):
            rgb_p = p_map[x, y]
            rgb_h = h_map[x, y]
            height = rgb_h[0]+rgb_h[1]+rgb_h[2] if only_p else rgb_h[2]
            if process.define_ele('mountain', rgb_p, only_p):
                if height > top_h:
                    top_h = height
                    top_x = x
                    top_y = y
    return (top_x, top_y)


# 通过三组坐标计算角度，如果min_90为true，则计算正弦，即大于90度就返回补角
def angle(p_a, p_b, p_c, min_90=False):
    a = dis(p_b, p_c)
    b = dis(p_a, p_c)
    c = dis(p_a, p_b)
    cos = (b**2+c**2-a**2)/(2*b*c)
    if min_90:
        sin = math.sqrt(1-cos**2)
        ang = np.arcsin(sin)*180/np.pi
    else:
        ang = np.arccos(cos)*180/np.pi
    return ang


# 计算两组坐标的距离
def dis(p1, p2):
    D = dist.euclidean(p1, p2) * 18*8/512  # 计算连线距离m
    return D


# 计算三要素的视线夹角：1.计算山到水到主厅的夹角——景观格局  2.计算主峰正对大厅的角度，如果为0则主峰正对大厅
def angle_ele(dir, only_p, center, left, right, draw, ifmulti=True):
    p = {'center': [0, 0], 'left': [0, 0], 'right': [0, 0]}
    min_90 = False
    for x in [center, left, right]:
        if x == 'landscape_bound':
            min_90 = True
            p[x] = center_bound(dir, only_p)
        elif x == 'top_mountain':
            p[x] = top_mountain(dir, only_p, ifmulti)
        else:
            p[x] = centerpoint(dir, x, only_p)

    # 如果出现要素缺少就直接返回error角度
    for x in [center, left, right]:
        if p[x][0] == 0 and p[x][1] == 0:
            errorangle = 0 if min_90 else 0
            return errorangle
    if draw:
        con = cv2.imread(dir+'plan.png')
        for r in range(1, 5):
            cv2.circle(con, p[center], 50*r, (0, 0, 0), 1)
        cv2.circle(con, p[center], 5, (255, 0, 255), -1)  # 绘制出中心点
        cv2.circle(con, p[left], 5, (255, 0, 255), -1)  # 绘制出中心点
        cv2.circle(con, p[right], 5, (255, 0, 255), -1)  # 绘制出中心点
        cv2.line(con, p[left], p[center], (255, 0, 255), 2)  # 绘制中心点连线
        cv2.line(con, p[center], p[right], (255, 0, 255), 2)  # 绘制中心点连线
        cv2.imwrite(dir+left+center+right+'.png', con)
    return angle(p[center], p[left], p[right], min_90)


# 计算两个要素之间的距离
def dis_sight(dir, ele1, ele2, only_p):
    ele1_p = centerpoint(
        dir, ele1, only_p) if ele1 != 'top_mountain' else top_mountain(dir, only_p)
    ele2_p = centerpoint(
        dir, ele2, only_p) if ele2 != 'top_mountain' else top_mountain(dir, only_p)
    return dis(ele1_p, ele2_p)


if __name__ == '__main__':
    # print(angle(2, 1, 1.732))
    dir = './results/multi_512/test_latest_iter800/images/1_'
    point = center_bound(dir, True)
    print(point)
    angle = angle_ele(dir, True, 'water', 'main',
                      'mountain', True)
    print(angle)
