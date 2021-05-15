from typing import Tuple
import cv2
import numpy as np
from PIL import Image
import os
from numpy.core import numeric

from scipy.spatial import distance as dist
from analyze import visualization
from analyze import config
# import config
# import visualization
# from analyze import util
# from analyze import calculation


# hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
# low_hsv = np.array([11, 43, 46])
# high_hsv = np.array([25, 255, 255])
# mask = cv2.inRange(hsv, lowerb=low_hsv, upperb=high_hsv)
# cv2.imshow("test", mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# cv2.fillPoly(h, [box], color=(int(b), int(b), int(b)))  # 填充轮廓线
# cv2.circle(h, (center_x, center_y), 1, (255, 255, 255), -1)  # 绘制出中心点
# cv2.polylines(con, [box], True, (0, 255, 0), 1)  # 绘制出轮廓线
# cv2.line(orig, (int(xA), int(yA)), (int(xB), int(yB)),color, 2) #绘制中心点连线
# D = dist.euclidean((xA, yA), (xB, yB)) #计算连线距离


# 通过轮廓图统计各要素数量或面积,coutarea=True则是算各要素面积比例
def total(dir, only_p, coutarea, if256):
    con_path = dir+'arcs.png'
    p_path = dir+'plan.png'
    s = ['water', 'mountain', 'corridor', 'second',
         'inter', 'main', 'landscape', 'other']
    ele_num = {'water': 0, 'mountain': 0, 'corridor': 0, 'second': -1,
               'inter': 0, 'main': 0, 'landscape': 0, 'other': 0}  # 主厅
    ele_num_sum = []
    if coutarea:
        site = count_site(p_path, dir, only_p, if256)

    con = cv2.imread(con_path)
    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    p = cv2.imread(p_path)
    '''
    计算建筑数量
    '''
    for cont in contours[1:]:
        area = cv2.contourArea(cont, False)  # 计算轮廓面积
        minarea = 10 if if256 else 40
        if area < minarea:
            continue
        M = cv2.moments(cont)  # 计算第一条轮廓的各阶矩,字典形式

        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        b = p[center_y, center_x, 0]  # opencv颜色顺序是BGR
        g = p[center_y, center_x, 1]
        r = p[center_y, center_x, 2]
        rgb = (r, g, b)
        for arc in s[5:]:
            if define_ele(arc, rgb, only_p):
                ele_num[arc] += area if coutarea else 1
                break

    '''
    计算其他要素数量
    '''
    for x in s[:5]:
        con = cv2.imread(dir+x+'.png')
        gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cont in contours[1:]:
            area = cv2.contourArea(cont, False)  # 计算轮廓面积
            ele_num[x] += area if coutarea else 1

    for x in ele_num.values():
        ele_num_sum.append(x)

    if coutarea:
        ele_num_sum = [x/site for x in ele_num_sum]

    return ele_num_sum


# 中值模糊
def blur(path, i=5):
    src = cv2.imread(path)
    src = cv2.medianBlur(src, i)
    cv2.imwrite(path, src)


# 返回轮廓的最小外接矩形四个坐标
def min_box(cont):
    rect = cv2.minAreaRect(cont)
    # cv2.boxPoints可以将轮廓点转换为四个角点坐标
    box = cv2.boxPoints(rect)
    # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
    startidx = box.sum(axis=1).argmin()
    box = np.roll(box, 4-startidx, 0)
    # 在原图上画出预测的外接矩形
    box = box.reshape((-1, 1, 2)).astype(np.int32)
    return box


# 通过像素识别元素
def define_ele(str, rgb, only_p=False):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    f = False
    if only_p:
        if str == 'water' and r < 20 and g > 240 and b > 240:
            f = True
        elif str == 'corridor' and r > 200 and g < 80 and b < 80:
            f = True
        elif str == 'mountain' and r > 30 and r < 130 and g < 100 and b < 100:
            f = True
        elif str == 'inter' and r > 80 and r < 160 and g > 40 and g < 100 and b > 190:
            f = True
        elif str == 'main' and r > 210 and g > 100 and g < 200 and b > 20 and b < 100:
            f = True
        elif str == 'landscape' and r > 130 and r < 215 and g > 205 and b > 205:
            f = True
        elif str == 'other' and r < 50 and g < 50 and b < 50:
            f = True
        elif str == 'site' and not((r > 200 and g > 200 and b > 200) or (r < 20 and g > 240 and b > 240)):
            f = True
    else:
        if str == 'water' and r > 200 and g > 200 and b < 50:
            f = True
        elif str == 'corridor' and r > 200 and g < 80:
            f = True
        elif str == 'second' and r > 200 and g > 80 and g < 200:
            f = True
        elif str == 'mountain' and r < 80 and g < 80:
            f = True
        elif str == 'inter' and r > 80 and r < 200 and g > 200 and b < 20:
            f = True
        elif str == 'main' and r > 90 and r < 190 and g < 70:
            f = True
        elif str == 'landscape' and r < 70 and g > 90 and g < 190:
            f = True
        elif str == 'other' and r > 90 and r < 190 and g > 90 and g < 190:
            f = True
        elif str == 'site' and not (r > 200 and g > 200 and b > 200):
            f = True
        elif str == 'dot' and g > 60 and g < 150:
            f = True
        elif str == 'group' and r < 110:
            f = True
    return f


