from readit import *


if __name__ == "__main__":
    readit = Readit(subreddit="r/AskReddit", url= "https://www.reddit.com/r/AskReddit/hot/?")
    posts = readit.getAllSubmissions(limit=26)
    # urlToPostMap = readit.getFullPostLinks(posts)
    print(f'total {len(posts)} posts loaded')

