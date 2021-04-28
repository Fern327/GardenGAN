from pyecharts.charts import Bar
from pyecharts.charts import Line
import pyecharts.options as opts
import util
import config
import xlrd
import xlwt


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
        width='3000px', height='1200px', page_title=name))
    bar.add_xaxis(xaxis_data=rows[1:])
    for i, n in enumerate(model_names):
        bar.add_yaxis(
            series_name=model_names[i], y_axis=datas[i], label_opts=opts.LabelOpts(font_size=15), color=config.COLORS[i])
    # bar.show_config()
    bar.set_global_opts(title_opts=opts.TitleOpts(title=name),
                        xaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(font_size=30), name='ELEMENTS'),
                        yaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(font_size=30), name='ELE_RATIO'),
                        legend_opts=opts.LegendOpts(
                            textstyle_opts=opts.TextStyleOpts(font_size=30))
                        )
    util.mkdir('./analysis')
    bar.render('./analysis/'+name+'.html')


# 折线图可视化各要素信息
def Line_ele(name, model_names, datas):
    x = [n+1 for n in range(len(datas[0]))]
    line = Line(init_opts=opts.InitOpts(bg_color='rgba(255,250,205,0.2)',
                                        width='3000px', height='1200px', page_title=name))
    line.add_xaxis(xaxis_data=x)
    for i in range(len(datas)):
        y = [n[0] for n in datas[i]]
        line.add_yaxis(
            series_name=model_names[i], y_axis=y, symbol="arrow", is_symbol_show=False)
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
                opts.MarkLineItem(type_="average", name="平均值")
            ]
        ),
    )
    line.set_global_opts(title_opts=opts.TitleOpts(title=name),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(
                             font_size=30), name='TEST_PICS'),
                         yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(
                             font_size=30), name='ANGLE', min_=0, max_=180),
                         legend_opts=opts.LegendOpts(
                             textstyle_opts=opts.TextStyleOpts(font_size=30))
                         )

    util.mkdir('./analysis')
    line.render('./analysis/'+name+'.html')


if __name__ == '__main__':
    datas = [[[1], [2], [3]], [[2], [6], [7]], [[6], [5], [7]]]
    for i in range(len(datas)):
        y = [n[0] for n in datas[i]]
        print(y)
