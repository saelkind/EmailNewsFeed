import json


class NewsSender:
    '''
    The NewsSender maintains a connection to the News Feed's email account for
    sending emails to subscibers, and sends the emails.

    All account information is read from the config file, and in addition all the
    external config options for the app.  Done here, since I do not want to
    retain the email account password persistently in memory and only want to
    read the file one time.
    '''

    EMAIL_ACCT_FILENAME = "files/config.json"
    CONFIG_KEYWORDS: dict = {"email_account", "email_pwd", "news_api_key",
                            "max_articles_per_topic", "max_topics_per_subscription",
                            "sort_order", "email_timeout_ms", "debug"}
    SORT_KEYWORDS = {"relevancy", "popularity", "publishedAt"}
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
        # Load in the config from the JSON format config file
        config_data: dict = {}
        try:
            file = open(NewsSender.EMAIL_ACCT_FILENAME, "r")
            config_data = json.load(file)
        except Exception as e:
            print("Error opening config file, will exit:", e)
            exit(1)
        # Check the config keys for sanity
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
        self.sort_order = config_data["sort_order"]
        if self.sort_order not in NewsSender.SORT_KEYWORDS:
            print(f"Error in config: sort_order not a valid value: {self.sort_order}"
                  f", exiting")
            exit(1)

    def open_email_account_connection(self, password) -> (bool, str):
        '''Open the connection to the email account.  If the connection fails,
        return False and the relevant error message to the caller.  Do  not store
        the password in anything but a local var.  Also, not committing my real config.json
        file to the repository, only an example one'''
        pass



    def send_email(self, email) -> (bool, str):
        timeout = self.email_timeout_ms
        pass
