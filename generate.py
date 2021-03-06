import sys
import time
from datetime import datetime, timedelta

import feedparser
import pytz
from feedgen.feed import FeedGenerator

ESPN_RSS_FEED = 'http://espn.go.com/espnradio/feeds/rss/podcast.xml?id=9941853'
CONTACT = {'name': 'Tim Schindler',
           'email': 'tim.schindler@gmail.com'}
FEED_TIMEZONE = 'America/Los_Angeles'


def episode_duration_string_to_int(duration):
    if len(duration.split(':')) == 3:
        ftr = [3600, 60, 1]
    else:
        ftr = [60, 1]
    return sum([a * b for a, b in zip(ftr, [int(i) for i in duration.split(":")])])

def modify_published_date(episode, entry):
    tz = pytz.timezone(FEED_TIMEZONE)

    dt = datetime.fromtimestamp(time.mktime(episode.published_parsed))
    date = tz.localize(dt)

    if 'Show: ' in episode.title:
        entry.published(date)
    elif 'Hour 1' in episode.title:
        entry.published(date + timedelta(hours=1))
    elif 'Hour 2' in episode.title:
        entry.published(date + timedelta(hours=2))
    elif 'Hour 3' in episode.title:
        entry.published(date + timedelta(hours=3))
    else:
        entry.published(date + timedelta(hours=-1))

def generate_feed(output_file, exclude_highlights=True):
    # Parse RSS feed
    d = feedparser.parse(ESPN_RSS_FEED)
    IMAGE_URL = d.feed.image['href']

    # RSS feed generation
    fg = FeedGenerator()
    fg.load_extension('podcast', rss=True)

    ## RSS tags
    # Required
    fg.title(d.feed.title)
    fg.link(href='https://github.com/aaearon/lebatard-show-rss')
    fg.description(d.feed.description)
    # Optional
    fg.language(d.feed.language)
    fg.image(IMAGE_URL)
    fg.subtitle(d.feed.subtitle)
    # iTunes
    fg.podcast.itunes_author(d.feed.author)
    fg.podcast.itunes_category(itunes_category=d.feed.category)
    fg.podcast.itunes_image(itunes_image=IMAGE_URL)
    fg.podcast.itunes_explicit(itunes_explicit='clean')
    fg.podcast.itunes_owner(name=CONTACT['name'], email=CONTACT['email'])

    for e in d.entries:

        if exclude_highlights and episode_duration_string_to_int(e['itunes_duration']) > 3600:
            pass
        else:
            fe = fg.add_entry()

            fe.id(e.id)
            fe.title(e.title)
            fe.description(e.description)
            fe.enclosure(url=e.enclosures[0]['href'],
                         length=e.enclosures[0]['length'],
                         type=e.enclosures[0]['type'])

            fe.podcast.itunes_summary(e.description)
            fe.podcast.itunes_subtitle(e.description)
            fe.podcast.itunes_duration(e['itunes_duration'])

            modify_published_date(e, fe)

    fg.rss_str(pretty=True)
    fg.rss_file(output_file)


if __name__ == '__main__':
    output_file = sys.argv[1]

    generate_feed(output_file)
