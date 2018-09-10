import json
import jieba
import sys
import jieba.analyse
import re
from collections import Counter
from pyecharts import Bar, Pie
from wordcloud import WordCloud,STOPWORDS
import numpy as np
import matplotlib.pyplot as plt
from os import path
from PIL import Image
d=path.dirname(__file__)
def format_content(content):  #去除空格等无用信息
#    content=content.replace(u'\xa0',u' ') # replace &nbsp
    content=re.sub(r'\[.*?\]' ,'',content)
    content=re.sub(r'\s*作曲.*\n','',content)
    content=re.sub(r'\s*作词.*\n','',content)
    content=re.sub(r'.*:','',content)
    content=re.sub(r'.*: ','',content)
    content=content.replace('\n',' ')
    return content

def word_segmentation(content,stop_words):
    #分词处理
    jieba.enable_parallel()
    seg_list=jieba.cut(content,cut_all=False)

    seg_list=list(seg_list)

    word_list=[]
    for word in seg_list:
        if word not in stop_words:  #停用词
            word_list.append(word)

    user_dict=[' ',u'哒',u'喵',u'说', u'里', u'嘞', u'做', u'噢', u'话']   #多余词 辞典
    filter_space=lambda w: w not in user_dict
    word_list=list(filter(filter_space,word_list))

    return word_list
#word_frequency @1
def word_frequency(word_list,*top_N):  #统计词频 top_N指定返回前多少个值
    if top_N:
        counter=Counter(word_list).most_common(top_N[0])
    else:
        counter=Counter(word_list).most_common()
    return counter

#word_fre @2
'''
def word_frequency2(word_list):
    stopwords=set(STOPWORDS)
    stopwords.add(' ')
    return stopwords
'''
def plot_chart(counter,chart_type='Bar'):
    items=[item[0] for item in counter]
    values=[item[1] for item in counter]

    if chart_type=='Bar':
        chart =Bar('词频统计')
        chart.add('词频',items,values,is_more_utils=True)
    else:
        chart=Pie('词频统计')
        chart.add('词频',items,values,is_label_show=True,is_more_utils=True)

    chart.show_config()
    chart.render('bar.html')

def cut_for_wordcloud(list):
    mylist=[]
    seg_list=jieba.cut(list,cut_all=False)
    liststr="/".join(seg_list)
    f_stop=open('data/stop_words.txt')
    try:
        f_stop_text=f_stop.read()
        f_stop_text=unicode(f_stop_text,'utf-8')
    finally:
        f_stop.close()
    f_stop_seg_list=f_stop_text.split('\n')
    for myword in liststr.split('/'):
        if not(myword.strip() in f_stop_seg_list) and len(myword.strip()) >1:
            mylist.append(myword)
    return ''.join(mylist)

#用jieba自带分词计数


def main():
    with open('data/lyric_list.json') as f:
        data=json.load(f)

    #data=data[0].encode('utf-8')

    #data_wordc=json.dumps('data/lyric_list.json')
    with open('data/stop_words.txt') as fi:
        stop_words=fi.read().split('\n')

    lyric=data[0]
    lyric=format_content(lyric)
    seg_list=word_segmentation(lyric, stop_words)
    counter=word_frequency(seg_list,10)
    plot_chart(counter)


    img=np.array(Image.open(path.join(d,"sister.jpeg")))

    wc=WordCloud(background_color="white",
                max_words=2000,
                font_path="/home/eggward/桌面/SIMYOU.TTF",
                mask=img)

    #word_list2=jieba.analyse.textrank(data_wordc,topK=100,withWeight=True)
    print(isinstance(counter,list))

    """keywords=dict()
    for i in word_list2:
        keywords[i[0]]=i[1]
"""

    data_wordc=''.join(seg_list)
    print(data_wordc)
    wc.generate(data_wordc)
    #_from_frequencies
    plt.figure()
    plt.imshow(wc)

    plt.axis("off")
    plt.show()
    wc.to_file(path.join(d,"Cloud.png"))

if __name__=='__main__':
    main()
