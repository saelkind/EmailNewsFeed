from news_sender import NewsSender
import requests
import logging

class Subscription:
    """
    Convenience class with static methods for processing one subscription at a time.
    For any given subscription, it finds news items of interest to the subscriber,
    by connecting to the news source using the apinews.org API key,
    and retrieves news articles for the cls.
    It then builds and sends the email with the list in a nicely-formatted (hah!)
    manner.  Finally,, it sends the email to the subscriber
    """

    IDX_FIRSTNAME = 0
    IDX_LASTNAME = 1
    IDX_EMAIL = 2
    IDX_TOPIC_LIST = 3
    NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"
    NEWS_EMAIL_SUBJECT = "Your daily NewsFeed from Marvin"

    @classmethod
    def process_subscription(cls, this_subs_rec: list, newssender: NewsSender) -> dict:
        """
        Process one subscription, retrieving articles for each topic in the subscription
        :param this_subs_rec: the list containing subscriber info
        :param newssender: the already-connected NewsSender object that also contains
            config params
        :return: list with email sent OK, error msg if not, topics requested, topics processed, articles retrieved
        """
        logger = logging.getLogger(NewsSender.LOGGER_NAME)
        firstname: str = this_subs_rec[cls.IDX_FIRSTNAME]
        lastname: str = this_subs_rec[cls.IDX_LASTNAME]
        email_address: str = this_subs_rec[cls.IDX_EMAIL]
        subscription_list: list = this_subs_rec[cls.IDX_TOPIC_LIST]
        topics_requested = len(subscription_list)
        articles_retrieved, topics_done, topics_retrieved = \
            cls.process_topics(newssender, subscription_list)
        # Hack alert!!!!! circular reference avoidance
        from email_content import EmailContent
        email_content = EmailContent(this_subs_rec, newssender)
        email_content.build_email_content(topics_retrieved)
        status_list = newssender.send_html_email("Your daily NewsFeed",
                                                 email_content.body,
                                                 [this_subs_rec[cls.IDX_EMAIL]])
        logger.info(f"{email_address}: done processing subscription")
        logger.info(f"{email_address}: {topics_done} completed out of {topics_requested} requested; "
                    f"{articles_retrieved} total articles retrieved")
        return {"email_sent": status_list[0],
                "error_msg": status_list[1],
                "topics_requested": topics_requested,
                "topics_retrieved": len(topics_retrieved),
                "articles_retrieved": articles_retrieved}

    @classmethod
    def process_topics(cls, newssender, subscription_list):
        topics_retrieved: dict = {}
        topics_done = 0
        articles_retrieved = 0
        for topic in subscription_list:
            if topics_done == newssender.max_topics_per_subscription:
                # don't bother the API server for excess topics in this subscription
                break
            topics_retrieved[topic] = cls.get_news(topic, newssender)
            topics_done += 1
            articles_retrieved += len(topics_retrieved[topic]["articles"])
        return articles_retrieved, topics_done, topics_retrieved

    @classmethod
    def get_news(cls, topic: str, newssender: NewsSender) -> dict:
        """
        Get the top news articles for the topic from yesterday, return them as a
        dict with two n-v pairs - topic name, and a list of relevant articles
        :param topic: the topic of interest (str)
        :param newssender: the connected NewsSender object, with contains the
            config params
        :return: dict with two n-v pairs - topic name & list of relevant articles
        """
        # news.org free license only permits news that's >= 24 hours old
        logger = logging.getLogger(NewsSender.LOGGER_NAME)
        sort_by = f"&sortBy={newssender.sort_order}"
        search_in = f"&searchin=description"
        url = f"{cls.NEWS_API_BASE_URL}?q={topic}"
        url += f"&from={newssender.date_str}&language=en" \
              f"{search_in}{sort_by}" \
              f"&pageSize={newssender.max_articles_per_topic}" \
              f"&apiKey={newssender.news_api_key}"
        response = requests.get(url=url, timeout=10)
        articles = response.json()
        articles_avail = articles["totalResults"]
        articles_retr = len(articles["articles"])
        logger.debug(f"Request for topic \"{topic}\":\nstatus: {response.status_code}, "
                  f"total articles found: {articles_avail}\narticles retrieved: {articles_retr}")
        return {"topic": f"{topic}", "articles": articles["articles"]}


# if __name__ == '__main__':
#     news_sender = NewsSender()
#     if news_sender.debug:
#         subscription_record = ["Steven", "Elkind", "selkind@aol.com",
#                             "Tesla, Ford, Powerwall, Marshmallows, Whipped Cream, Butterscotch"]
#         subscription = Subscription(news_sender, subscription_record)
#         cls.process_subscription()
