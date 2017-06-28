import sys
sys.path.append('./')
from contentExtraction import contentExtractionTool

f = open('example-bbc-news.html', 'r')
htmlCode = f.read()

ceTool = contentExtractionTool()
body = ceTool.mainContent(htmlCode)
print(body.text)

print('____________')
dt = ceTool.publishDate(htmlCode)
if(dt):
    print(dt)
