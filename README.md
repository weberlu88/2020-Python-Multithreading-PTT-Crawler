# 2020-Python-Multithreading-PTT-Crawler

`2020/1/27` `Created by Weber Lu`

## Outcome Present


> @Input: None. Can alter the amount of page to crawl in `main()` manually.  
@Output: `ptt-gossiping.csv` file and info in console.


* **Previous version**: In `18_crawler.py`, it could only crawl the post titles.
![](https://i.imgur.com/iseRS7h.png)

* **Multi-thread version**: Program `19_crawler-with-thread.py` support downward access to each aritical in post list, in order to get **precise datetime** and **full aritical content**. Getting the comments below is capable, but no needed.
Here, you see the csv file I produced. And you may compared to the post list present by web browser. The comment amount may have a bit different due to the time gap where I take screenshots. 
![](https://i.imgur.com/Wei1SZt.jpg)
![](https://i.imgur.com/c0dO4NU.jpg)

* **Average time**: With Multi-threading, it takes less time to access and parse the aritical page.
![](https://i.imgur.com/VDkpcoJ.png)



## Program Design

1) Get a page HTML with a list of 20 (or so) posts.
2) Loop: 
    * Get title, author, push from HTML. Store with object.     
    * Threading to send request for each existing post aritical. Retrive date, content and store with object.
3) Join all threads and collect data from the current page. Store in csv file.
4) Continue on crawling next page.

```
main()
`-- getData(pageURL)
    |-- get_post_list(soup)
    |
    |-- get_post_basic(html_list)
    |    |-- get_title(post_html)
    |    |-- get_push(post_html)
    |    |-- get_author(post_html)
    |    `-- get_href(post_html)
    |
    |-- get_post_detail(post)
    |    |-- get_date(soup)
    |    `-- get_content(soup)
    |
    `-- write_result(post_list)
```

## Techniques

### 1. Basic knowledge of web programming, including HTML format, web api connecting, Google Chrome developing tools.
Web crawling is easy but stupid. If you have both url and permission to the service api, there's no need for web crawling. Only when we can't access to the server directly will we resort to crawrling. So if you know how to get PTT's articals by telnet protocol, skip my method :D.

Web crawling has 2 steps, that is
* Send a https requset to get the HTML file from server.
```python
# Step.1 抓取 PTT 八卦版的網頁原始碼 (HTML file)
# Create a Request object. Need over18's cookie to access Gossoping BBS.
import urllib.request as req
request = req.Request(url, headers={
    "cookie": "over18=1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
})
with req.urlopen(request) as response:
    html = response.read().decode("utf-8")
```
* Parse the HTML file, here we apply with python's beautiful soup package.
```python
# Step.2 透過 bs4 解析網頁原始碼，取得每篇文章的標題、作者、推文數
import bs4 
soup = bs4.BeautifulSoup(html, "html.parser")
```

### 2. Multi-threading concept
Because crawling *N* aritical page under a list requires *N* times of connection. If get the content of the aritical page one by one, it takes *N* more connection time. But under multi-threading, it only takes **one** connection time. Each thread will access the aritical page simultaneously.
```python
import threading
threading.Thread(target = FUNCTION, args = (ARGS,))
```
```python
# Step.3 使用執行續同時對該頁面的20篇文章爬蟲，取得文章全文、發文日期時間 
# https://docs.python.org/3/library/threading.html#thread-objects
    thread_pool = []
    
    for i in range(len(post_list)): # 平行做爬蟲 > Thread.start()
        post = post_list[i]
        thread_pool.append(threading.Thread(target = get_post_detail, args = (post,)))
        thread_pool[i].start()
        # print("thread_pool["+ str(i) +"].start()")
        
    for i in range(len(post_list)): # 等待所有執行續都結束 > Thread.join()
        thread_pool[i].join()
        # print("thread_pool["+ str(i) +"].join()")
```
    
### 3. Object-oriented concept
We create our own `Post` class to store the attributes, which are *title, author, push, date, content*, and *url*.
```python
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
```


###### tags: `Github` `Python` `Web Crawl`