# 通过像素识别元素，并返回元素标准rgb值，在规整建筑重新绘制在平面图上可以用到
def define_arc(rgb, only_p):
    if only_p:
        if define_ele('other', rgb, only_p):
            rgb = (0, 0, 0)
        elif define_ele('main', rgb, only_p):
            rgb = (255, 150, 59)
        elif define_ele('landscape', rgb, only_p):
            rgb = (181, 255, 254)
    else:
        if define_ele('other', rgb, only_p):
            rgb = (127, 127, rgb[2])
        elif define_ele('main', rgb, only_p):
            rgb = (127, 0, rgb[2])
        elif define_ele('landscape', rgb, only_p):
            rgb = (0, 127, rgb[2])
    return rgb


# 通过p_path识别山体，将img_path上的山体像素复制到h_path上
def copy_moutain(h_path, img_path, p_path, only_p):
    h = Image.open(h_path)  # 要粘贴的高度图片
    p = Image.open(p_path)  # 识别山石的平面
    ori = Image.open(img_path)  # 原始山石平面
    w, hei = ori.size
    p_map = p.load()
    h_map = h.load()
    o_map = ori.load()
    for x in range(w-512 if w > 512 else w):
        for y in range(hei):
            rgb_p = p_map[x, y]
            if define_ele('mountain', rgb_p, only_p):  # 山石
                h_map[x, y] = o_map[x+512 if w > 512 else x, y]
    h.save(h_path)


# 通过p_path绘制出不同要素的轮廓图
def find_cont(path, ele, dir, only_p, if256=False):
    for n, s in enumerate(ele):
        img = Image.open(path)
        w, h = img.size
        w = w - 512 if w > 512 else w
        p = img.load()
        cont_path = dir+s+'.png'
        for x in range(w):
            for y in range(h):
                rgb_p = p[x, y]
                # 建筑画到一张图
                if s == 'arcs' and (define_ele('main', rgb_p, only_p) or define_ele('landscape', rgb_p, only_p) or define_ele('other', rgb_p, only_p)):
                    p[x, y] = config.PLAN_RGB[s]
                # 其他要素单独画图
                elif define_ele(s, rgb_p, only_p):
                    p[x, y] = config.PLAN_RGB[s]
                else:
                    p[x, y] = (255, 255, 255)
        img.save(cont_path)
        blur(cont_path)

        con = cv2.imread(cont_path)
        gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cont in contours[1:]:
            area = cv2.contourArea(cont, False)  # 计算轮廓面积
            minarea = 25 if if256 else 100
            if area < minarea:
                cv2.fillPoly(con, [cont], (255, 255, 255))   # 填充轮廓
                continue
        cv2.imwrite(cont_path, con)


# 算出场地面积
def count_site(path, dir, only_p, if256=False):
    if not(os.path.exists(dir+'site.png')):
        find_cont(path, ['site'], dir, only_p, if256)
    con = cv2.imread(dir+'site.png')
    water = cv2.imread(dir+'water.png')
    area = 0
    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # for cont in contours[1:]:
    area = cv2.contourArea(contours[1], False)  # 计算除水外的轮廓面积

    # gray = cv2.cvtColor(water, cv2.COLOR_BGR2GRAY)
    # _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # contours, _ = cv2.findContours(
    #     binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # for cont in contours[1:]:
    #     area += cv2.contourArea(cont, False)  # 计算水的轮廓面积

    return area


