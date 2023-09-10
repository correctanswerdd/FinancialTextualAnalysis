# -*- coding: utf-8 -*-
# @Time    : 2020/8/21 19:12
# @Author  : DUN
# @FileName: wordcount.py
# @Software: PyCharm
# @Blog    ：

import re  # 正则表达式库
import collections  # 词频统计库
import numpy as np  # numpy数据处理库
import wordcloud  # 词云展示库
from PIL import Image  # 图像处理库
import matplotlib.pyplot as plt  # 图像展示库
import os
import pandas as pd

key = "icode300"
list_of_values = pd.DataFrame(pd.read_excel("para_group.xlsx"))[key]
a = [int(x) for x in list_of_values if not pd.isnull(x)]
set_of_values = set(a)
set_of_values = list(set_of_values)
for value in set_of_values:
    print(value)
    for root, dirs, files in os.walk("./log/20200823/{key}={value}/".format(key=key, value=value)):
        for file in files:
            if file.find("topic") != -1 and file.find("txt") >= 0:
                topic = file[5]
                file_path = os.path.join(root, file)  # root文件所属目录
                with open(file_path, "r") as f:
                    word_list = f.readlines()[0].split(",")

                # 词频统计
                word_counts = collections.Counter(word_list)  # 对分词做词频统计
                # word_counts_top10 = word_counts.most_common(200)  # 获取前10最高频的词
                # for i in range(len(word_counts_top10)):
                #     print("{word}:{freq}".format(word=word_counts_top10[i][0], freq=word_counts_top10[i][1]))  # 输出检查

                # 词频展示
                mask = np.array(Image.open('wordcount.jpg'))  # 定义词频背景
                wc = wordcloud.WordCloud(
                    font_path='C:/Windows/Fonts/simhei.ttf',  # 设置字体格式
                    mask=mask,  # 设置背景图
                    max_words=5,  # 最多显示词数
                    max_font_size=100  # 字体最大值
                )

                wc.generate_from_frequencies(word_counts)  # 从字典生成词云
                image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
                wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
                plt.imshow(wc)  # 显示词云
                plt.axis('off')  # 关闭坐标轴
                # plt.show()  # 显示图像
                plt.savefig("{root}/topic{topic}.png".format(root=root, topic=topic))


