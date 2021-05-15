from pyecharts.charts import Bar, Line, Radar
import pyecharts.options as opts
from pyecharts.render import make_snapshot
# 使用snapshot-selenium 渲染图片
# from snapshot_selenium import snapshot
from snapshot_phantomjs import snapshot
import util
from analyze import config
# import config
import xlrd
import xlwt
from PIL import Image

# 将分析数据写入excel表格


def write_excel(model_names, rows, datas, exc_name):
    f = xlwt.Workbook()
    for model, model_name in enumerate(model_names):
        sheet = f.add_sheet(model_name, cell_overwrite_ok=True)
        # 写第一行
        for i in range(0, len(rows)):
            sheet.write(0, i, rows[i])
        # 写第一列
        for i in range(config.test_n*config.test_fre):
            s = f'_{i//config.test_n}' if i > config.test_n-1 else ''
            d = './results/'+model_name+'/test_latest_iter800'
            test_dir = d+s+'/images/'+str(i % config.test_n+1)+'_fake_B.png'
            sheet.write(i+1, 0, test_dir)
            for n in range(len(rows)-1):
                # print(model, i, n)
                sheet.write(i+1, n+1, datas[model][i][n])
    util.mkdir('./analysis')
    util.mkdir('./analysis/excel')
    f.save('./analysis/excel/'+exc_name+'.xls')


# 读取excel表格的分析数据
def read_excel(exc_name):
    file = './analysis/excel/'+exc_name+'.xls'
    datas = []
    with xlrd.open_workbook(filename=file) as f:  # 打开文件
        for model in f.sheet_names():
            intergrity_onemodel = []
            sheet = f.sheet_by_name(model)  # 通过名字获取表格
            for row in range(sheet.nrows-1):
                intergrity_onepic = []
                for col in range(sheet.ncols-1):
                    intergrity_onepic.append(sheet.cell_value(row+1, col+1))
                intergrity_onemodel.append(intergrity_onepic)
            datas.append(intergrity_onemodel)
    return datas


# 直方图形式可视化各要素信息
def Histogram_ele(name, model_names, rows, datas):
    bar = Bar(init_opts=opts.InitOpts(
        width='1500px', height='600px', page_title=name))
    bar.add_xaxis(xaxis_data=rows)
    for i, n in enumerate(model_names):
        print(model_names[i], config.COLORS[i])
        bar.add_yaxis(

            series_name=model_names[i], y_axis=datas[i], label_opts=opts.LabelOpts(font_size=15), color=config.COLORS[i])
    # bar.show_config()
    bar.set_global_opts(title_opts=opts.TitleOpts(title=name),
                        xaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(font_size=20), name='ELEMENTS'),
                        yaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(font_size=30), name='ELE_RATIO'),
                        legend_opts=opts.LegendOpts(
                            textstyle_opts=opts.TextStyleOpts(font_size=20))
                        )
    util.mkdir('./analysis')
    bar.render('./analysis/'+name+'.html')


# 折线图可视化各要素信息
def Line_ele(name, model_names, datas, y_name, y_max):
    x = [n for n in range(len(datas[0]))]
    line = Line(init_opts=opts.InitOpts(bg_color='rgba(255,250,205,0.2)',
                                        width='1500px', height='600px', page_title=name))
    line.add_xaxis(xaxis_data=x)

    average = []
    for i in range(len(datas)):
        sum = 0
        num = 0
        y = [n[0] for n in datas[i]]
        line.add_yaxis(
            series_name=model_names[i], y_axis=y, symbol="arrow", is_symbol_show=False)
        for j in datas[i]:
            sum += j[0]
            num = num+1 if j[0] > 0 else num
        average.append(sum/num)
        print(sum, num, average[i])
    line.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="min", name="最小值"),
                opts.MarkPointItem(type_="max", name="最大值"),
            ]
        ),
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(name="multi", y=average[0]),
                opts.MarkLineItem(name="multis", y=average[1]),
                opts.MarkLineItem(name="plans", y=average[2])
            ]
        ),
    )
    line.set_global_opts(title_opts=opts.TitleOpts(title=name),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(
                             font_size=30), name='TEST_PICS'),
                         yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(
                             font_size=30), name=y_name, min_=0, max_=y_max),
                         legend_opts=opts.LegendOpts(
                             textstyle_opts=opts.TextStyleOpts(font_size=30))
                         )

    util.mkdir('./analysis')
    line.render('./analysis/'+name+'.html')


