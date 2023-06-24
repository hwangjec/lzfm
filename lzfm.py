import requests
from lxml import etree
import os
import re
import pandas as pd

'''
由于时间关系 代码并未用函数封装，以致于可读性较差
'''

cookies = {
    'Hm_lvt_45dcc777b283462d0db81563b6c09dbe': '1687427378',
    'page-type': 'play',
    'repeater': '1',
    'page': '%7B%22hiddenPh%22%3A%22mJ17WARtcjM%22%2C%22band%22%3A18459%2C%22rid%22%3A6931495515974784%2C%22uid%22%3A11953%2C%22userName%22%3A%22%E4%BF%AE%E7%82%BC%E7%88%B1%E6%83%85%E2%9C%A8%E5%BC%82%E5%9C%B0%E6%81%8B%E7%92%90%E7%92%90%22%2C%22radioName%22%3A%22%E4%BF%AE%E7%82%BC%E7%88%B1%E6%83%85%F0%9F%8E%88%E5%BC%82%E5%9C%B0%E6%81%8B%22%2C%22title%22%3A%22Vol.759%20%E7%88%B1%E4%B8%80%E4%B8%AA%E4%B8%8D%E5%96%9C%E6%AC%A2%E4%BD%A0%E7%9A%84%E4%BA%BA%22%2C%22duration%22%3A318%2C%22url%22%3A%22%22%2C%22id%22%3A%222907349938499047942%22%2C%22cover%22%3A%22https%3A%2F%2Fcdnimg103.lizhi.fm%2Fradio_cover%2F2016%2F11%2F30%2F2571155323974400516.jpg%22%2C%22payflag%22%3A0%2C%22islistenfirst%22%3A0%2C%22index%22%3A2%7D',
    'page-ts': '1687429764847',
    'box': '1e520b5',
    'box-ts': '1687429765203',
    'Hm_lpvt_45dcc777b283462d0db81563b6c09dbe': '1687585298',
}
# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}
# 创建文件
path = "D:\\pic\\"
if not os.path.exists(path):
    os.mkdir(path)
if not os.path.exists("D:\\audio\\"):
    os.mkdir("D:\\audio\\")

cnt = 0 # 统计个数
url_list = [] # 保存二级url
for j in range(1, 9):# 恋爱类节目共有8页 本意可使用selenium做个自动滚动找到最后一页的位置 但selenium写起来较为繁琐且效率较低
    response = requests.get(f'https://www.lizhi.fm/label/24229798160629936/{j}.html', cookies=cookies, headers=headers)# 发送请求
    html = etree.HTML(response.text)# 解析页面
    root = html.xpath('/html/body/div/div[2]/div[1]/div/ul/li')
    for i in root:
        cnt += 1
        nick = i.xpath('./p[1]/a/text()')[0].replace('\n', "").strip().replace('*', "").replace('丨', "").replace('＇',"").replace(
            '\\', "")# 昵称
        img_url = i.xpath('./a/img/@data-echo')[0]# 图片url
        pic = requests.get(img_url, headers=headers).content# 请求
        name = str(cnt) + nick
        with open(r"D:\pic\{0}.jpg".format(name), "wb") as f:# 写入文件
            f.write(pic)
        second = i.xpath("./a/@href")[0]
        second_url = url_list.append(f"https://www.lizhi.fm{second}")# 二级url

df = pd.DataFrame()# 用于输出
num = 0# 计数
for i in url_list:
    res = requests.get(i, headers=headers)# 对二级页面发起请求
    second_html = etree.HTML(res.text)# 解析页面
    second_root = second_html.xpath("/html/body/div/div[2]")
    for i in second_root:
        name = (lambda x: x[0] if x else " ")(i.xpath("./div[1]/div/text()")) # 昵称
        title = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/h1/text()")) # 标题
        works = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/div[1]/p[1]/span[1]/text()")) # 作品数
        audio = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/div[1]/p[1]/span[2]/text()")) # 播放量
        fans = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/div[1]/p[1]/span[3]/text()")) # 粉丝数
        audio_type = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/div[1]/div/a/text()")) # 类型
        sign = (lambda x: x[0] if x else " ")(i.xpath("./div[3]/div[2]/div[2]/text()")) # 个性签名
        last_audio = (lambda x: x[0] if x else " ")(i.xpath("./div[4]/ul/li/a/@title")) # 最新音频标题

        total = (lambda x: x[0] if x else " ")(i.xpath("./div[4]/ul/li/a/div/div[1]/p[2]/text()")).split("   ") # 最新内容细节
        if len(total) > 1:
            last_cnt = (lambda x: x[1] if x else " ")(total[0].split("：")) # 最新音频播放量
            last_time = (lambda x: x[1] if x else " ")(total[1].split("：")) # 最新作品发表时间
            compliex = re.compile(r"\d+")
            last_content = compliex.findall(total[2])[0] # 最新作品评论数
            split_time = last_time.split("-")
            audio_id = (lambda x: x[0] if x else " ")(i.xpath("./div[4]/ul/li/a/@data-id"))
            '''
            爬取最新音频 在分析页面时 MP3文件可通过id结合url前缀拼接发起请求得到json数据包解析后可得到音频文件，
            但频繁请求会使代码变得繁杂，根据文件名发现规律直接拼接对MP3文件发起请求
            '''
            audio_url = f"http://cdn5.lizhi.fm/audio/{split_time[0]}/{split_time[1]}/{split_time[2]}/{audio_id}_hd.mp3"
            if len(audio_id) > 2 and num < 10:
                last_vol = requests.get(audio_url, headers=headers).content
                with open(r"D:\audio\{0}.mp3".format(last_audio), "wb") as f:
                    f.write(last_vol)
                    num += 1
    text = pd.DataFrame(
        {"昵称": [name], "标题": [title], "作品数": [works], "浏览数": [audio], "粉丝": [fans], "类型": [audio_type], "个性签名": [sign],
         "最新作品": [last_audio]})
    df = pd.concat([df, text])

df.to_excel(r".\result.xlsx", index=False)# 输出文件
