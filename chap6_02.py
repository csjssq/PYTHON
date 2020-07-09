#分析Ajax爬取今日头条街拍美图
import requests
from urllib.parse import urlencode
from requests import codes
import os
from hashlib import md5
from multiprocessing.pool import Pool
import re
import random

def get_page(offset):
    headers = {
        'cookie': 'ttcid=234c9d509285438bbfdfabd6e035820c13; WEATHER_CITY=%E5%8C%97%E4%BA%AC; SLARDAR_WEB_ID=3f0c65b0-ffac-4c28-8046-eac588891f8c; csrftoken=95ff4ffb37a19fc1823962108bc60227; tt_webid=6847277022881990158; s_v_web_id=verify_kce2tfy9_A8ErP1sr_uGYm_40Rt_BvLd_J0oVpXhBtfzh; __tasessionId=vtin9mbmf1594255930140; tt_webid=6847277022881990158; tt_scid=L3YgArGrJw6cGojul4bpLsVUbDMRcqCwwyW-D8HfgtW0zXogi6gdN3I6x69kUMUS3f7d',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    }
    params = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    base_url = 'https://www.toutiao.com/api/search/content/?'
    url = base_url + urlencode(params)
    try:
        resp = requests.get(url, headers=headers)
        if 200  == resp.status_code:
            return resp.json()
    except requests.ConnectionError:
        return None
    
def get_images(json):
    headers = {
        'cookie': 'ttcid=234c9d509285438bbfdfabd6e035820c13; WEATHER_CITY=%E5%8C%97%E4%BA%AC; SLARDAR_WEB_ID=3f0c65b0-ffac-4c28-8046-eac588891f8c; csrftoken=95ff4ffb37a19fc1823962108bc60227; tt_webid=6847277022881990158; s_v_web_id=verify_kce2tfy9_A8ErP1sr_uGYm_40Rt_BvLd_J0oVpXhBtfzh; __tasessionId=vtin9mbmf1594255930140; tt_webid=6847277022881990158; tt_scid=L3YgArGrJw6cGojul4bpLsVUbDMRcqCwwyW-D8HfgtW0zXogi6gdN3I6x69kUMUS3f7d',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    }
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('title') is None: # 刨掉前部分无关内容
                continue
            title = re.sub('[\t]', '', item.get('title')) # 获取标题
            url = item.get("article_url")  #获取子链接
            if url == None:
                continue
            try:
                resp = requests.get(url,headers=headers)
                if 200  == resp.status_code:
                    images_pattern = re.compile('JSON.parse\("(.*?)"\),\n',re.S)
                    result = re.search(images_pattern,resp.text)
                    if result == None: # 非图集形式
                        images = item.get('image_list')
                        for image in images:
                            origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url')) # 改成origin/pgc-image是原图
                            yield {
                                'image': origin_image,
                                'title': title
                            }
                    else: # 图集形式 抓取gallery下json格式数据
                        url_pattern=re.compile('url(.*?)"width',re.S)
                        result1 = re.findall(url_pattern,result.group(1))
                        for i in range(len(result1)):
                            yield{
                                'image': "http://p%d.pstatp.com/origin/pgc-image/"%(random.randint(1,10)) + 
                                           result1[i][result1[i].rindex("u002F")+5:result1[i].rindex('\\"')], #存储url
                                'title': title
                            }
            except requests.ConnectionError: # 打开子链接失败就直接保存图集中前部分
                for image in images:
                    origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url')) # 改成origin/pgc-image是原图
                    yield {
                        'image': origin_image,
                        'title': title
                    }
                
def save_image(item):
    img_path = 'img' + os.path.sep + item.get('title')
    if not os.path.exists(img_path):
        os.makedirs(img_path) # 生成目录文件夹
    try:
        resp = requests.get(item.get('image'))
        if codes.ok == resp.status_code:
            file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                file_name=md5(resp.content).hexdigest(), 
                file_suffix='jpg')  # 单一文件的路径
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(resp.content) 
                print('Downloaded image path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except Exception as e:
        print(e)
        
def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        save_image(item)

if __name__ == '__main__':
    '''
    for i in range(3):
        main(20*i)
    '''
    pool = Pool()
    groups = ([x * 20 for x in range(0, 3)])
    pool.map(main, groups)