# 处理图片，gh=true则生成一张导入gh显示高程的图
def process(dir, name='', gh=True, only_p=True):
    img_path = dir+'fake_B.png' if name == '' else dir+name
    con_path = dir+'arcs.png'
    p_path = dir+'plan.png'
    h_path = dir+'height.png'
    # gh_path = dir+'gh.png'

    '''
    如果两张图就裁图
    '''
    img = Image.open(img_path)
    if gh:
        img_p = img.crop((0, 0, 512, 512))
        img_h = img.crop((512, 0, 1024, 512))
        img_h.save(h_path)
        blur(h_path)
        h = cv2.imread(h_path)  # 后面灰度图要用到
    else:
        img_p = img
    img_p.save(p_path)
    blur(p_path, 3)
    p = cv2.imread(p_path)  # 在平面图上规整建筑要用到

    '''
    生成建筑轮廓图
    '''
    find_cont(p_path, ['arcs'], dir, only_p)

    # con = cv2.medianBlur(con, 5)
    '''
    规整建筑绘制到p_path上
    '''
    con = cv2.imread(con_path)

    # 找出每个区块的轮廓
    gray = cv2.cvtColor(con, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 计算每个区块的最小外接矩形
    for cont in contours[1:]:
        area = cv2.contourArea(cont, False)  # 计算轮廓面积
        # 对每个轮廓点求最小外接矩形
        box = min_box(cont)
        if area < 80:
            # 填掉arcs.png中太小的碎建筑
            cv2.fillPoly(con, [box], color=(255, 255, 255))
            continue
        M = cv2.moments(cont)  # 计算第一条轮廓的各阶矩,字典形式
        center_x = int(M['m10']/M['m00'])
        center_y = int(M['m01']/M['m00'])
        # if center_x > 512:
        #     continue
        b = p[center_y, center_x, 0]  # opencv颜色顺序是BGR
        g = p[center_y, center_x, 1]
        r = p[center_y, center_x, 2]
        rgb = define_arc((r, g, b), only_p)

        rgb = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
        cv2.fillPoly(p, [box], color=rgb)  # 在plan上画出规整后的建筑

        # 如果有灰度图，就同时也填充到灰度图上
        if gh:
            b = 0
            for i in range(0, 3):
                for j in range(0, 3):
                    r = h[center_y+i-1, center_x+j-1, 0]
                    b += r
            b = b//9
            cv2.fillPoly(h, [box], color=(int(b), int(b), int(b)))  # 填充轮廓线

        cv2.polylines(con, [box], True, (0, 255, 0), 1)  # 在arcs上绘制出建筑的轮廓线

    cv2.imwrite(con_path, con)
    cv2.imwrite(p_path, p)

    '''
    如果是有高度的模型，gh=True，生成导入gh的图片
    修改草地和水的高度，复制山石部分
    '''
    if gh:
        cv2.imwrite(h_path, h)
        copy_moutain(h_path, img_path, p_path, only_p)
    else:
        copy_moutain(p_path, img_path, p_path, only_p)

    '''
    如果是b表示高度的则复制山体到plan上
    '''


# 计算要素完整数和平均数,ifarg表示是否算平均数，arg是平均的底数
def caculate(elements, ifarg, arg=1):
    datas = []
    for x, e in enumerate(elements):
        data = [0*x for x in e[0]]
        for i in e:
            for j in range(len(i)):
                if ifarg:
                    data[j] += i[j]
                else:
                    data[j] = data[j]+1 if i[j] > 0 else data[j]
        if ifarg:
            data = [x/arg for x in data]
        datas.append(data)
    return datas


# 删除生成的轮廓文件等
def remove(dir, i):
    file = ['contour.png', 'arcs.png', 'plan.png', 'height.png', 'watermaintop_mountain.png',
            'gh.png', 'corridor.png', 'inter.png', 'mountain.png', 'water.png', 'site.png', 'mainwatermountain.png', 'landscape_boundmaintop_mountain.png', 'test.png']
    for f in file:
        if os.path.exists(dir+f):
            os.remove(dir+f)


if __name__ == "__main__":
    # path = "./results/compare2/sample/8_plan.png"
    # dir = "./results/compare2/sample/8_"
    # find_cont(path, ["arcs"], dir, False)

    # ele_num_sums = []
    # area_sums = []
    # angles = []
    # distances = []
    # for x in config.model_names:
    #     d = './results/compare2/unity/'+x+'/test_latest_iter800'
    #     area_sum = []
    #     ele_num_sum = []
    #     angle = []
    #     dists = []
    #     for i in range(config.test_n*config.test_fre):
    #         s = f'_{i//config.test_n}' if i > config.test_n-1 else ''
    #         j = i % config.test_n+1
    #         #dir = d+s+'/images/'+str(j)+'_'
    #         dir = d+s+'/'+str(j)+'_'
    #         print(i, dir+'fake_B.png')
    #         area = total(dir, False, coutarea=True, if256=(
    #             x == "multi_256" or x == "multis_256" or x == "plans_256"))
    #         area_sum.append(area)
    #     area_sums.append(area_sum)

    # # #         '''
    # # #         处理图片
    # # #         '''
    #         process(dir, x == 'multi_512' or x ==
    #                 'multis_512', x != 'plans_512')
    # find_cont(dir+'plan.png', ['water', 'mountain',
    #                            'inter', 'corridor', 'second'], dir, False)
    # # # '''
    # # # 计算景观格局角度或者主峰正对主厅角度
    # # # '''
    #         angle_lay = [calculation.angle_ele(
    #             dir, x != 'plans_512', 'water', 'main', 'mountain', draw=True)]
    # angle_t = [calculation.angle_ele(
    #     dir, x != 'plans_512', 'main', 'landscape_bound', 'top_mountain', draw=True)]
    #         angle.append(angle_t)
    #     angles.append(angle)
    # print(angle_lay, angle_t)
    # '''
    # 计算主景观建筑到主峰的距离或主峰到山中心的距离
    # '''
    #         dis_tl = [calculation.dis_sight(
    #                                      dir, 'top_mountain', 'landscape', x != 'plans_512')]
    #         dis_tm = [calculation.dis_sight(
    #         dir, 'top_mountain', 'mountain', x != 'plans_512')]
    #         dists.append(dis_tm)
    #     distances.append(dists)
    #         '''
    #         删除轮廓图等
    #         '''
    # remove(dir, j)
    #         '''
    #         统计图片要素数
    #         '''
    #     #     ele_num = total(dir, x != 'plans_512', coutarea=False)
    #     #     area = total(dir, x != 'plans_512', coutarea=True)
    #     #     ele_num_sum.append(ele_num)
    #     #     area_sum.append(area)
    #     # ele_num_sums.append(ele_num_sum)
    #     # area_sums.append(area_sum)

    # '''
    # 读取excel里的数据
    # '''
    # ele_num_sums = visualization.read_excel('ele_num_sum')  # 每张图中要素数
    # area_sums = visualization.read_excel('sample_area_sum')  # 每张图中要素面积占场地比例
    angle_mwms = visualization.read_excel(
        'angle_main_water_mountain_3')  # 每张图中山水主厅格局角度大小
    angle_tms = visualization.read_excel('angle_top_3')  # 每张图中主厅正对主峰角度大小
    # dis_tl = visualization.read_excel(
    #     'sample_dis_top_landscape')  # 每张图中主峰到主景观建筑的距离
    # dis_tm = visualization.read_excel(
    #     'sample_dis_top_mountain')  # 每张图中主峰到山石中心的距离

    # '''
    # 计算要素完整度和平均数量
    # '''

    # intergritys = caculate(ele_num_sums, False)
    # argnums = caculate(ele_num_sums, ifarg=True,
    #                    arg=config.test_n*config.test_fre)
    # argareas = caculate(area_sums, ifarg=True,
    #                     arg=config.test_n*config.test_fre)

    # '''
    # 将图片里的分析数据写入excel
    # '''

    # visualization.write_excel(
    #     config.model_names, config.rows_ele, ele_num_sums, 'ele_num_sum')#每张图中要素数
    # visualization.write_excel(
    #     config.model_names, config.rows_ele, area_sums, 'area_sum')  # 每张图中要素面积占场地比例
    # visualization.write_excel(
    #     config.model_names, config.rows_angle_top, angles, 'angle_top')  # 每张图中主厅正对主峰角度大小
    # visualization.write_excel(
    #     config.model_names, config.rows_angle_m_w_m, angles, 'angle_main_water_mountain')  # 每张图中山水主厅格局角度大小
    # visualization.write_excel(
    #     config.model_names, config.rows_dis_tl, distances, 'dis_top_lanscape')#每张图中主峰到主景观建筑的距离
    # visualization.write_excel(
    #     config.model_names, config.rows_dis_tm, distances, 'dis_top_mountain')#每张图中主峰到山石中心的距离

    # '''
    # 直方图显示数据
    # '''

    # visualization.Histogram_ele(
    #     'average_area_scale', ["samples"], config.rows, argareas)
    # print(argareas)
    # visualization.Histogram_ele(
    #     'intergrity', config.model_names, config.rows, intergritys)
    # visualization.Histogram_ele(
    #     'average_number', config.model_names, config.rows, argnums)

    visualization.Line_ele('angle_main_water_mountain',
                           ['multi_512', 'multis_512', 'plans_512'], angle_mwms, "angle", 180)
    visualization.Line_ele('angle_top',
                           ['multi_512', 'multis_512', 'plans_512'], angle_tms, "angle", 180)
    # visualization.Line_ele('sample_dis_top_landscape',
    #                        ["samples"], dis_tl, "distance", 100)
    # visualization.Line_ele('sample_dis_top_mountain',
    #                        ["samples"], dis_tm, "distance", 100)
