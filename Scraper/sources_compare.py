non_news = open("non_news_users.txt", "a")
t500 = open("t500.txt", "r")
news = open("NewsList.txt", "r")

is_news = False

for line in t500:
    for user in news:
        if(line.lower() == user.lower()):
            is_news = True
    if(is_news == False):
        non_news.write(line)
    is_news = False
    news.seek(0)

non_news.close()
t500.close()
news.close()