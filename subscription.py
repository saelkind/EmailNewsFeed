from typing import List
from news_sender import NewsSender
import requests
from pprint import pprint
from datetime import date, timedelta

class Subscription:
    '''Subscription for one person.  Has his/her name, email address. and a list of
    topics of interest
    For any given subscription, it finds news items of interest to the subscriber,
    by connecting to the news source using the apinews.org API key,
    and retrieves news articles for the subscription.
    then builds email with the list in a nicely-formatted (hah!) manner
    Finally,, it sends the email to the subscriber

    '''

    IDX_FIRSTNAME = 0
    IDX_LASTNAME = 1
    IDX_EMAIL = 2
    IDX_TOPIC_LIST = 3
    NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, newssender: NewsSender, subscription_rec: list):
        self.newssender = newssender
        self.firstname: str = subscription_rec[Subscription.IDX_FIRSTNAME]
        self.lastname: str = subscription_rec[Subscription.IDX_LASTNAME]
        self.email_address: str = subscription_rec[Subscription.IDX_EMAIL]
        subscription_list_str: str = subscription_rec[Subscription.IDX_TOPIC_LIST]
        self.subscription_list: list = subscription_list_str.split(",")
        for i in range(0, len(self.subscription_list) - 1):
            self.subscription_list[i] = self.subscription_list[i].strip()
            self.subscription_list[i].replace(" ", "+")
        self.email_content = None

    def process_subscription(self) -> (int, int):
        # hack to avoid circular refs.  What a PITA
        from email_content import EmailContent
        self.email_content = EmailContent(self, self.newssender)
        topics_retrieved: dict = {}
        topics_done = 0
        for topic in self.subscription_list:
            if topics_done == self.newssender.max_topics_per_subscription:
                # don't bother the API server for excess topics in this subscription
                break
            topics_retrieved[topic] = self.get_news(topic)
            topics_done += 1
        self.email_content.build_email_content(topics_retrieved)
        print("done!")

    def get_news(self, topic: str) -> dict:
        # news.org free license only permits news that's >= 24 hours old
        yesterday = date.today() - timedelta(days=1)
        sort_by = f"&sortBy={self.newssender.sort_order}"
        search_in = f"&searchin=description"
        date_str = yesterday.strftime("%Y-%m-%d")
        url = f"{Subscription.NEWS_API_BASE_URL}?q={topic}"
        url += f"&from={date_str}&language=en" \
              f"{search_in}{sort_by}" \
              f"&pageSize={self.newssender.max_articles_per_topic}" \
              f"&apiKey={self.newssender.news_api_key}"
        response = requests.get(url=url, timeout=10)
        articles = response.json()
        articles_avail = articles["totalResults"]
        articles_retr = len(articles["articles"])
        if self.newssender.debug:
            print(f"\n\nrequest for topic \"{topic}\":\nstatus: {response.status_code}\n"
                  f"total articles found: {articles_avail}\narticles retrieved: {articles_retr}")
        # TODO put logger in here
        return {"topic": f"{topic}", "articles": articles["articles"]}


if __name__ == '__main__':
    news_sender = NewsSender()
    subscription_rec = ["Steven", "Elkind", "selkind@aol.com",
                        "Tesla, Ford, Powerwall, Marshmallows, Whipped Cream, Butterscotch"]
    subscription = Subscription(news_sender, subscription_rec)
    subscription.process_subscription()
