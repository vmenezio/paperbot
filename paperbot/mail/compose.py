import os
import json
import regex
import arrow
import random
import mistune
import cssutils
from collections import namedtuple

DATA = os.path.dirname(__file__)+"/data/"

def create_newsletter(urls, base_md=DATA+"base.md", subs_json=DATA+"subs.json",
        links_json=DATA+"links.json", style_css=DATA+"style.css"):
    """Return a newsletter object.

    Build a newsletter from a list of URLs, a base file (markdown) and a
    substituitions file, creating a somewhat unique message each time;
    then return it as a namedtuple Newsletter(html_text, plain_text).
    """
    substitutions = get_substitutions(subs_json)
    date = arrow.now().format("DD/MM/YYYY")
    date_weekday = arrow.now().format("dddd, DD/MM/YYYY")

    user_links, paperbot_links = parse_links(links_json)

    with open(base_md) as base_file:
        markdown = base_file.read().format(**substitutions, date=date_weekday,
            user_links=user_links, paperbot_links=paperbot_links)

    html_text = style_html(mistune.markdown(markdown), style_css)
    encoded_html_text = html_text.encode("latin-1", "xmlcharrefreplace")
    plain_text = html_to_text(html_text)

    Newsletter = namedtuple("Newsletter", ["html_text","plain_text","date"])
    return Newsletter(encoded_html_text, plain_text, date)

def html_to_text(html_text):
    """Strip html_text tags from string and return a plain plain_text version."""
    strip_tags = regex.compile(r"<.*?>")
    eol_tags = regex.compile(r"</p>")
    return strip_tags.sub("", eol_tags.sub("\n", html_text))

def style_html(html_text, style_css):
    """Applies inline styles to an html_text string from an externa file."""
    styled_html = html_text

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
    """Randomly pull phrase variations from the substitutions file."""
    with open(subs_json) as subs_file:
        raw_subs = json.loads(subs_file.read())
    return { k : random.choice(raw_subs[k]) for k in raw_subs }

def parse_links(links_json): # TODO: paperbot's suggestions
    """Return a html_text string with lists made up from the links file."""
    with open(links_json) as links_file:
        raw_links = json.loads(links_file.read())
    user_links = raw_links["user_links"]
    paperbot_links = raw_links["paperbot_links"]
    return get_md_links(user_links), "paperbot's suggestions coming soon"

def get_md_links(link_list):
    """Return an unordered list of links in markdown syntax."""
    html_links = "\n"
    for link in link_list:
        html_links += "* [{title}]({url})\n".format(**link)
    return html_links
