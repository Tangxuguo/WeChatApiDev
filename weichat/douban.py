#coding:utf-8
import json
import sys
import urllib2
reload(sys)
sys.setdefaultencoding('utf-8')

def douban_music(content):
        query_str = content
        DOUBAN_API_KEY = "0f1a47ce6e21028e2d4ed76b4a6307aa"
        bookurlbase = " https://api.douban.com/v2/music/search"
        searchkeys = urllib2.quote(query_str)
        url = '%s?q=%s&apikey=%s' % (bookurlbase,searchkeys,DOUBAN_API_KEY) 
        resp = urllib2.urlopen(url)
        music = json.loads(resp.read())
        id = music["musics"][0]["id"]
        musicurlbase_1 = "http://api.douban.com/v2/music/"
        url_1 = '%s%s?apikey=%s' %(musicurlbase_1,id,DOUBAN_API_KEY)
        resp_1 = urllib2.urlopen(url_1)
        res = json.loads(resp_1.read())
        title = res["title"]
        image = res["image"]
        alt = res["alt"]
        description = res["summary"]
        return (title,image,alt,description)
def douban_book(content):
        query_str = content
        DOUBAN_API_KEY = "0f1a47ce6e21028e2d4ed76b4a6307aa"
        bookurlbase = " https://api.douban.com/v2/book/search"
        searchkeys = urllib2.quote(query_str)
        url = '%s?q=%s&apikey=%s' % (bookurlbase,searchkeys,DOUBAN_API_KEY) 
        resp = urllib2.urlopen(url)
        book = json.loads(resp.read())
        id = book["books"][0]["id"]
        bookurlbase_1 = "http://api.douban.com/v2/book/"
        url_1 = '%s%s?apikey=%s' %(bookurlbase_1,id,DOUBAN_API_KEY)
        resp_1 = urllib2.urlopen(url_1)
        res = json.loads(resp_1.read())
        title = book["books"][0]["title"]
        image = book["books"][0]["images"]["large"]
        alt = book["books"][0]["alt"]
        description = res["summary"]
        return (title,image,alt,description)

def douban_movie(content):
        query_str = content
        DOUBAN_API_KEY = "0f1a47ce6e21028e2d4ed76b4a6307aa"
        movieurlbase = "http://api.douban.com/v2/movie/search"
        searchkeys = urllib2.quote(query_str) 
        url = '%s?q=%s&apikey=%s' % (movieurlbase, searchkeys, DOUBAN_API_KEY)
        resp = urllib2.urlopen(url)
        movie = json.loads(resp.read())
        id = movie["subjects"][0]["id"] 
        movieurlbase_1 = "http://api.douban.com/v2/movie/subject/"
        url_1 = '%s%s?apikey=%s' % (movieurlbase_1,id, DOUBAN_API_KEY)
        resp_1 = urllib2.urlopen(url_1)
        res = json.loads(resp_1.read())
        description = res["summary"]
        title=movie["subjects"][0]["title"]
        image=movie["subjects"][0]["images"]["large"]
        alt=movie["subjects"][0]["alt"]
        return (title,image,alt,description)