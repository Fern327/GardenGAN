import albumentations as A
from torch.utils.data import Dataset
import os
import numpy as np
from PIL import Image
from torchvision import transforms

transform = A.Compose(
    [
        A.Resize(width=256, height=256),
    ],
)
unload = transforms.ToPILImage()

dir = "E:/PYTHON/datasets"
num_sample = 72


def resize(plan_path, plan_save_path):
    plan_files = os.listdir(plan_path)

    for i in range(len(plan_files)):
        plan = np.array(Image.open(plan_path+"/"+str(plan_files[i])))
        plan = transform(image=plan)["image"]
        plan = unload(plan)
        plan.save(plan_save_path+f"/{i+1}.jpg")


def combine(plan_save_path, height_save_path, combine_save_path):
    plan_files = os.listdir(plan_save_path)
    height_files = os.listdir(height_save_path)

    for i in range(0, num_sample):
        plan = Image.open(plan_save_path+f"/{i+1}.jpg")
        height = Image.open(height_save_path+f"/{i+1}.jpg")
        p = plan.load()  # 创造一个rgb map
        H = height.load()
        w, d = plan.size

        # for x in range(0, w):
        #     for y in range(0, d):
        #         rgb_p = p[x, y]  # 获取一个像素块的rgb
        #         rgb_h = H[x, y]
        #         r = rgb_p[0]
        #         g = rgb_p[1]
        #         b = rgb_p[2]
        #         h = rgb_h[0]
        #         if r > 220 and g < 60 and b < 60:  # 廊
        #             p[x, y] = (255, 0, h)
        #         elif r > 220 and g > 220 and b < 40:  # 草地
        #             p[x, y] = (0, 255, 10)
        #         elif r < 20 and g > 240 and b > 240:  # 水
        #             p[x, y] = (255, 255, 0)
        #         elif r < 50 and g < 50 and b < 50:  # 其他建筑
        #             p[x, y] = (127, 127, h)
        #         elif r > 215 and g > 115 and g < 165 and b > 25 and b < 95:  # 主厅
        #             p[x, y] = (127, 0, h)
        #         elif r > 145 and r < 215 and g > 205 and b > 205:  # 主景观
        #             p[x, y] = (0, 127, h)
        #         elif r > 40 and r < 120 and g < 90 and b < 90:  # 山石
        #             p[x, y] = (0, 0, h)
        #         elif r > 80 and r < 160 and g > 40 and g < 100 and b > 190:  # 夹层
        #             p[x, y] = (127, 255, h)
        #         elif r < 50 and g < 50 and b > 220:  # 边
        #             p[x, y] = (255, 127, h)
        #         else:  # 其他
        #             p[x, y] = (255, 255, 0)

        for x in range(0, w):
            for y in range(0, d):
                rgb_p = p[x, y]  # 获取一个像素块的rgb
                rgb_h = H[x, y]
                r = rgb_p[0]
                g = rgb_p[1]
                b = rgb_p[2]
                h = rgb_h[0]
                if r > 220 and g > 220 and b > 220:  # 空地
                    p[x, y] = (255, 255, 0)
                else:
                    p[x, y] = (r, g, b)

        plan.save(combine_save_path+f"/{i+1}.jpg")


def cat(plan_save_path, height_save_path, combine_save_path):
    plan_files = os.listdir(plan_save_path)
    height_files = os.listdir(height_save_path)

    for i in range(len(plan_files)):
        plan = Image.open(plan_save_path+"/"+str(plan_files[i]))
        height = Image.open(height_save_path+"/"+str(height_files[i]))
        w, h = plan.size
        combine = Image.new('RGB', (3*w, h), 255)
        combine.paste(plan, (0, 0))
        combine.paste(height, (w, 0))
        combine.save(combine_save_path+f"/{i+1}.jpg")


if __name__ == "__main__":
    # resize(plan_path="E:/PYTHON/datasets/process/2060/input_1_2160",
    #        plan_save_path="E:/PYTHON/datasets/process/2060/input_1_256")
    # combine(plan_save_path="E:/PYTHON/datasets/process/test_1_512",
    #         height_save_path="E:/PYTHON/datasets/process/test_1_512", combine_save_path="E:/PYTHON/datasets/process/test_1_512")
    cat(plan_save_path="E:/PYTHON/datasets/process/256/input_1_256", height_save_path="E:/PYTHON/datasets/process/256/train_2_256",
        combine_save_path="E:/PYTHON/datasets/process/256/train_multi_256")
