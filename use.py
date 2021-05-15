
import os
import shutil
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
import util.util as util
import torch
from analyze import process
# from analyze import calculation
from analyze import unity
from analyze import visualization
from PIL import Image
import numpy as np

#test_img_path = os.path.join('./test_pics/original/')
#result_path = os.path.join('./test_pics/result/')
#project_name = 'schooltest14'

test_img_path = os.path.join('./test_pics/original/')
result_path = os.path.join('./test_pics/result/')
# project_name = 'multi_pix2pix'
project_name = 'plants_512'

# 对于multi生成的6通道图片转化为并排的3通道


def trans(fake_B, input_nc=3, crop_size=512):
    fake_B1 = fake_B[:, :input_nc, :, :]
    fake_B2 = fake_B[:, input_nc:, :, :]
    fake_B = torch.randn((1, input_nc, crop_size, 2*crop_size))
    fake_B[:, :, :, :crop_size] = fake_B1
    fake_B[:, :, :, crop_size:] = fake_B2
    return fake_B


# 第二张图片是高度的情况下，将生成初级图片中值模糊后算出最小外接矩形,生成新的图片
def plan(dir, name):
    process.process(dir, name, gh=True, only_p=False)
    p_path = dir+'plan.png'
    h_path = dir+'height.png'
    assert not os.path.isabs(p_path)
    assert not os.path.isabs(h_path)
    plan = Image.open(p_path)
    height = Image.open(h_path)
    combine = Image.new('RGB', (1024, 512), 255)
    combine.paste(plan, (0, 0))
    combine.paste(height, (512, 0))
    combine.save(dir+name)


# 第二张图片是植载设计的情况下，规整建筑和植物
def plan_with_tree(dir, name):
    unity.draw_circle_center(dir, name, test_img_path)
    process.process(dir, name, gh=False, only_p=False)
    plan_path = dir+'plan.png'
    tree_path = dir+'plant.png'
    assert not os.path.isabs(plan_path)
    assert not os.path.isabs(tree_path)
    plan = Image.open(plan_path)
    tree = Image.open(tree_path)
    combine = Image.new('RGB', (1024, 512), 255)
    combine.paste(plan, (0, 0))
    combine.paste(tree, (512, 0))
    combine.save(dir+name)


# 生成unity中的需要识别的arcs文件，将图片保存到unity DEMO文件夹路径中
def unityfile():
    unity_dir = 'E:/Bigsoftware/unity/project/garden/Assets/Demo/'
    if not os.path.exists(unity_dir):
        assert("unity文件路径不存在")
        return

    # 生成unity中的需要识别的arcs文件
    unity.point(False, result_path, unity_dir)

    # 把平面图和高度图复制到unity路径中
    source_p = result_path+'plan.png'
    source_h = result_path+'plant.png'
    assert not os.path.isabs(source_p)
    assert not os.path.isabs(source_h)
    target_p = unity_dir+'plan.png'
    target_h = unity_dir+'plant.png'

    # adding exception handling
    try:
        shutil.copyfile(source_p, target_p)
        shutil.copyfile(source_h, target_h)
    except IOError as e:
        print("Unable to copy file. %s" % e)
    except:
        print("Unexpected error:")


