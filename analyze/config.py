
PLAN_RGB = {'main': (255, 150, 59), 'landscape': (181, 255, 254), 'other': (0, 0, 0), 'water': (0, 0, 0),
            'mountain': (76, 30, 35), 'corridor': (255, 0, 0), 'fenth': (0, 0, 255), 'inter': (125, 65, 232),
            'land': (255, 255, 0), 'outer': (255, 255, 255), 'arcs': (0, 0, 0), 'site': (0, 0, 0), 'second': (0, 0, 0)}

# 统计图显示的颜色
# COLORS = [['rgba(139,193,186,100)'], ['rgba(182,224,230,100)'],
#           ['rgba(111,144,181,100)'], ['rgba(237,142,138,100)']]
COLORS = [['rgba(206,206,206,100)'], ['rgba(155,155,155,100)'],
          ['rgba(83,215,198,100)'], ['rgba(50,189,174,100)'],
          ['rgba(49,123,148,100)'], ['rgba(31,89,115,100)']]


test_n = 5  # 测试边界数
test_fre = 5  # 每张边界测试次数

model_names = ['multi_512', 'multi_256', 'multis_512', 'multis_256', 'plans_512',
               'plans_256']
# model_names = ['multi_512', 'multis_512',  'plans_512']
# model_names = ['plan_512']  # 比较的模型名字
rows = ['water', 'mountain',
        'corridor', 'second', 'inter', 'main', 'landscape', 'other']
rows_ele = ['test_pic', 'water', 'mountain',
            'corridor', 'second', 'inter', 'main', 'landscape', 'other']
rows_angle_top = ['test_pic', 'angle_top']
rows_angle_m_w_m = ['test_pic', 'angle_main_water_mountain']
rows_dis_tl = ['test_pic', 'dis_top_lanscape']
rows_dis_tm = ['test_pic', 'dis_top_mountain']
