class BoardPostElements(object):
    title: str = ".//div/a"
    posts: str = "//div[@class='message-block-subject-date']"
    comments: str = ".//div[@class='comments']"
    creation_date: str = ".//span[contains(@class, 'post-date-board')]"
    last_post_date: str = ".//span[@class='post-date']"
    last_page: str = "//div[@class='page-info']"


class BoardMessageElements(object):
    posts: str = "//div[contains(@class, 'MessageView')]"
    messasge: str = ".//div[@class='lia-message-body-content']"
    message_num: str = ".//span[@class='MessagesPositionInThread']//a"


class EbayHTMLElements(object):
    board_posts: BoardPostElements = BoardPostElements()
    board_messages: BoardMessageElements = BoardMessageElements()
