from PIL import Image, ImageEnhance
import numpy


dir = "E:/PYTHON/datasets/process/second/"


def combine(dir, i):
    input = Image.open(dir+'A/'+str(i)+'.jpg')
    plan = Image.open(dir+'c_plan/'+str(i)+'.png')
    height = Image.open(dir+'D/'+str(i)+'_plants.png')
    combine = Image.new('RGB', (1536, 512), 255)
    combine.paste(input, (0, 0))
    combine.paste(plan, (512, 0))
    combine.paste(height, (1024, 0))
    combine.save(dir+"result/"+str(i*4-3)+".jpg")
    # enh_bri = ImageEnhance.Sharpness(combine)
    # factor = 2.0
    # enhance_image = enh_bri.enhance(factor)
    input = input.transpose(Image.FLIP_LEFT_RIGHT)
    plan = plan.transpose(Image.FLIP_LEFT_RIGHT)
    height = height.transpose(Image.FLIP_LEFT_RIGHT)
    combine.paste(input, (0, 0))
    combine.paste(plan, (512, 0))
    combine.paste(height, (1024, 0))
    combine.save(dir+"result/"+str(i*4-2)+".jpg")

    input = input.transpose(Image.FLIP_TOP_BOTTOM)
    plan = plan.transpose(Image.FLIP_TOP_BOTTOM)
    height = height.transpose(Image.FLIP_TOP_BOTTOM)
    combine.paste(input, (0, 0))
    combine.paste(plan, (512, 0))
    combine.paste(height, (1024, 0))
    combine.save(dir+"result/"+str(i*4-1)+".jpg")

    input = input.transpose(Image.FLIP_LEFT_RIGHT)
    plan = plan.transpose(Image.FLIP_LEFT_RIGHT)
    height = height.transpose(Image.FLIP_LEFT_RIGHT)
    combine.paste(input, (0, 0))
    combine.paste(plan, (512, 0))
    combine.paste(height, (1024, 0))
    combine.save(dir+"result/"+str(i*4)+".jpg")


# 在山上对应减去路径的高度
def process(dir, dir_s, i):
    p_path = dir+str(i)+"_p.jpg"
    h_path = dir+str(i)+"_h.jpg"
    m_path = dir+str(i)+"_m.jpg"
    input_path = dir+str(i)+"_1.jpg"

    input = Image.open(input_path)
    plan = Image.open(p_path)
    height = Image.open(h_path)
    mountain = Image.open(m_path)

    m = mountain.load()
    p = plan.load()
    h = height.load()

    w, hei = plan.size

    for x in range(w):
        for y in range(hei):
            rgb_p = p[x, y]
            rgb_h = h[x, y]
            rgb_m = m[x, y]
            r = rgb_h[0]
            g = rgb_h[1]
            b = rgb_h[2]
            if rgb_m[0] < 30 and rgb_m[1] < 30 and rgb_p[0] > 30 and rgb_p[1] > 30:
                r -= 10
                g -= 10
                b -= 10
                p[x, y] = (0, 0, 0)
                # h[x, y] = (r, g, b)

    plan.save(dir_s+str(i)+"_p.jpg")
    height.save(dir_s+str(i)+"_h.jpg")
    # combine(input, plan, height, save_path=dir_s+str(i*4-3))

    # input = input.transpose(Image.FLIP_LEFT_RIGHT)
    # plan = plan.transpose(Image.FLIP_LEFT_RIGHT)
    # height = height.transpose(Image.FLIP_LEFT_RIGHT)
    # combine(input, plan, height, save_path=dir_s+str(i*4-2))

    # input = input.transpose(Image.FLIP_TOP_BOTTOM)
    # plan = plan.transpose(Image.FLIP_TOP_BOTTOM)
    # height = height.transpose(Image.FLIP_TOP_BOTTOM)
    # combine(input, plan, height, save_path=dir_s+str(i*4-1))

    # input = input.transpose(Image.FLIP_LEFT_RIGHT)
    # plan = plan.transpose(Image.FLIP_LEFT_RIGHT)
    # height = height.transpose(Image.FLIP_LEFT_RIGHT)
    # combine(input, plan, height, save_path=dir_s+str(i*4))


def combine_hp(dir, i):
    img_p = Image.open(dir+'B/'+str(i)+'.jpg')
    img_h = Image.open(dir+'C/'+str(i)+'.jpg')
    p = img_p.load()
    h = img_h.load()
    w, hei = img_p.size

    for x in range(w):
        for y in range(hei):
            rgb_p = p[x, y]
            rgb_h = h[x, y]
            p[x, y] = (rgb_p[0], rgb_p[1], rgb_h[2])

    img_p.save(dir+'c_plan/'+str(i)+'.png')


# 合并植物点植和丛植的数据
def combine_plants(dir):
    dot = Image.open(dir+'_d.png')
    group = Image.open(dir+'_g.png')
    d = dot.load()
    g = group.load()
    w, h = dot.size

    for x in range(w):
        for y in range(h):
            d_rgb = d[x, y]
            g_rgb = g[x, y]
            g[x, y] = (g_rgb[0], d_rgb[0], 255)

    group.save(dir+'_plants.png')


if __name__ == "__main__":
    dir = "E:/PYTHON/datasets/plants/"
    for i in range(22):
        print(i+1)
        combine(dir, i+1)
    # dir_s = "E:/PYTHON/datasets/process/analyze/"
    # for i in range(22):
    #     print(i, dir+str(i))
    #     process(dir, dir_s, i+1)
    # combine_plants(dir)
