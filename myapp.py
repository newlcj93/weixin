#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, g,request, make_response
import os
import urlparse
import time
import requests
import json
from wechat_sdk import WechatBasic

app = Flask(__name__)


# 图灵机器人的 API KEY
TURING_API_KEY = '15a3f5d45e862e7c349705d463d66c27'

# 微信公众平台 TOKEN
TOKEN = 'weixin'

# 图灵机器人
def get_turing(message):
    url = 'http://www.tuling123.com/openapi/api?key=' + TURING_API_KEY + '&info='
    req = requests.get(url + message)
    return json.loads(req.content)["text"]
'''
# 小 i 机器人
def get_xiaoi(message):
    url = 'http://www.xiaodoubi.com/xiaoiapi.php?msg='
    req = requests.get(url + message)

    return req.content
'''
# 获取知乎日报
def get_zhihudaily():
    json_str_data = requests.get('http://news-at.zhihu.com/api/4/news/latest')
    json_data = json.loads(json_str_data.content)['stories']
    news_str = []

    count = 0
    for x in json_data:
        news_str.append({'title': x["title"], 'url': 'http://daily.zhihu.com/story/' + str(x['id']), 'picurl': x["images"][0].replace('\\/', '/')})
        count += 1

        if count == 10:   # 最多允许 10 条新闻
            break

    return news_str

# 获取 V2EX 前十大热帖
def get_v2ex_news():
    json_str_data = requests.get('http://www.v2ex.com/api/topics/hot.json')
    json_data = json.loads(json_str_data.content)
    news_str = []

    for x in json_data:
        news_str.append({'title': x["title"], 'url': x['url']})

    return news_str


@app.route('/', methods=['GET', 'POST'])
def wechat_auth():
    wechat = WechatBasic(token=TOKEN)
    if request.method == 'GET':
        token = 'weixin'  # your token
        query = request.args  # GET 方法附上的参数
        signature = query.get('signature', '')
        timestamp = query.get('timestamp', '')
        nonce = query.get('nonce', '')
        echostr = query.get('echostr', '')

        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return make_response(echostr)
        else:
            return 'Signature Mismatch'
    else:
        body_text=request.data
        wechat.parse_data(body_text)
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = wechat.get_message()
        response = None
        # 在这里解析 message.content 也就是用户发来的文字
        if message.type == 'text':
            if message.content.lower() in ('h', 'help'):
                response = wechat.response_text(u'z 看知乎日报\nv 看 V2EX 十大\nh 为帮助\n输入其他文字与机器人对话 : )')
            elif message.content == 'wechat':
                response = wechat.response_text(u'^_^')
            elif message.content[0:3] == 'test':
                response = wechat.response_text(u'I\'m testing ' + message.content[4:])
            elif (u'陆' or u'杰') in message.content:
                response = wechat.response_text(u'爸爸是个天才')
            elif (u'俞汭蔚' or u'内内') in message.content:
                response = wechat.response_text(u'内内,为什么你名字那么难写')
            elif message.content.upper() in ('V', 'V2EX'):
                response = wechat.response_news(get_v2ex_news())
            elif message.content.upper() in ('Z', 'ZHIHU'):
                response = wechat.response_news(get_zhihudaily())
            else:
                response = wechat.response_text(get_turing(message.content))
        elif message.type == 'image':
            response = wechat.response_text(u'您发来了一个图片')
        elif message.type == 'location':
            response = wechat.response_text(u'您的位置我已收到')
        elif message.type == 'event':
            if message.event == "subscribe":
                response = wechat.response_text(u'oh...你居然关注了,其实我自己也不知道关注这个号有啥用.\nz 看知乎日报\nv 看 V2EX 十大\nh 为帮助\n输入其他文字与机器人对话 : )')
        else:
            response = wechat.response_text(u'未知类型。您发的是什么？')
        return response
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 443))
    app.run(host='0.0.0.0',port=port,debug=True)

