# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 23:38:46 2020

@author: Henki.Yang
"""

import pandas as pd
import  requests
from  lxml import etree
import re

def get_url():#获取番剧链接
    
    result = []
    end = 159
    for page in range(1,end):
        link ='https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page='+str(page)+'&season_type=1&pagesize=20&type=1'
        
        page = requests.get(link)   
        text = page.text
        
        pattern =re.compile('"link":"(.*?)"')
        text_signal = pattern.findall(text)
        result = result + text_signal
        
    return result


def get_cid(link):#输入番剧链接，输出番剧名字、集数、cid
    page = requests.get(link)   
    text = page.text
    
    pattern =re.compile('"cid":(.*?),.*?"(第.*?话)"')
    pattern_name = re.compile( '"name": "(.*?)"')
    try:
        name =  pattern_name.search(text).groups()[0]
        text_signal = pattern.findall(text)
    except AttributeError:
        text_signal = None
        name = 0
    
    if len(text_signal) > 50:
        text_signal = None
        text_signal = None
        name = 0
        
    if len(name) > 50:
        text_signal = None
        text_signal = None
        name = 0
        
    return name,text_signal

def num(cid):#输入番剧cid输出单集弹幕数量
    text = []
    num = 0
    
    url='https://comment.bilibili.com/'+cid+'.xml'
    response = requests.get(url).content
    html= etree.HTML(response)
    content = html.xpath('//d//text()')
    pattern = re.compile('awsl|AWSL|阿伟')
    
    for text in content:   
        if re.search(pattern,text):
            num  = num + 1
    return num



names = []
nums  = []
num_single = []
pic_souce = pd.DataFrame(columns=['名字','数量','单集数量'])

urls = get_url()

for url in urls:
    try:
        number = 0
        name,res = get_cid(url)
        for i in res:
            names.append(name+i[1])
            num_i  = num(i[0])
            num_single.append(num_i)
            number = number + num_i#计算番剧累计的弹幕数量
            nums.append(number)
        print(name,number)
    except:
        print('wrong',name,i[0])
        continue
    
pic_souce['名字'] = names 
pic_souce['数量'] = nums       
pic_souce['单集数量'] = num_single

#除去重复与无效数据
pic_souce=pic_souce[~pic_souce['名字'].str.contains('"type":1')]
pic_souce = pic_souce.drop_duplicates(subset=['名字'],keep = "first")

#保存数据
writer = pd.ExcelWriter('pic_souce.xlsx')
pic_souce.to_excel(writer, "sheet1")
writer.save() 

sig_res = pic_souce.sort_values(by ='单集数量',ascending=False ).iloc[0:10]