import urllib.request as req
import bs4 
import re # Regular Expression
import threading
import time
import statistics
import csv

'''
爬蟲八掛版的文章 Programming Design:
1) Get a page HTML with a list of 20 posts
2) Loop: Get title, author, push from HTML. Store with object.
3)       Threading to send request for each existing post aritical. Retrive date, content and store with object.
4) Join all threads and collect data from the current page. Store in csv file.
5) Continue on crawling next page.
'''

class Post:
    def __init__(self, title, author, push):
        self.title = title
        self.author = author
        self.push = push
        self.date = ""
        self.content = ""
        self.url = ""
    def __str__(self):
        return self.title
        
# .r-ent 貼文總覽, return: list() of post html objects
def get_post_list(soup):
    html_list = soup.find_all("div", class_ = "r-ent")
    return html_list

# .nrec 推文數量
def get_push(post_html):
    pushes = 0
    div = post_html.find("div", class_ = "nrec") # select <div> with .nrec 
    if div.span != None: # includes <span> means pushes != 0
        pushes = div.span.string
    return pushes

# .author 作者名稱
def get_author(post_html):
    div = post_html.find("div", class_ = "author")
    if div.string != "-":
        return div.string
    else:
        div = post_html.find("div", class_ = "title")
        deleted_title = div.string
        # ... [author name] > author name
        author = deleted_title[deleted_title.find('[')+1 : deleted_title.find(']')]
        return author
    

# .title 分類 + 文章標題。if no title > post nonexist
def get_title(post_html):
    div = post_html.find("div", class_ = "title")
    if div.a != None: # includes <a> means post exists
        return div.a.string
    else:
        return None

# .title > <a> 文章連結網址
def get_href(post_html):
    div = post_html.find("div", class_ = "title")
    if div.a != None: # includes <a> means post exists
        return "https://www.ptt.cc" + div.a['href']
    else:
        return None

# 從貼文內頁取得日期
def get_date(post_html):
    meta_list = post_html.find_all("div", class_ = "article-metaline")
    div = meta_list[2] # 日期的容器在第3個<div>
    date = div.find("span", class_ = "article-meta-value") # Sun Jan 26 15:26:41 2020 字串在<span>中
    return date.string.strip() # remove leading and ending spaces

# 從貼文內頁取得文章全文 #main-content
def get_content(post_html):
    div = post_html.find(id = "main-content")

    # 把推文和meta等非內文清乾淨
    for i in div.find_all("div", {'class':'push'}): 
        i.decompose()
    for i in div.find_all("div", {'class':'article-metaline'}): 
        i.decompose()
    div.find('div', class_ ="article-metaline-right").decompose()

    return div.text # .text/get_text() gets all the child strings and return concatenated using the given separator

def checkformat(soup, class_tag, data, index, url):
    content = soup.select(class_tag)[index].text
    return content

def get_comment(post_html):

    date = checkformat(post_html, '.article-meta-value', 'date', 3, url)

    #將原始碼做整理
    content = post_html.find(id="main-content").text
    target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
    #去除掉 target_content
    content = content.split(target_content)
    #print(content)
    content = content[0].split(date)
    #print(content)
    #去除掉文末 --
    main_content = content[1].replace('--', '')
    #印出內文
    print(main_content)

    return main_content

# This fuction parse and store basic information
# @return post_list: a list of Post objects
def get_post_basic(html_list):
    post_list = []
    for html in html_list:

        title = get_title(html)
        push = get_push(html)
        author = get_author(html)
        url = get_href(html)

        # print("title: ", title)
        # print("push: ", push)
        # print("author: ", author)
        # print("url: ", url)

        if title != None:
            post = Post(title, author, push)
            post.url = url
            post_list.append(post)

    return post_list