# 雷达图视化
def Radar_pic(name, datas, ifratio) -> Radar:
    color = ["#ff7f00"] if ifratio else ["#4587E7"]
    data = [{"value": datas, "name": name}]
    watermax = 1000 if datas[0] < 1000 else datas[0]*1.1
    mountainmax = 1000 if datas[1] < 1000 else datas[1]*1.1
    corridormax = 1000 if datas[2] < 1000 else datas[2]*1.1
    secondmax = 250 if datas[3] < 250 else datas[3]*1.1
    intermax = 500 if datas[4] < 500 else datas[4]*1.1
    landscapemax = 250 if datas[5] < 250 else datas[5]*1.1
    mainmax = 250 if datas[6] < 250 else datas[6]*1.1
    othermax = 450 if datas[7] < 450 else datas[7]*1.1

    waterratio = 0.25 if datas[0] < 0.25 else datas[0]*1.2
    mountainratio = 0.25 if datas[1] < 0.25 else datas[1]*1.1

    c_schema = [
        {"name": "主水", "max": round(waterratio, 2)
         if ifratio else round(watermax)},
        {"name": "主山", "max": round(mountainratio, 2)
         if ifratio else round(mountainmax)},
        {"name": "廊道", "max": 0.25 if ifratio else round(corridormax)},
        {"name": "次路", "max": 0.20 if ifratio else round(secondmax)},
        {"name": "夹层", "max": 0.20 if ifratio else round(intermax)},
        {"name": "主景观建筑", "max": 0.20 if ifratio else round(landscapemax)},
        {"name": "主厅", "max": 0.20 if ifratio else round(mainmax)},
        {"name": "其他建筑", "max": 0.20 if ifratio else round(othermax)},
    ]

    c = (
        Radar()
        .set_colors(color)
        .add_schema(
            schema=c_schema,
            shape="circle",
            # 图片中心位置
            center=["50%", "50%"],
            # 雷达图半径大小
            radius="80%",
            angleaxis_opts=opts.AngleAxisOpts(
                # 径向轴大小
                # min_=0,
                # max_=360,
                # is_clockwise=False,
                # 径向轴间隔大小
                interval=4,
                axistick_opts=opts.AxisTickOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            textstyle_opts=opts.TextStyleOpts(font_size=20),
            radiusaxis_opts=opts.RadiusAxisOpts(
                min_=0,
                max_=1000,
                interval=200,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=False, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            polar_opts=opts.PolarOpts(),
            splitarea_opt=opts.SplitAreaOpts(is_show=False),
            splitline_opt=opts.SplitLineOpts(is_show=False),
        )
        .add(
            series_name=name,
            data=data,
            # 透明度
            areastyle_opts=opts.AreaStyleOpts(opacity=0.2),
            # 线宽
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(font_size=20)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=name,
                pos_left="22%",
                pos_top="10",
            ),
            legend_opts=opts.LegendOpts(pos_right=10)
        )
    )
    return c


# 存为图片
def area_radar(name, data, save_path, ifratio):
    r = Radar_pic(name, data, ifratio)
    make_snapshot(snapshot, r.render(), save_path)


if __name__ == '__main__':
    datas = [0, 0, 0, 0, 0, 0, 0, 0]
    area_radar("要素面积占比(㎡)", datas, './analyze/testfcr.png', True)
