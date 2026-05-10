import re


def normalize_title(title: str):

    title = re.sub(r'【.*?】', '', title)

    title = re.sub(r'第\d+話', '', title)

    title = re.sub(r'#\d+', '', title)

    title = re.sub(r'\s+', ' ', title)

    return title.strip()