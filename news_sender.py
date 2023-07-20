from typing import List
from article import Article
from subscription import Subscription
import json
import requests
from pprint import pprint
from datetime import date, timedelta


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

    MAX_ARTICLES_PER_TOPIC: int = 5
    EMAIL_ACCT_FILENAME = "files/accounts.json"
    EMAIL_TIMEOUT_MS = 10000
    IDX_STATUS = 0
    IDX_ERR_MSG = 2
    IDX_SUBJECTS_FOUND = 3
    IDX_TOT_SENT = 4

    def __init__(self):
        file = open(NewsSender.EMAIL_ACCT_FILENAME, "r")
        acct_data = json.load(file)
        self.sender_account = acct_data["email_account"]
        sender_pwd = acct_data["email_pwd"]
        self.sender_account_connection = self.open_email_account_connection(sender_pwd)
        self.news_api_key = acct_data["news_api_key"]
    def open_email_account_connection(self, password) -> (bool, str):
        '''Open the connection to the email account.  If the connection fails,
        return False and the relevant error message to the caller.  Do  not store
        the password in anything but a local var.  Also, not committing my real accounts.json
        file to the repository, only an example one'''
        pass

    def process_subscription(self, subscription: Subscription) -> (bool, str, int, int):
        pass

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
              f"&pageSize={NewsSender.MAX_ARTICLES_PER_TOPIC}" \
              f"&apiKey={self.news_api_key}"
        response = requests.get(url=url, timeout=10)
        articles = response.json()
        # don't find out which of these is more performant (if either)
        # string.json() is a shortcut for the json.loads(), but it is more
        # robust in the it checks the character encoding first
        # articles = json.loads(response.text)
        articles_avail = articles["totalResults"]
        articles_retr = len(articles["articles"])
        print(f"\n\nrequest for topic \"{topic}\":\nstatus: {response.status_code}\n" \
              f"total articles found: {articles_avail}\narticles retrieved: {articles_retr}")
        # TODO put logger in here
        if articles_retr > 0:
            print(json.dumps(articles, indent=4))
            print(json.dumps(articles["articles"][0], indent=4))
            print("\n\npublished by:", articles["articles"][0]["source"]["name"])
            print("author:", articles["articles"][0]["author"])
            print("title:", articles["articles"][0]["title"])
            print("description:", articles["articles"][0]["description"])
            print("url:", articles["articles"][0]["url"])

    def send_email(self, email) -> (bool, str):
        pass


if __name__ == '__main__':
    news_sender = NewsSender()
    news_sender.get_news("Powerwall")
    news_sender.get_news("Tesla")
