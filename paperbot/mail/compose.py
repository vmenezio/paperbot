import os
import json
import regex
import arrow
import random
import mistune
import cssutils
from collections import namedtuple

DIR = os.path.dirname(__file__)+"/"

def create_newsletter(urls, base_md=DIR+"base.md", subs_json=DIR+"subs.json",
        links_json=DIR+"links.json", style_css=DIR+"style.css"):
    """Return a newsletter object.

    The newsletter is built from a list of URLs, a base file (markdown)
    and a substituitions file, creating a somewhat unique message each
    time. It is then returned as a namedtuple Newsletter(html, text).
    """
    substitutions = get_substitutions(subs_json)
    date = arrow.now().format("DD/MM/YYYY")
    date_weekday = arrow.now().format("dddd, DD/MM/YYYY")

    user_links, paperbot_links = parse_links(links_json)

    with open(base_md) as base_file:
        markdown = base_file.read().format(**substitutions, date=date_weekday,
            user_links=user_links, paperbot_links=paperbot_links)

    html = style(mistune.markdown(markdown), style_css)
    text = html_to_text(html)

    return namedtuple("Newsletter", ["html","text","date"])(html, text, date)

def html_to_text(html):
    """Strip html elements from string and return a plaintext version."""
    strip_tags = regex.compile(r"<.*?>")
    eol_tags = regex.compile(r"</p>")
    return strip_tags.sub("", eol_tags.sub("\n", html))

def style(html, style_css):
    """Applies css styles from an external file to an html string inline."""
    styled_html = html

    with open(style_css) as css_file:
        css = cssutils.parseString(css_file.read())

    styles = {}

    for rule in css:
        for selector in rule.selectorText.split(", "):
            for prop in rule.style:
                try:
                    styles[selector].append(prop)
                except KeyError:
                    styles[selector] = [prop]

    for selector, prop_list in styles.items():
        inline = " style=\""
        for prop in prop_list:
            inline += "{}:{};".format(prop.name, prop.value)
        inline += "\""
        styled_html = regex.sub("<"+selector, "<"+selector+inline, styled_html)

    return styled_html

def get_substitutions(subs_json):
    """Randomly pull word/phrase variations from the substitutions file."""
    with open(subs_json) as subs_file:
        raw_subs = json.loads(subs_file.read())
    return { k : random.choice(raw_subs[k]) for k in raw_subs }

def parse_links(links_json): # TODO: paperbot's suggestions
    """Return a html string with lists made up from the links file."""
    with open(links_json) as links_file:
        raw_links = json.loads(links_file.read())
    user_links = raw_links["user_links"]
    paperbot_links = raw_links["paperbot_links"]
    return get_html_links(user_links), "paperbot's suggestions coming soon"

def get_html_links(link_list):
    html_links = "\n"
    for link in link_list:
        html_links += "* [{title}]({url})\n".format(**link)
    return html_links