# This fuction launch a GET requset to open a sepcific post HTML, in order to crawl the post's CONTENT, TIME.
# @paraemter: Post object
# @return: Post object (with content & date)
def get_post_detail(post):

    # 1) Send requset to get 文章內頁 HTML. 
    url = post.url
    request = req.Request(url, headers={
        "cookie": "over18=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    })
    with req.urlopen(request) as response:
        html = response.read().decode("utf-8")
    # time.sleep(5)

    # 2) Get content, date.
    soup = bs4.BeautifulSoup(html, "html.parser")
    post.date = get_date(soup)
    post.content = get_content(soup)
    # print(str(post.date) + "\n" + content + "\n" +">> end thread")

    return post

# 將爬到的標題寫進csv，並print出來
def write_result(post_list):

    with open('files/ptt-gossiping.csv', 'w', newline='', encoding='utf-8') as csvfile:

        # 建立 CSV 檔寫入器
        writer = csv.writer(csvfile)
        csv_title = ["push", "title", "author", "date", "url", "content"]
        writer.writerow(csv_title)


        for post in post_list:

            # 取出物件內的變數
            title = post.title
            author = post.author
            push = post.push
            date = post.date
            content = post.content
            url =  post.url

            print("\ntitle: ", title)
            print("push: ", push)
            print("author: ", author)
            print("date: ", date)
            print("url: ", url)
            # print("content: ", content)
            
            # 寫進 scv file
            row = [push, title, author, date, url, content]
            writer.writerow(row)
    return

# This function get all titles in a signle page.
# @retrun next_link: "/bbs/Gossiping/index39154.html"
def getData(url):

    html_list = []
    post_list = []

    # Step.1 抓取 PTT 八卦版的網頁原始碼 (HTML file)
    # Create a Request object. Need over18's cookie to access Gossoping BBS.
    request = req.Request(url, headers={
        "cookie": "over18=1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    })
    with req.urlopen(request) as response:
        html = response.read().decode("utf-8")

    print(">>> end of requset")

    # Step.2 透過 bs4 解析網頁原始碼，取得每篇文章的標題、作者、推文數
    soup = bs4.BeautifulSoup(html, "html.parser")
    html_list = get_post_list(soup)
    post_list = get_post_basic(html_list)

    # Step.3 使用執行續同時對該頁面的20篇文章爬蟲，取得文章全文、發文日期時間 # https://docs.python.org/3/library/threading.html#thread-objects
    thread_pool = []
    for i in range(len(post_list)): # 平行做爬蟲 > Thread.start()
        post = post_list[i]
        thread_pool.append(threading.Thread(target = get_post_detail, args = (post,)))
        thread_pool[i].start()
        # print("thread_pool["+ str(i) +"].start()")
    for i in range(len(post_list)): # 等待所有執行續都結束 > Thread.join()
        thread_pool[i].join()
        # print("thread_pool["+ str(i) +"].join()")

    # Step.4 儲存20篇的 Post 成 csv file
    write_result(post_list)

    # Step.5 抓取上一頁的連結並 return
    next_link = soup.find("a", string = "‹ 上頁") # 搜尋內文是"‹ 上頁"的<a>
    return next_link["href"]

# main codes
def main():
    time_list = []
    pageURL = "https://www.ptt.cc/bbs/Gossiping/index.html"
    
    count = 0
    while count < 1:
        tStart = time.time() # 計時開始

        # getData() : /bbs/Gossiping/index39154.html
        pageURL = "https://www.ptt.cc" + getData(pageURL)
        print(pageURL + "\n")

        tEnd = time.time() # 計時結束
        time_list.append(tEnd - tStart)
        count += 1

    print("Average time per page: ", statistics.mean(time_list))
    return

if __name__ == "__main__":
    main()
    pass

'''
<div class="r-ent">
    <div class="nrec"><span class="hl f2">3</span></div> # 沒有推文: <div class="nrec"></div>
    <div class="title">
        <a href="/bbs/Gossiping/M.1579684896.A.B64.html">Re: [問卦] 我大膽預言</a>
    </div>
    <div class="meta">
        <div class="author">CavendishJr</div>
        <div class="article-menu">
            <div class="trigger">&#x22ef;</div>
            <div class="dropdown">
                <div class="item"><a href="/bbs/Gossiping/search?q=thread%3A%5B%E5%95%8F%E5%8D%A6%5D&#43;%E6%88%91%E5%A4%A7%E8%86%BD%E9%A0%90%E8%A8%80">搜尋同標題文章</a></div>
                <div class="item"><a href="/bbs/Gossiping/search?q=author%3ACavendishJr">搜尋看板內 CavendishJr 的文章</a></div>               
            </div>      
        </div>
        <div class="date"> 1/22</div>
        <div class="mark"></div>
    </div>
</div>

<div class="r-ent">
    <div class="nrec"><span class="hl f2">3</span></div>
    <div class="title">
    
        (本文已被刪除) [fatslave]
    
    </div>
    <div class="meta">
        <div class="author">-</div>
        <div class="article-menu"></div>
        <div class="date"> 1/22</div>
        <div class="mark"></div>
    </div>
</div>
'''