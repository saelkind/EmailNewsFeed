from typing import List
from article import Article
from subscription import Subscription
import json
import requests
from pprint import pprint
from datetime import date, timedelta


# TODO Refactor NewsSender by moving the email retrieval and building for each email
#  into NewsEmail. Processing through the subscriptions needs to go into
#  Subscription.  Maybe even further refactoring into NewsRetriever  \
#  Just leave
class NewsSender:
    '''For any given subscription, the NewsSender located news items of intereest
    to the subscriber, then emails the list in a nicely-formatted (hah!) email
    to the subscriber
    The NewsSender also maintains a connection to the News Feed's email account for
    sending the emails
    Finally, the NewsSender connects to the New source using the news.org API key,
    and retrieves news articles for the subscription.
    All account information is read from the
    '''

    EMAIL_ACCT_FILENAME = "files/config.json"
    CONFIG_KEYWORDS: dict = {"email_account", "email_pwd", "news_api_key",
                            "max_articles_per_topic", "max_topics_per_subscription",
                            "sort_order", "email_timeout_ms", "debug"}
    IDX_STATUS = 0
    IDX_ERR_MSG = 2
    IDX_SUBJECTS_FOUND = 3
    IDX_TOT_SENT = 4
    DEBUG = True


    def __init__(self):
        ''' Read the config file for the app.   Contains email acct info,
        apinews.org API key, max topics per subscription and mas headlines
        retrieved per topic, and the order of preference for selecting
        each top article list to send
        '''
        config_data: dict = {}
        try:
            file = open(NewsSender.EMAIL_ACCT_FILENAME, "r")
            config_data = json.load(file)
        except Exception as e:
            print("Error opening config file, will exit:", e)
            exit(1)
        config_keys_found = config_data.keys()
        config_keys_needed = NewsSender.CONFIG_KEYWORDS
        missing_keys = []
        extra_keys = []
        for key in config_keys_found:
            if key not in config_keys_needed and key != "_comment_":
                extra_keys.append(key)
        for key in config_keys_needed:
            if key not in config_keys_found:
                missing_keys.append(key)
        if len(extra_keys) != 0:
            print("Warning, extra config parameters found and ignored:")
            print("\t", extra_keys)
        if len(missing_keys) != 0:
            print("Error: missing required config parameter(s), exiting:")
            print("\t", missing_keys)
            exit(1)
        self.sender_account = config_data["email_account"]
        sender_pwd = config_data["email_pwd"]
        self.sender_account_connection = self.open_email_account_connection(sender_pwd)
        self.news_api_key = config_data["news_api_key"]
        self.max_articles_per_topic = config_data["max_articles_per_topic"]
        self.max_topics_per_subscription = config_data["max_topics_per_subscription"]
        self.email_timeout_ms = config_data["email_timeout_ms"]
        self.debug = config_data["debug"].strip().upper() == "TRUE"

    def open_email_account_connection(self, password) -> (bool, str):
        '''Open the connection to the email account.  If the connection fails,
        return False and the relevant error message to the caller.  Do  not store
        the password in anything but a local var.  Also, not committing my real config.json
        file to the repository, only an example one'''
        pass

    def process_subscription(self, this_subscription: Subscription) -> (int, int):
        topics = this_subscription.subscription_list
        topics_retrieved: dict = {}
        for topic in topics:
            topics_retrieved[topic] = self.get_news(topic)
        email_body: str = self.build_email_body(this_subscription, topics_retrieved)

    def get_news(self, topic: str) -> dict:
        # news.org free license only permits news that's >= 24 hours old
        yesterday = date.today() - timedelta(days=1)
        sort_by = "&sortBy=relevancy"
        # sort_by = "popularity"
        # sort_by = ""
        search_in = f"&searchin=description"
        # search_in = ""
        date_str = yesterday.strftime("%Y-%m-%d")
        url = f"https://newsapi.org/v2/everything?q={topic}" \
              f"&from={yesterday}&language=en" \
              f"{search_in}{sort_by}" \
              f"&pageSize={self.max_articles_per_topic}" \
              f"&apiKey={self.news_api_key}"
        response = requests.get(url=url, timeout=10)
        articles = response.json()
        # don't find out which of these is more performant (if either)
        # string.json() is a shortcut for the json.loads(), but it is more
        # robust in that it checks the character encoding first
        # articles = json.loads(response.text)
        articles_avail = articles["totalResults"]
        articles_retr = len(articles["articles"])
        if self.debug:
            print(f"\n\nrequest for topic \"{topic}\":\nstatus: {response.status_code}\n" \
                  f"total articles found: {articles_avail}\narticles retrieved: {articles_retr}")
        # TODO put logger in here
        return {"topic": f"{topic}", "articles": articles["articles"]}

    def build_email_body(self, this_subscription: Subscription, retrieved_articles: dict) -> str:
        body:str = "<html><head><style>body {background-color: lightyellow}\n" \
                   "table, th, td " \
                   "{border:1px solid coral; border-collapse: collapse; padding:4px; " \
                   "background-color: mintcream;} th {background-color: papayawhip;}</style></head>\n" \
                   f"<body><p>Good day, {this_subscription.firstname}!</p>\n" \
                   f"<p>Welcome to your daily news headline feed.  We've found " \
                   f"the top news items for your topics of interest.</p>\n"
        num_topics_of_interest: int = len(this_subscription.subscription_list)
        if num_topics_of_interest > self.max_topics_per_subscription:
            body += f"Just one bit of warning.  Currently, you've expressed interest" \
                    f"in {num_topics_of_interest} topics, but we only support up to" \
                    f"{self.max_topics_per_subscription}.  So, we will not be looking" \
                    f"for information on the following topics for you:<br/><ul><li>\n"
            for topic in this_subscription.subscription_list[self.max_topics_per_subscription:num_topics_of_interest]:
                body += f"{topic}, "
            body += "</ul></p>"
        body += "<p>Now, let's get started!</p>\n"
        body += '<table><tr>' \
                '<th style="width:10%">Topic</th>' \
                '<th style="width:30%">Headline</th>' \
                '<th>Summary</th></tr>\n'
        topics = retrieved_articles.keys()
        for topic in topics:
            topic_articles = retrieved_articles[topic]
            if len(topic_articles["articles"]) == 0:
                body += f'<tr><td><b>{topic}</b></td>' \
                        '<td><i>No articles found for today</i></td><td/></tr>'
                continue
            first_one = True
            for article in topic_articles["articles"]:
                body += f'<tr><td><b>{topic}</b></td>' if first_one else '<tr><td></td>'
                first_one = False
                body += f'<td>{article["title"]}</td>' \
                        f'<td>{article["description"]} - <a href="{article["url"]}">' \
                        '<i>go to article</i></a></td></tr>\n'
        body += '</table>'
        body += "<p>That's it for today!  We'll be back tomorrow with " \
                "more headlines for you </p><br/><p>Regards,</p><p>The Editors" \
                '<img src="https://icons.iconarchive.com/icons/sykonist/looney-tunes/256/Marvin-Martian-icon.png"' \
                ' style="width:100px; height:100px;"></p></html>'
        if self.debug:
            html_file = open("C:\\Users\\selki\\Desktop\\new3.html", "w")
            html_file.write(body)
            html_file.close()
        return body





    def send_email(self, email) -> (bool, str):
        timeout = self.email_timeout_ms
        pass


if __name__ == '__main__':
    news_sender = NewsSender()
    subscription = Subscription()
    subscription.firstname = "Steve"
    subscription.subscription_list = ["Tesla", "Powerwall", "Ford"]
    news_sender.get_news("Powerwall")
    news_sender.get_news("Tesla")
    news_sender.process_subscription(subscription)
