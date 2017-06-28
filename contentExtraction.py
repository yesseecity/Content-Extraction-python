# coding=UTF-8
from bs4 import BeautifulSoup
import re
from dateutil import parser

class contentExtractionTool:

    def __init__(self):
        self.removeList = {
            'class':['Header', 'Footer', 'header', 'footer', 'topbar', 'ArticleList', 'LinkList', 'links', 'banner', 'leaderboard', 'related', 'avatar', 'previous', 'next', 'feed', 'navbar', 'menu'],
            'id':['links', 'header', 'footer', 'banner', 'leaderboard', 'related'],
            'tag':['script', 'noscript', 'iframe', 'header', 'footer', 'style', 'a'],
            'other':['list', 'link', 'sidebar', 'ad', 'banner', 'related', 'lightbox', 'header', 'footer', 'social', 'comment', 'copyright', 'pop', 'dialog', 'subscription', 'billboard', 'a2a' ,'author', 'navi', 'secondary']
        }

        self.preserveList = {
            'class':['mark-links', 'post_list', 'with,sidebar','-,sidebar', 'image,popup', 'primary,secondary', 'lazyloaded', 'load', 'loaded', 'pad', 'category,banner'],
            'iframe': ['youtube', 'vimeo', 'facebook', 'line']
        }

        self.publishNameList = ['publish', 'published', 'date', 'created', 'entry-date']

    def _removeByClassName(self, className, dom):
        while (len(dom.select('.'+className))>0):
            dom.select('.'+className)[0].extract()
            # print(len(dom.select('.'+className)))

    def _removeByTagName(self, tagName, dom):
        while (len(dom.select(tagName))>0):
            dom.select(tagName)[0].extract()
            # print(len(dom.select(tagName)))

    def _removeById(self, id, dom):
        while (len(dom.select('#'+id))>0):
            dom.select('#'+id)[0].extract()
            # print(len(dom.select('#'+id)))

    def _removeIframe(self, dom):
        iframeTags = dom.select('iframe')
        for iframe in iframeTags:
            inPreserveList = False;
            for preserve in self.preserveList['iframe']:
                if (len(re.findall( preserve, str(iframe)))>0):
                    inPreserveList = True
            if (not inPreserveList):
                # print('remove it!!')
                iframe.extract()

    def _removeHyperlink(self, dom):
        for hyperLink in dom.select('a'):
            hasIMG = False
            for child in hyperLink.children:
                if (child.name == 'img'):
                    hasIMG = True
            if (not hasIMG):
                hyperLink.extract();

    def _searchInAttr(self, keyword, dom):
        tmpClassList = [];
        tmpIdList = [];

        re1 = re.compile('((class|id)=")((\\s|\\w|-)*'+keyword+'(\\s|\\w|-)*)(")')
        if (re1.search(str(dom))):
            regExpFound = re.findall(re1, str(dom))
            for regExpFound in re.findall(re1, str(dom)):
                keywordType = regExpFound[1]

                if (keywordType == 'class'):
                    for v in regExpFound[2].split(' '):
                        hasKeyword = re.search('\\b'+keyword, v)
                        if (hasKeyword) :
                            tmpClassList.append(v)
                elif (keywordType == 'id'):
                    for v in regExpFound[2].split(' '):
                        hasKeyword = re.search('\\b'+keyword, v)
                        if (hasKeyword) :
                            tmpIdList.append(v)

                # for v in regExpFound[2].split(' '):
                #     hasKeyword = re.search('\\b'+keyword, v)
                #     if (hasKeyword) :
                #         if (keywordType == 'class'):
                #             tmpClassList.append(v)
                #         elif (keywordType == 'id'):
                #             tmpIdList.append(v)


            for className in tmpClassList:
                for pClassName in self.preserveList['class']:
                    # print('pClassName: ', pClassName)
                    classNamePreserve = all(re.search(v, className)   for v in pClassName.split(','))
                    if classNamePreserve:
                        tmpClassList.remove(className)


            # print('tmpIdList: ',tmpIdList)
            # print('tmpClassList: ',tmpClassList)

            return {
                'id': tmpIdList,
                'class': tmpClassList
            }


    def mainContent(self, htmlCode):
        try:
            htmlDOM = BeautifulSoup(htmlCode)
            body = htmlDOM.select('body')[0]

            for keyword in self.removeList['tag']:
                if(keyword == 'iframe'):
                    self._removeIframe(body);
                elif (keyword == 'a'):
                    self._removeHyperlink(body);
                else:
                    self._removeByTagName(keyword, body);

            for keyword in self.removeList['class']:
                self._removeByClassName(keyword, body);

            for keyword in self.removeList['id']:
                self._removeById(keyword, body);

            for keyword in self.removeList['other']:
                attr = self._searchInAttr(keyword, body)
                if(attr):
                    for domId in attr['id']:
                        self._removeById(domId, body);
                    for className in attr['class']:
                        self._removeByClassName(className, body);

            return body
        except Exception as e:
            raise e

    def publishDate(self, htmlCode):
        htmlDOM = BeautifulSoup(htmlCode)
        for className in self.publishNameList:
            for dom in htmlDOM.select('.'+className):
                publishedDate = None
                try:
                    if ('datetime' in dom.attrs):
                        dt = parser.parse(dom.attrs['datetime'])
                        print(dt)
                    elif ('data-datetime' in dom.attrs):
                        dt = parser.parse(dom.attrs['data-datetime'])
                        print(dt)
                    else:
                        dt = parser.parse(dom.text)
                    timeISO8601 = dt.isoformat()
                    # print(timeISO8601)
                    return timeISO8601
                    # return dt
                except Exception as e:
                    return None

