from news_sender import NewsSender
from subscription import Subscription
import pandas as pd
import numpy as np
# import openpyxl
# import xlrd


class Subscriptions:
    '''The list of subscriptions to process at each cycle.
    Each item in the list is a subscription: subscriber name, email, and list
    of news topics of interest.

    Format of subscriptions Excel file:
        - only the first worksheet will be used, others are ignored
        - First row, names for the columns (row required, values up to user, but
          should probably stick to letters, numbers, _, -, ?, /
        - data row columns (4):
            First name
            Last name
            email address
            comma-separated list of topics
    Name and location of the Excel spreadsheet file are a configuration parameter
    in config.json
    '''

    IDX_FIRSTNAME = 0
    IDX_LASTNAME = 1
    IDx_EMAIL = 2
    IDX_TOPIC_LIST = 3

    # TODO: check topic list for illegal chars, HTML, etc.?  Although, in
    #  theory this would have been done in the web form where the user was
    #  managing their topic list

    def __init__(self):
        # array of subscription arrays
        self.newssender = NewsSender()
        pd.set_option('display.max_columns', None)
        pd.set_option('max_colwidth', None)
        pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_seq_items', None)
        pd.set_option('display.width', None)
        self.subscriptions_array = None
        self.data_columns_names: list[str] = None
        self.load_subscriptions()

    def load_subscriptions(self):
        ''' Load the subscriptions from the configured Excel file into
        a member array for processing
        '''
        subscriptions_df = pd.read_excel(self.newssender.subscriptions_excel_file)
        # TODO debug test & print() - replace with logger.debug
        self.data_columns_names = list(subscriptions_df.columns)
        self.subscriptions_array = np.array(subscriptions_df)
        if self.newssender.debug:
            print("DataFrame:\n", subscriptions_df)
            print("\nArray:\n", self.subscriptions_array)
            print("\n\nColumn names:\n", self.data_columns_names)
        # TODO: workaround to iteration antipattern with Pandas DataFrames. Need
        #  to refactor this if subscriber list gets "large".
        # use transform to numpy array
        for subscription_row in self.subscriptions_array:
            topics_list = subscription_row[Subscriptions.IDX_TOPIC_LIST].split(",")
            print(topics_list)
            for i in range(0, len(topics_list) - 1):
                topics_list[i] = topics_list[i].strip()
                topics_list[i].replace(" ", "+")
            subscription_row[Subscriptions.IDX_TOPIC_LIST] = topics_list

    def process_subscriptions(self) -> dict:
        """
        process all subscriptions one at a time
        :return: list of:
        <ul>
        <li>total subscriptions</li>
        <li>subscriptions successfully processed</li>
        <li>total topics processed
        <li>total articles retrieved</li>
        """
        total_subscriptions = len(self.subscriptions_array)
        subscriptions_processed_ok = 0
        topics_requested = 0
        topic_processed = 0
        articles_retrieved = 0
        for subscription_rec in self.subscriptions_array:
            stats = Subscription.process_subscription(subscription_rec, self.newssender)
            subscriptions_processed_ok += 1 if stats["email_sent"] else 0
            # subscriptions_processed_ok += stats["error_msg"]
            topics_requested += stats["topics_requested"]
            topic_processed += stats["topics_retrieved"]
            articles_retrieved += stats["articles_retrieved"]
        total_stats = {
            "subscriptions_processed_ok": subscriptions_processed_ok,
            "topics_requested": topics_requested,
            "topic_processed": topic_processed,
            "articles_retrieved": articles_retrieved
        }
        # TODO: replace print() with logger.info()
        print("Final stats over all subscriptions: \n", total_stats)


if __name__ == "__main__":
    subs = Subscriptions()
    # print("DataFrame:\n", subs.subscriptions_df)
    subs.process_subscriptions()
