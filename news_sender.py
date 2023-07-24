import json
import smtplib
from email.message import EmailMessage
from datetime import date, timedelta
import time
import logging
from logging.handlers import RotatingFileHandler


class NewsSender:
    """
    The NewsSender maintains a connection to the News Feed's email account for
    sending emails to subscribers, and sends the emails.

    All account information is read from the config file, and in addition all the
    external config options for the app.  Done here, since I do not want to
    retain the email account password persistently in memory and only want to
    read the file one time.
    """

    CONFIG_FILENAME = "files/config.json"
    CONFIG_KEYWORDS: dict = {"email_account", "email_pwd", "news_api_key",
                            "max_articles_per_topic", "max_topics_per_subscription",
                            "sort_order", "email_timeout_ms",
                            "subscriptions_excel_file", "logfile", "debug"}
    SORT_KEYWORDS = {"relevancy", "popularity", "publishedAt"}
    IDX_STATUS = 0
    IDX_ERR_MSG = 2
    IDX_SUBJECTS_FOUND = 3
    IDX_TOT_SENT = 4
    DEBUG = True
    LOGGER_NAME = "logger"

    # TODO: Would be nice to refactor to have a NewsFeedConfig class.  However,
    #  would have to work at not exposing password in memory

    def __init__(self):
        # Load in the config from the JSON format config file
        # Not putting this stuff here is a style violation (PEP? or just PyCharm?)
        self.sender_account_connection: smtplib.SMTP_SSL = smtplib.SMTP_SSL()
        self.sender_account: str = ""
        self.news_api_key: str = ""
        self.max_articles_per_topic: int = 0
        self.max_topics_per_subscription: int = 0
        self.email_timeout_sec: float = 0.0
        self.debug:bool = True
        self.sort_order: str = ""
        self.subscriptions_excel_file = ""
        self.config: dict = self.load_config_and_connect()
        self.logfile: str = ""
        self.logger: logging.Logger = None
        # for news searches.  free use of API only works for news 1 day old or older
        yesterday = date.today() - timedelta(days=1)
        self.date_str = yesterday.strftime("%Y-%m-%d")

    def load_config_and_connect(self) -> dict:
        """
        Read the config file for the app.   Contains email acct info,
        apinews.org API key, max topics per subscription and mas headlines
        retrieved per topic, and the order of preference for selecting
        each top article list to send.  Sets all of the app config members.
        :return: dictionary with the loaded config
        """
        try:
            file = open(NewsSender.CONFIG_FILENAME, "r")
            config_data = json.load(file)
        except Exception as ex:
            # since don't have config info (and log file name/path) yet
            # will just do a print()
            logging.critical(f"Config file issue: {ex}, will exit")
            exit(1)
        # Check the config keys for sanity
        config_keys_found = config_data.keys()
        config_keys_needed = NewsSender.CONFIG_KEYWORDS
        missing_keys = []
        extra_keys = []
        # doing this early so can use logging from now on
        if "logfile" in config_keys_found:
            self.logfile = config_data["logfile"]
            self.start_logging(self.logfile)
        self.logger.info(">>>>>> Starting up EmailNewsFeed app")
        for key in config_keys_found:
            if key not in config_keys_needed and key != "_comment_":
                extra_keys.append(key)
        for key in config_keys_needed:
            if key not in config_keys_found:
                missing_keys.append(key)
        if len(extra_keys) != 0:
            self.logger.warning(f"extra config parameters found and ignored: {extra_keys}")
        if len(missing_keys) != 0:
            self.logger.critical(f"Missing required config parameter(s), exiting. "
                          f"Missing keys: {missing_keys}")
            exit(1)
        self.sender_account = config_data["email_account"]
        sender_pwd = config_data["email_pwd"]
        self.news_api_key = config_data["news_api_key"]
        self.max_articles_per_topic = config_data["max_articles_per_topic"]
        self.max_topics_per_subscription = config_data["max_topics_per_subscription"]
        # TODO: use the timeout in the smtp API calls
        self.email_timeout_sec: float = config_data["email_timeout_ms"] / 1000.0
        self.debug = config_data["debug"].strip().upper() == "TRUE"
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        self.sort_order = config_data["sort_order"]
        self.subscriptions_excel_file = config_data["subscriptions_excel_file"]
        if self.sort_order not in NewsSender.SORT_KEYWORDS:
            self.logger.error(f"Error in config: sort_order not a valid value:"
                         f" {self.sort_order}, will assume 'relevancy'")
            self.sort_order = "relevancy"
        # have to put this here if I don't want pwd to be persistent in memory
        self.sender_account_connection = self.connect_sender(sender_pwd)
        return config_data

    def start_logging(self, logfilename: str):
        # check file appendable first
        try:
            f = open(logfilename, "a")
            f.close()
        except Exception as ex:
            # yup, will have to do this to stdout
            logging.critical(f"Could not open logfile {logfilename}, "
                             f"exception {ex}, will exit")
            exit(1)
        self.logger = logging.getLogger(NewsSender.LOGGER_NAME)
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename=logfilename, mode="a",
                                      maxBytes=500000, backupCount=4)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def connect_sender(self, pwd: str) -> smtplib.SMTP_SSL:
        """
        Connect sender to gmail SMTP server
        :param pwd: password for email account
        :return: smtp_ssl connection to gmail
        """
        # TODO look into refactoring to use OAUTH 2.0 - not now, that will
        #   take a fair amount of research
        # Ardit uses yagmail ("yet another gmail") library, instead of
        # using the smptlib to deal with it directory.
        # TODO: Look into which API yagmail uses - he didn't set up a google dev
        #  account and get an API key, probably smtplib.
        smtp_server: smtplib.SMTP_SSL = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        try:
            connect_resp = smtp_server.login(user=self.sender_account, password=pwd)
            self.logger.info(f"connected, value returned: {connect_resp}")
        except smtplib.SMTPException as smtpe:
            self.logger.critical(f"Exception trying to login to email:"
                                 f" {smtpe}, will exit")
        return smtp_server

    def send_html_email(self, subject: str, html_body:str, recipients: list[str]) -> (bool, str):
        """
        send an HTML-format email message using the established
        email connection
        :param subject: subject line
        :param html_body: the body of the email
        :param recipients: a list of recipients.  Even one recipient must
           still be in a list
        :return: list with bool sent successfully, ena status resp or error msg
        """
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_account
        msg['To'] = ", ".join(recipients)
        msg.set_content(html_body, subtype='html')
        # print(recipients)
        # print("msg: ", msg)
        # print("msg.as_string()", msg.as_string())
        try:
            send_resp = self.sender_account_connection.send_message(msg)
        except smtplib.SMTPException as smtpe:
            self.logger.error(f"Got exception sending email: {smtpe}")
            return False, smtpe
        # print(f"Message subject {subject} sent!")
        return True, "no error"

    def close_connection(self):
        self.sender_account_connection.quit()


if __name__ == '__main__':
    email_sender = NewsSender()
    msg_body_html = "<html><body><h1>Hi there!</h1><p>Hi how are <b>you</b>?</p></body></html>"
    print("Sending first email...", end="")
    status = email_sender.send_html_email("Test", msg_body_html, ["saelkind@gmail.com"])
    print(" ...email sent successfully: ", status[0])
    print("Trying to send email with bad-format to address...\n", end="")
    status = email_sender.send_html_email("Test #3 AOL", msg_body_html, ["selkind@@aol.com"])
    print(" ...email sent successfully: ", status[0], ", err msg: ", status[1])
    time.sleep(20)
    print("Sending second email (two recipients...", end="")
    status = email_sender.send_html_email("Test #2 BOTH", msg_body_html,
                                 ["saelkind@gmail.com", "selkind@aol.com"])
    print(" ...email sent successfully: ", status[0])
    time.sleep(20)
    print("Sending third email...", end="")
    status = email_sender.send_html_email("Test #3 AOL", msg_body_html, ["selkind@aol.com"])
    print(" ...email sent successfully: ", status[0])
