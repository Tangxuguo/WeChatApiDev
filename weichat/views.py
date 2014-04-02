#coding:utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Template
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
import urllib, urllib2, hashlib, time
import pylibmc
import re
import json
from douban import douban_movie,douban_music,douban_book
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
TOKEN = "marson"

YOUDAO_KEY = "208336561"
YOUDAO_KEY_FROM = "WechatPublic"
YOUDAO_DOC_TYPE = "xml"

@csrf_exempt

def handleRequest(request):
    if request.method == "GET":
        response = HttpResponse(CheckSignature(request), content_type="text/plain")
        return response
    elif request.method == "POST":
        response = HttpResponse(responseMsg(request), content_type="application/xml")
        return response
    else:
        return "Hello I'm Here"
    
def CheckSignature(request):
    global TOKEN
    signature = request.GET.get("signature",None)
    timestamp = request.GET.get("timestamp",None)
    nonce = request.GET.get("nonce",None)
    echoStr = request.GET.get("echostr",None)
    
    token = TOKEN
    tmpList = [token,timestamp,nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echoStr
    else:
        return None
    
def responseMsg(request):
    raw_str = smart_str(request.raw_post_data)
    msg = paraseMsgXml(ET.fromstring(raw_str))
    msgType = msg.get('MsgType')
    event = msg.get('Event')
    fromuser = msg.get('FromUserName')
    mc = pylibmc.Client()
    if msgType == 'event' and event == 'CLICK':
        eventKey = msg.get('EventKey')
        if eventKey == "help":
            replyContent = u'1:输入中英文文本翻译.\n2:输入电影/图书/音乐名称搜索相关信息,输入quitmovie/quitbook/quitmusic即可退出相应服务.\n3:点击扇贝，进入新闻/读书/论坛/小组.\n4:输入help获得帮助.'
        if eventKey == "movie":
            replyContent = u'输入电影名称（中文或英文）来获得相关信息,输入quitmovie离开电影查询'
            mc.set(fromuser+'_movie','search')
        if eventKey == "book":
            replyContent = u'输入图书名称(中文或英文)来获取相关信息，输入quitbook离开图书查询'
            mc.set(fromuser+'_book','search')
        if eventKey == "music":
            replyContent = u'输入音乐名称(中文或英文)来获取相关信息，输入quitmusic离开音乐查询'
            mc.set(fromuser+'_music','search')
        return getReplyText(msg,replyContent)

    if msgType == 'event' and event == 'subscribe':
        replyContent = u'终于等到你，还好我没放弃！'
        return getReplyText(msg,replyContent)
    if msgType == 'event' and event =='unsubscribe':
        replyContent = u'你好狠心!'
        return getReplyText(msg,replyContent)
    if msgType == 'text':
        content = msg.get('Content',"You have input nothing")
        mcmovie = mc.get(fromuser+'_movie')
        mcbook = mc.get(fromuser+'_book')
        mcmusic = mc.get(fromuser+'_music')
        if content.lower() =='quitbook':
            mc.delete(fromuser+'_book')
            replyContent = u'您已退出图书查询，谢谢使用'
            return getReplyText(msg,replyContent)
        if content.lower() == 'quitmovie':
            mc.delete(fromuser+'_movie')
            replyContent = u'您已退出电影查询，谢谢使用'
            return getReplyText(msg,replyContent)
        if content.lower() == 'quitmusic':
            mc.delete(fromuser+'_music')
            replyContent = u'您已退出音乐查询，谢谢使用'
            return getReplyText(msg,replyContent)
        if mcmovie == 'search':
            getcha = douban_movie(content)
            return getReplyNews(msg,getcha)
        if mcbook == 'search':
            getcha = douban_book(content)
            return getReplyNews(msg,getcha)
        if mcmusic == 'search':
            getcha = douban_music(content)
            return getReplyNews(msg,getcha)

        else:
            replyContent=youdao(content)
            return getReplyText(msg,replyContent)

def youdao(content):
        query_str = content
        raw_youdaoURL = "http://fanyi.youdao.com/openapi.do?keyfrom=%s&key=%s&type=data&doctype=%s&version=1.1&q=" % (YOUDAO_KEY_FROM,YOUDAO_KEY,YOUDAO_DOC_TYPE)
        youdao_URL = "%s%s" % (raw_youdaoURL,urllib2.quote(query_str))
        req = urllib2.Request(youdao_URL)
        result = urllib2.urlopen(req).read()
        replyContent = paraseYouDaoXml(ET.fromstring(result))
        return replyContent

def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg

def paraseYouDaoXml(rootElem):
    replyContent = ''
    if rootElem.tag == 'youdao-fanyi':
        for child in rootElem:
            if child.tag == 'errorCode':
                if child.text == "20":
                    return "Too long to translate\n"
                elif child.text == "30":
                    return "Cannot translate with effort\n"
                elif child.text == "40":
                    return "Cannot support this language\n"
                elif child.text == "50":
                    return "invalid key\n"
            elif child.tag == 'query':
                replyContent = "%s%s\n" % (replyContent, child.text)
            elif child.tag == 'translation':
                replyContent = '%s%s\n%s\n' % (replyContent, '-' * 3 + u'有道翻译' + '-' * 3, child[0].text)
            elif child.tag == 'basic':
                replyContent = "%s%s\n" % (replyContent, '-' * 3 + u'基本词典' + '-' * 3)
                for c in child:
                    if c.tag == 'phonetic':
                        replyContent = '%s%s\n' % (replyContent, c.text)
                    elif c.tag == 'explains':
                        for ex in c.findall('ex'):
                            replyContent = '%s%s\n' % (replyContent, ex.text)
                            
            elif child.tag == 'web':
                replyContent = "%s%s\n" % (replyContent, '-' * 3 + u'网络释义' + '-' * 3)
                for explain in child.findall('explain'):
                    for key in explain.findall('key'):
                        replyContent = '%s%s\n' % (replyContent, key.text)
                    for value in explain.findall('value'):
                        for ex in value.findall('ex'):
                            replyContent = '%s%s\n' % (replyContent, ex.text)
                    replyContent = '%s%s\n' % (replyContent,'--')
                    
    return replyContent
        
def getReplyText(msg,replyContent):
        extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
        return extTpl
def getReplyNews(msg,getcha):
        pictextTpl = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[news]]></MsgType>
                <ArticleCount>1</ArticleCount>
                <Articles>
                <item>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[%s]]></Description>
                <PicUrl><![CDATA[%s]]></PicUrl>
                <Url><![CDATA[%s]]></Url>
                </item>
                </Articles>
                <FuncFlag>1</FuncFlag>
                </xml>"""
        pictextTpl = pictextTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())), getcha[0], getcha[3],getcha[1], getcha[2])
        return pictextTpl

                
    
        
    
        