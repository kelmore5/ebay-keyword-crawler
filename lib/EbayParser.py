import ast
import os.path
import sys
from typing import List, Set, Union

# noinspection PyUnresolvedReferences
from EbayHTMLElements import EbayHTMLElements
# noinspection PyUnresolvedReferences
from SeleniumBrowser.lib.SeleniumBrowser import SeleniumBrowser
# noinspection PyUnresolvedReferences
from SeleniumBrowser.lib.XPathLookupProps import XPathLookupProps
# noinspection PyUnresolvedReferences
from database.models.Keywords import Keywords, KeywordsKeys
# noinspection PyUnresolvedReferences
from database.models.Messages import Messages, MessagesKeys
# noinspection PyUnresolvedReferences
from database.models.Posts import Posts, PostsKeys
from peewee import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
# noinspection PyUnresolvedReferences,PyPep8Naming
from utilities.lib.Arrays import Arrays as arrays
# noinspection PyUnresolvedReferences,PyPep8Naming
from utilities.lib.Excel import Excel as sheets
# noinspection PyUnresolvedReferences,PyPep8Naming
from utilities.lib.Jsons import Jsons as jsons

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '..'))

sys.path.append(dir_path)

# from lib.database.models.Posts import Posts, PostsKeys
# from lib.database.models.Messages import Messages
# from lib.database.models.Keywords import Keywords
# from lib.utilities.Excel import Excel as sheets

# TODO: Move to db
# Set keywords to search for her
keywords = [
    ["good deal", "great deal", "fair deal", "best deal", "good price", "great price", "fair price", "best price",
     "good customer", "great customer", "repeat customer", "fair", "honest", "reasonable"],
    ["scam", "scams", "scammed", "scamming", "scammer", "scammers", "fraud", "frauds", "defrauded", "fraudster",
     "fraudsters", "con", "cons", "conned", "conning", "con artist", "con artists", "trick", "tricks", "tricked",
     "tricking", "trickster", "tricksters", "swindle", "swindles", "swindled", "swindler", "swindlers"]
]

# TODO: Move to db
# Set board names and links to be downloaded here
board_names = ['Bidding and Buying', 'Selling']

board_urls = ["http://community.ebay.com/t5/Bidding-Buying/bd-p/bidding-buying-db",
              "http://community.ebay.com/t5/Selling/bd-p/selling-db"]


class ParsedBoard(object):
    posts: List[Posts]
    max_page: int

    def __init__(self, posts: List[Posts], max_page: int):
        self.posts = posts
        self.max_page = max_page


class PostLink(object):
    link: str
    page_num: int

    def __init__(self, link: str, page_num: int):
        self.link = link
        self.page_num = page_num


