from subscription import Subscription
from news_sender import NewsSender
import os


class EmailContent:
    """An email to be sent.  First name to form the greeting part of the
    opening, email address to send to, and the formatted body.
    """
    EDITOR_PORTRAIT_LINK = ""
    BODY_HEAD = '<html><head><meta charset="UTF-8"><style>body {background-color: lightyellow}\n' \
                "table, th, td " \
                "{border:1px solid coral; border-collapse: collapse; padding:4px; " \
                "background-color: mintcream;} th {background-color: papayawhip;}" \
                "table {margin-right:40px; margin-left:40px}</style></head>\n"
    CLOSING_BOILERPLATE = "<p>That's it for today!  We'll be back tomorrow with " \
                "more headlines for you.  if you liked this, please" \
                "let us know by emailing the editors.</p><br/><p>Regards,</p><p>The Editors" \
                '<img src=' \
                '"https://icons.iconarchive.com/icons/sykonist/looney-tunes/256/Marvin-Martian-icon.png"' \
                ' style="width:100px; height:100px;"></p>' \
                '<a href="mailto:editors@ournewsroom.com">' \
                '<i>editors@ournewsroom.com</i></a></body></html>'

    def __init__(self, subscription: Subscription, newssender: NewsSender):
        self.subscription = subscription
        self.firstname: str = subscription.firstname
        self.email_address: str = subscription.email_address
        self.subscription_list = subscription.subscription_list
        self.body: str = EmailContent.BODY_HEAD
        self.retrieved_articles = None
        self.newssender = newssender

    def build_email_content(self, retrieved_articles: dict):
        self.retrieved_articles = retrieved_articles
        self.add_opening()
        self.add_news_table()
        self.add_closing()
        if self.newssender.debug:
            html_file = open("output_files/test_news.html", "w", encoding="utf-8")
            html_file.write(self.body)
            html_file.close()

    def add_news_table(self):
        '''build the news headline table for the body of the email '''
        self.body += '<table><tr>' \
                    '<th style="width:10%">Topic</th>' \
                    '<th style="width:30%">Headline</th>' \
                    '<th>Summary</th></tr>\n'
        topics = self.retrieved_articles.keys()
        for topic in topics:
            topic_articles = self.retrieved_articles[topic]
            if len(topic_articles["articles"]) == 0:
                self.body += f'<tr><td><b>{topic}</b></td>' \
                        '<td><i>No articles found for today</i></td><td/></tr>'
                continue
            first_one = True
            for article in topic_articles["articles"]:
                self.body += f'<tr><td><b>{topic}</b></td>' if first_one else '<tr><td></td>'
                first_one = False
                self.body += f'<td>{article["title"]}</td>' \
                        f'<td>{article["description"]} - <a href="{article["url"]}">' \
                        '<i>go to article</i></a></td></tr>\n'
        self.body += '</table>'

    def add_opening(self):
        self.body += f"<body><p>Good day, {self.firstname}!</p>\n" \
                    f"<p>Welcome to your daily news headline feed.  We've found " \
                    f"the top news items for your topics of interest.</p>\n"
        num_topics_of_interest: int = len(self.subscription_list)
        if num_topics_of_interest > self.newssender.max_topics_per_subscription:
            self.body += f"Just one bit of warning.  Currently, you've expressed interest " \
                         f"in {num_topics_of_interest} topics, but we only support up to " \
                         f"{self.newssender.max_topics_per_subscription}.  So, we will not be looking " \
                         f"for information on the following topics for you:<br/><ul><li>\n"
            excess_topics = self.subscription_list[
                            self.newssender.max_topics_per_subscription:num_topics_of_interest]
            excess_count = len(excess_topics)
            for topic in excess_topics:
                excess_count -= 1
                self.subscription_list.remove(topic)
                self.body += f"{topic}, " if excess_count != 0 else f"{topic}"
            self.body += "</ul></p>"
        self.body += "<p>Now, let's get started!</p>\n"

    def add_closing(self):
        self.body += EmailContent.CLOSING_BOILERPLATE
