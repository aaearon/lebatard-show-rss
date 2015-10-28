from datetime import datetime, timedelta
import time

from feedgen.feed import FeedGenerator
import feedparser
import pytz
import sys

ESPN_RSS_FEED = 'http://espn.go.com/espnradio/feeds/rss/podcast.xml?id=9941853'
CONTACT = {'name': 'Tim Schindler',
           'email': 'tim.schindler@gmail.com'}


def generate_feed(output_file):
    # Parse RSS feed
    d = feedparser.parse(ESPN_RSS_FEED)
    IMAGE_URL = d.feed.image['href']

    # RSS feed generation
    fg = FeedGenerator()
    fg.load_extension('podcast', rss=True)

    ## RSS tags
    # Required
    fg.title(d.feed.title)
    fg.link(href='http://sports.espn.go.com/espnradio/podcast/index')
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

    tz = pytz.timezone('Europe/Amsterdam')

    for e in d.entries:
        fe = fg.add_entry()

        fe.id(e.id)
        fe.title(e.title)
        fe.description(e.description)
        fe.enclosure(url=e.enclosures[0]['href'],
                     length=e.enclosures[0]['length'],
                     type=e.enclosures[0]['type'])

        fe.podcast.itunes_summary(e.description)
        fe.podcast.itunes_subtitle(e.description)

        dt = datetime.fromtimestamp(time.mktime(e.published_parsed))
        date = tz.localize(dt)

        if 'Local Hour' in e.title:
            fe.published(date)
        elif 'Hour 1' in e.title:
            fe.published(date + timedelta(hours=1))
        elif 'Hour 2' in e.title:
            fe.published(date + timedelta(hours=2))
        elif 'Hour 3' in e.title:
            fe.published(date + timedelta(hours=3))
        else:
            fe.published(date + timedelta(hours=-1))

    fg.rss_str(pretty=True)
    fg.rss_file(output_file)


if __name__ == '__main__':
    output_file = sys.argv[1]

    generate_feed(output_file)
