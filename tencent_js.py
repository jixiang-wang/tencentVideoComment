from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import pymongo


# 连接到Mongo
conn = pymongo.MongoClient(host='localhost', port=27017)
# 选择或创建数据库
tencent = conn['tencent']
# 选择或创建数据集合
newsdata = tencent['鬼吹灯之黄皮子坟']

# 把每个评论的数据存入这个字典
comment_one = {}
# 使用Chrome浏览器模拟打开网页，但是要把下载的chromedriver.exe放在python的文件路径下,
#调试好之后换成PhantomJs,速度应该会快一点
driver = webdriver.Chrome()
driver.get("https://v.qq.com/tv/p/topic/gcdzhpzf/index.html")
# 下拉滑动浏览器屏幕，具体下拉多少根据自己实际情况决定
driver.execute_script("window.scrollBy(0,10000)")
time.sleep(8)
driver.execute_script("window.scrollBy(0,6000)")
time.sleep(3)

i = 0
# 这里必须要先切到你要爬取数据的frame下，否则找不到你写的路径
driver.switch_to.frame('commentIframe1')
# 这里我用的是find_elements_by_xpath匹配的元素，个人比较喜欢用xpath匹配，比较简单方便
comments_name = driver.find_elements_by_xpath(
    '//div[@class="np-post-header"]/span[1]/a[1]')
comments_content = driver.find_elements_by_xpath(
    '//div[@id="allComments"]//div[@class="np-post-content"]')
comments_vote = driver.find_elements_by_xpath(
    '//div[@class="np-post-footer"]/a[1]/em')

print("第%s页" % i)
print(comments_name)
#存入字典
for comment_name, comment_content, comment_vote in zip(
        comments_name[-10: ], comments_content[-10: ], comments_vote[-10: ]):
    comment_one = {
        '评论者': comment_name.text,
        '评论内容': comment_content.text,
        '评论赞': comment_vote.text
    }
    # 把数据插入数据库
    newsdata.insert_one(comment_one)
#下面是爬取多页的评论数据，同上
while driver.find_element_by_xpath('//div[@id="loadMore"]').text == '加载更多':
    page_a = len(comments_name)
    driver.find_element_by_xpath('//div[@id="loadMore"]').click()
    time.sleep(5)
    driver.execute_script("window.scrollBy(0,6000)")
    time.sleep(3)
    comments_name = driver.find_elements_by_xpath(
        '//div[@class="np-post-header"]/span[1]/a[1]')
    comments_content = driver.find_elements_by_xpath(
        '//div[@id="allComments"]//div[@class="np-post-content"]')
    comments_vote = driver.find_elements_by_xpath(
        '//div[@class="np-post-footer"]/a[1]/em')
    page_b = len(comments_name)
    i += 1
    print("第%s页" % i)

    for comment_name, comment_content, comment_vote in zip(
            comments_name[page_a:page_b], comments_content[page_a:page_b], comments_vote[page_a:page_b]):
        comment_one = {
            '评论者': comment_name.text,
            '评论内容': comment_content.text,
            '评论赞': comment_vote.text
        }
        newsdata.insert_one(comment_one)