class EbayParser(object):
    db: SqliteDatabase
    browser: SeleniumBrowser
    search_elements: EbayHTMLElements

    # TODO: Check for chromedriver existence, exit if not
    def __init__(self, path_to_chromedriver: str = dir_path + "/lib/chromedriver"):
        self.browser = SeleniumBrowser(path_to_chromedriver)
        self.db = Posts.db
        self.db.connect()

        self.search_elements = EbayHTMLElements()
        self.db.create_tables([Posts, Messages, Keywords])

    def parse_ebay(self):
        print('\n\nScript starting. Ebay forums \'Bidding and Buying\' and \'Selling\' will be downloaded and '
              'parsed to search for keywords within postings\n\n')

        print('Starting download of ebay forum links. Once downloaded, will use links to get all messages within '
              'forum listing\n')
        self.download_ebay_posts()

        print(
            'Finished parsing and saving all links for boards. Moving on to downloading messages for keyword search\n')
        # Go to all remaining new forum links and extract keywords
        self.download_ebay_messages()

        print('\nFinished downloading all messages from all boards. Moving on to parsing keywords\n')
        self.parse_keywords_from_messages()

        print('Done\n\nOutputting keywords to Excel\n')
        EbayParser.output_keywords_to_excel()
        print('\nDone\n\nScript finished')

        self.browser.quit()

    def download_ebay_posts(self):
        # TODO: Method for input for boards - save to db?
        # Loop through specified boards (pre-defined by user)
        for board_num in range(len(board_urls)):
            ebay_board_name: str = board_names[board_num]
            ebay_bid_forum_url: str = board_urls[board_num]

            # Start at page 0, set preliminary last page as 2nd page
            current_page: int = 0
            last_page: int = 2  # Could use math.inf for preliminary, but may end up in infinite loop, so choosing 2

            no_updates_count = 0

            # Loop through all pages
            # print("\nGetting all keywords from board " + ebay_bid_forum_url)
            print('Grabbing all links for listing ' + ebay_board_name + '\n')
            while current_page < last_page:
                print("Currently working page {} of {}...".format(str(current_page + 1), str(last_page)), end="")

                # Create forum url (from ebay) and an XPath check once the page is loaded (to confirm loading)
                new_url: str = '{}/page/{}'.format(ebay_bid_forum_url, str(current_page + 1))
                load_check: XPathLookupProps = XPathLookupProps(By.XPATH, self.search_elements.board_posts.posts,
                                                                done_message=None)

                # If url did not load, continue on to next page
                if not self.browser.browse_to_url(new_url, load_check):
                    # TODO: Error db
                    print('\nThere was an error loading page {}, skipping for now...'.format(str(current_page + 1)))
                    current_page += 1
                    continue

                # Parse all the links from the forum page into
                print('Loaded\nParsing and uploading to the database...', end='')
                board_links = self.get_ebay_forum_links_from_main_board_tree(self.browser.get_browser())

                # Set last page if not set
                if last_page == 2:
                    last_page = board_links.max_page

                # Check for changes within info (for skipping boards)
                filtered_posts = EbayParser.check_for_updates(board_links.posts)

                if len(filtered_posts) == 0:
                    print("All forum links already in database. Continuing\n")
                    no_updates_count += 1

                    if no_updates_count == 5:
                        print(
                            "Found 5 boards in a row with all items already in database...Moving on to next board.\n")
                        break
                    continue

                # Upload all the parsed links into a database
                # Data changes often, but doing this just for safe-keeping
                # in case internet disconnects or some other problem
                # noinspection PyCallByClass
                Posts().upload_many(board_links.posts)
                print('Done, uploaded\nMoving on to next page\n')

                break

    def download_ebay_messages(self):
        offset: int = 0
        step: int = 5

        posts_to_download: List[Posts] = Posts.select(Posts.title, Posts.link, Posts.total_pages).limit(step).offset(
            offset)
        messages_load_check: XPathLookupProps = XPathLookupProps(By.XPATH, self.search_elements.board_messages.posts,
                                                                 done_message=None)

        num_posts: int = Posts.select(fn.COUNT('*').alias('count'))[0].count
        while len(posts_to_download) > 0:
            print('Downloading messages from {} to {} pages of {} total...'.format(offset, offset + step, num_posts),
                  end='')
            message_uploads: List[Messages] = []

            for post in posts_to_download:
                for page_num in range(post.total_pages):
                    if not self.browser.browse_to_url('{}/page/{}/'.format(post.link, str(page_num + 1)),
                                                      messages_load_check):
                        # TODO: Remove urls that no longer exist...
                        print('')
                        continue

                    new_messages = self.parse_post_messages(self.browser.get_browser())

                    for message in new_messages:
                        message.title = post.title
                        message.link = post.link
                        message.page_num = page_num + 1

                        message_uploads.append(message)

            print('Done\nUploading to database...', end='')
            # noinspection PyCallByClass
            Messages().upload_many(message_uploads)
            print('Uploaded\nMoving on to next {} pages\n'.format(step))
            self.browser.restart_browser()

            offset += step
            posts_to_download = Posts.select(Posts.title, Posts.link, Posts.total_pages).limit(step).offset(offset)
            message_uploads.clear()

    @staticmethod
    def parse_keywords_from_messages():
        offset = 0
        step = 5

        positives = keywords[0]
        negatives = keywords[1]

        num_messages: int = Messages.select(fn.COUNT('*').alias('count'))[0].count
        messages_to_parse: List[Messages] = Messages.select(Messages.title, Messages.link,
                                                            fn.GROUP_CONCAT(Messages.message).alias("message")) \
            .group_by(Messages.title, Messages.link).offset(offset).limit(step)

        keyword_uploads: List[Keywords] = []
        print('Parsing keywords for {} messages'.format(num_messages))
        while len(messages_to_parse) > 0:
            for message_datum in messages_to_parse:
                positive_keyword = Keywords()
                negative_keyword = Keywords()

                positive_keyword.group = 'Positive'
                negative_keyword.group = 'Negative'

                message = message_datum.message

                positive_keywords = [x for x in positives if x in message]
                negative_keywords = [x for x in negatives if x in message]

                positive_keyword.title = message_datum.title.title
                negative_keyword.title = message_datum.title.title

                positive_keyword.link = message_datum.link.link
                negative_keyword.link = message_datum.link.link

                positive_keyword.keywords_in_title = str([x for x in positives if x in message_datum.title.title])
                negative_keyword.keywords_in_title = str([x for x in negatives if x in message_datum.title.title])

                positive_keyword.keywords_in_message = str(positive_keywords)
                negative_keyword.keywords_in_message = str(negative_keywords)

                if len(positive_keywords) > 0:
                    keyword_uploads.append(positive_keyword)

                if len(negative_keywords) > 0:
                    keyword_uploads.append(negative_keyword)

            offset += step
            messages_to_parse = Messages.select(Messages.title, Messages.link,
                                                fn.GROUP_CONCAT(Messages.message).alias("message")) \
                .group_by(Messages.title, Messages.link).offset(offset).limit(step)

            if len(keyword_uploads) > 20 or len(messages_to_parse) == 0:
                Keywords().upload_many(keyword_uploads)
                keyword_uploads.clear()

        return True

    @staticmethod
    def output_keywords_to_excel():
        global keywords

        # TODO: Format excel spreadsheet output
        sheet_rows = []
        headers = ["Title", "Page Link", "Keyword Group", "Keywords Found in Title", "Keywords Found in Messages",
                   "Post Creation Date", "Post Last Response Date"]

        output: List[Union[Keywords, Posts]] = Keywords.select(Keywords.title, Keywords.link, Keywords.group,
                                                               Keywords.keywords_in_title, Keywords.keywords_in_message,
                                                               Posts.creation_date.alias("creation_date"),
                                                               Posts.last_post_date) \
            .join(Posts, JOIN.LEFT_OUTER, on=(Posts.link == Keywords.link)).order_by(Keywords.group.desc())

        positives = keywords[0]
        negatives = keywords[1]

        db_keywords: List[str] = []
        for keyword in output:
            title_keys = ast.literal_eval(keyword.keywords_in_title)
            message_keys = ast.literal_eval(keyword.keywords_in_message)
            db_keywords += title_keys + message_keys

        unique_keywords = set(db_keywords)
        keyword_rows = [[], []]
        for key in unique_keywords:
            if key in positives:
                keyword_rows[0].append([key, str(db_keywords.count(key))] + [""] * 5)
            if key in negatives:
                keyword_rows[1].append([key, str(db_keywords.count(key))] + [""] * 5)

        compare_keys = lambda x: int(x[1]) * -1

        keyword_rows[0].sort(key=compare_keys)
        keyword_rows[1].sort(key=compare_keys)

        rem_brackets = lambda x: x.replace('[', '').replace(']', '').replace('\'', '')

        sheet_rows.append(headers)
        sheet_rows.append([""] * 7)
        for keyword in output:
            # noinspection PyUnresolvedReferences
            new_row = [keyword.title.title, keyword.link.link, keyword.group, rem_brackets(keyword.keywords_in_title),
                       rem_brackets(keyword.keywords_in_message), keyword.posts.creation_date,
                       keyword.posts.last_post_date]
            sheet_rows.append(new_row)

        sheet_rows += [[]] + [["Total Keywords"]] + [[]]
        sheet_rows += [["Positive Keywords:"]] + [[]] + keyword_rows[0] + [[]]
        sheet_rows += [["Negative Keywords:"]] + [[]] + keyword_rows[1]

        output_path = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.abspath(os.path.join(output_path, '../output/output.xlsx'))

        sheets.create_master_sheet(output_path, sheet_rows)

    @staticmethod
    def check_for_updates(posts_to_check: List[Posts]) -> List[Posts]:
        # Links is the UID in posts, so
        # Grab all links about to be uploaded
        # Then, grab all items from database with same link
        # Filter out all links past page 1 since don't need when checking
        links: List[Posts] = [x.link for x in posts_to_check if x.total_pages == 1]
        saved_posts: List[Posts] = Posts.select().where(Posts.link.in_(links))

        # Create a link lookup dictionary (from db) to check current links with db-saved total comments
        link_lookup = dict()
        for saved_post in saved_posts:
            link_lookup[saved_post.link] = saved_post.total_comments

        # Loop through posts to be checked, find any with the same number of total comments,
        # and then remove from array - don't need to download forum if link exists and total
        # comments are the same
        to_remove: Set[str] = set()
        for idx in range(len(posts_to_check)):
            checking_post: Posts = posts_to_check[idx]

            # Check if link in db
            if checking_post.link in link_lookup:
                # Get total comments from db
                comments_check = link_lookup[checking_post.link]

                # Check if db # of comments = checking # of comments
                # If so, remove
                if checking_post.total_comments == comments_check:
                    to_remove.add(checking_post.title)

        reduced_posts = [x for x in posts_to_check if x.title not in to_remove]
        return reduced_posts

    @staticmethod
    def search_for_element(html_tree: WebElement, search_tag: str) -> Union[WebElement, object]:
        try:
            return html_tree.find_element_by_xpath(search_tag)
        except NoSuchElementException:
            return type("FakeWebElement", (object,), {"text": None})

    @staticmethod
    def get_all_links_within_post(post_link: str, comment_num: int) -> List[PostLink]:
        post_links: List[PostLink] = []
        page_num = 1
        if comment_num < 1000:
            while comment_num / 21 > 0:
                new_link = post_link.replace("/jump-to/first-unread-message", "") + "/page/" + str(page_num)
                post_links.append(PostLink(new_link, page_num))
                comment_num -= 20
                page_num += 1

        return post_links

    def get_ebay_forum_links_from_main_board_tree(self, html_tree: webdriver.Chrome) -> ParsedBoard:
        elements = self.search_elements.board_posts

        max_page = html_tree.find_elements_by_xpath(elements.last_page)[0].text
        max_page = max_page[max_page.index("of") + 3:]

        board_posts: List[WebElement] = html_tree.find_elements_by_xpath(elements.posts)
        formatted_boards: List[Posts] = []

        # Get four HTML elements from ebay:
        # board_post = A posting on ebay's forum
        # comments = The number of comments on the post and a link to the comments section
        # dates = Last post time
        # dates2 = When post was created
        for board in board_posts:
            title_html: WebElement = EbayParser.search_for_element(board, elements.title)
            title = title_html.text
            link = title_html.get_attribute('href').replace("/jump-to/first-unread-message", "")

            num_comments: int = int(EbayParser.search_for_element(board, elements.comments).text)
            post_creation_date: str = EbayParser.search_for_element(board, elements.creation_date).text
            last_post_date: str = EbayParser.search_for_element(board, elements.last_post_date).text

            if last_post_date == "" or last_post_date is None:
                last_post_date = post_creation_date

            total_pages: int = (num_comments / 20) + 1

            post_values = [title, link, total_pages, num_comments, post_creation_date, last_post_date]
            post_props = jsons.create_dict(PostsKeys.keys, post_values)
            post = Posts.initialize(post_props)

            formatted_boards.append(post)

        return ParsedBoard(formatted_boards, int(max_page))

    def parse_post_messages(self, html_tree: webdriver.Chrome) -> List[Messages]:
        elements = self.search_elements.board_messages
        messages: List[Messages] = []

        posts = html_tree.find_elements_by_xpath(elements.posts)
        for post in posts:
            new_message = Messages()

            # TODO: Remove block quotes
            message = post.find_element_by_xpath(elements.messasge)
            message_num = post.find_element_by_xpath(elements.message_num)

            new_message.message = message.text
            new_message.message_num = message_num.text

            messages.append(new_message)
        return messages


# TODO: Catch KeyboardInterrupt and close browser - super big memory leaks if opened/exited a lot
parser = EbayParser()
parser.parse_ebay()
