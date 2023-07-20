from subscription import Subscription
from typing import List
from article import Article


class NewsEmail:
    """An email to be sent.  First name to form the greeting part of the
    opening, email address to send to, and the formatted body.
    """
    BODY_HEAD = "<html><body>"
    CLOSING_BOILERPLATE = "<p>So that's all for today,  if you liked this, please" \
                         "let us know by emailing the editors." \
                         "<br/><p>Regards,</p>" \
                         "<p>Your Friendly Editing Staff</p>" \
                         '<p><a href="editors@ournewsroom.com">' \
                         "<i>editors@ournewsroom.com</i></a></body></html>"

    def __init__(self, subscription: Subscription):
        self.firstname: str = subscription.firstname
        self.email_address: str = subscription.email_address
        self.body: str = NewsEmail.BODY_HEAD

    def add_topic_list(self, article_list: List[Article]):
        pass

    def add_opening(self):
        self.body += f"<br/><p>Hi {self.firstname}.</p>" \
                "<p> Welcome to your customized news feed for today</p>"

    def add_closing(self):
        self.body += NewsEmail.CLOSING_BOILERPLATE