# 分析生成布局中不同要素的面积和比例
def analyze_area(input, output):
    area = {'water': 0, 'mountain': 0, 'corridor': 0, 'second': 100,
            'inter': 0,  'landscape': 0, 'main': 0, 'other': 0, 'site': 0}
    area_data = []
    area_ratio = []

    border = Image.open(input)
    plan = Image.open(output)
    border_map = border.load()
    plan_map = plan.load()
    w, h = plan.size

    for x in range(w):
        for y in range(h):
            b_rgb = border_map[x, y]
            p_rgb = plan_map[x, y]

            # 获取不同要素的面积
            if process.define_ele('water', p_rgb):
                area['water'] += 1
            elif process.define_ele('mountain', p_rgb):
                area['mountain'] += 1
            elif process.define_ele('corridor', p_rgb):
                area['corridor'] += 1
            elif process.define_ele('second', p_rgb):
                area['second'] += 1
            elif process.define_ele('inter', p_rgb):
                area['inter'] += 1
            elif process.define_ele('main', p_rgb):
                area['main'] += 1
            elif process.define_ele('landscape', p_rgb):
                area['landscape'] += 1
            elif process.define_ele('other', p_rgb):
                area['other'] += 1

            # 获取整个园林面积
            if process.define_ele('site', p_rgb):
                area['site'] += 1

            # 因为次路和边界颜色相同所以减去边界的面积
            if process.define_ele('second', b_rgb):
                if area['second'] > 10:
                    area['second'] = area['second'] - 1
                else:
                    break

    # 按照真实比例计算面积
    for key, value in area.items():
        print(key, value)
        a = value*120*120/(512*512)
        ratio = value/area['site']
        if key != 'site':
            area_data.append(round(a))
            area_ratio.append(round(ratio, 2))
    print(area_data, area_ratio)

    # 实际面积
    save_path = './static/images/spider.png'
    # 各要素面积比例
    save_path_ratio = './static/images/ratio.png'
    display_path = './static/images/analysis.png'
    visualization.area_radar('要素面积(㎡)', area_data, save_path, False)
    visualization.area_radar('要素场地占比(%)', area_ratio, save_path_ratio, True)
    # 将面积数据和面积比例数据合成一张分析图
    areacout = Image.open(save_path)
    areacout = areacout.crop((400, 0, 1400, 1000))
    arearatio = Image.open(save_path_ratio)
    arearatio = arearatio.crop((400, 0, 1400, 1000))
    combine = Image.new('RGBA', (2000, 1000), 255)
    combine.paste(areacout, (0, 0))
    combine.paste(arearatio, (1000, 0))
    combine.save(display_path)


if __name__ == '__main__':
    # def use():
    opt = TestOptions().parse()  # get test options
    # hard-code some parameters for test
    opt.num_threads = 0   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.serial_batches = True
    # no flip; comment this line if results on flipped images are needed.
    opt.no_flip = True
    # no visdom display; the test code saves the results to a HTML file.
    opt.display_id = -1
    opt.dataset = test_img_path
    opt.name = project_name
    opt.model = 'test'
    opt.netG = 'unet_256'
    opt.direction = 'AtoB'
    opt.dataset_mode = 'single'
    opt.norm = 'batch'
    opt.load_size = 512
    opt.crop_size = 512
    opt.output_nc = 6

    # create a dataset given opt.dataset_mode and other options
    dataset = create_dataset(opt)
    # create a model given opt.model and other options
    model = create_model(opt)
    # regular setup: load and print networks; create schedulers
    model.setup(opt)

    if opt.eval:
        model.eval()
    for i, data in enumerate(dataset):
        if i+1 != len(dataset):
            continue
        # if i >= opt.num_test:  # only apply our model to opt.num_test images.
        #    break
        model.set_input(data)  # unpack data from data loader
        model.test()           # run inference
        visuals = model.get_current_visuals()  # get image results
        img_path = model.get_image_paths()     # get image paths
        print(img_path)
        # 路径问题，如果是window则是split('\\')如果是ubuntu 则是/
        p = os.path.join('1', '')
        osstr = p.split('1')[-1]
        name = img_path[0].split(f'{osstr}')[-1].split('.')[0]
        print(name)
        for label, im_data in visuals.items():
            if label == 'fake':
                # 对于multi生成的6通道图片转化为并排的3通道
                im_data = trans(im_data)
                im = util.tensor2im(im_data)
                image_name = '%s.png' % (name)
                save_path = os.path.join(result_path, image_name)
                util.save_image(im, save_path)
                # 处理生成的矩形，生成建筑边界图
                plan_with_tree(result_path, image_name)
                # 生成unity角度文件
                unityfile()
                analyze_area(test_img_path+image_name, result_path+'plan.png')
