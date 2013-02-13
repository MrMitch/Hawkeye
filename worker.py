#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sqlite3
from datetime import datetime
from urllib2 import urlopen
import rdcli.RDWorker as RDWorker
import twitter


BASE = path.join(path.abspath(path.expanduser(u'~')), '.config', 'hawkeye')
BASE = path.join(path.abspath(path.expanduser('./')))
CONF = path.join(BASE, 'hawkeye_oauth.conf')
SQLITE = path.join(BASE, 'hawkeye.db')

RDCLI_CONF = path.join(BASE, 'rdcli.conf')
RDCLI_COOKIE = path.join(BASE, 'rdcli.cookie')

APP_NAME = 'Hawkeye Server'
CONSUMER_KEY = 'OzICYfiYXDZlo41cMBr1yQ'
CONSUMER_SECRET = '7mN5kptD3Qc14Jb5KWJnTMcICG6FXf5cAAJdX7MA'

OUTPUT_DIR = path.abspath(path.join(path.expanduser('~'), 'Videos'))


def get_oauth_info():

    print BASE
    try:
        with open(CONF) as conf:
            lines = conf.readlines()

        return {
            'consumer_key': lines[0].strip(),
            'consumer_secret': lines[1].strip(),
            'access_token': lines[2].strip(),
            'access_token_secret': lines[3].strip(),
            'account_name': lines[4].strip()
        }
    except Exception as e:
        raise IOError('Unable to read conf file: %s' % str(e))


def initialize_db():
    with sqlite3.connect(SQLITE, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE refs(tweet_id INT, creation_date timestamp, processing_date timestamp)')
        cursor.execute('CREATE TABLE failed(sender text, url text, processing_date timestamp)')


def main():
    # retrieve OAuth tokens
    try:
        oauth_token, oauth_token_secret = twitter.read_token_file(CONF)
    except BaseException:
        try:
            oauth_token, oauth_token_secret = twitter.oauth_dance(APP_NAME, CONSUMER_KEY, CONSUMER_SECRET, CONF)
        except Exception:
            exit('Unable to get OAuth tokens')

    # twitter API client
    client = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))

    # open sqlite3 connection
    with sqlite3.connect(SQLITE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as connection:
        cursor = connection.cursor()
        last_processed_dm = 0

        # get the ID of the last processed DM
        try:
            cursor.execute("""SELECT ID as "id [integer]" FROM refs
            WHERE processing_date = (SELECT MAX(processing_date) FROM refs)""")
            last_processed_dm = cursor.fetchone()
        except sqlite3.OperationalError:
            initialize_db()

        count = 0
        links = []
        for dm in client.direct_messages():
            if count == 0:
                count += 1
                cursor.execute("""INSERT INTO refs VALUES(?, ?, ?)""",
                               (dm['id'], datetime.strptime(dm['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), datetime.now()))

            if dm['id'] == last_processed_dm:
                break

            if len(dm['entities']['hashtags']) and len(dm['entities']['urls']):
                for url in dm['entities']['urls']:
                    links.append((dm['sender_screen_name'], url['expanded_url']))

        rd_worker = RDWorker.RDWorker(RDCLI_COOKIE, RDCLI_CONF)

        for link in links.reverse():
            try:
                target = rd_worker.unrestrict(link)
                filename = rd_worker.get_filename_from_url(target)
                fullpath = path.join(OUTPUT_DIR, filename)

                stream = urlopen(target )

                with open(fullpath, 'wb') as output:
                    while True:
                        content = stream.read(10240)  # 10 KB
                        if not buffer:
                            break
                        else:
                            output.write(content)
                    stream.close()
            except Exception as e:
                error = str(e)

    exit(0)


if __name__ == '__main__':
    main()

# check if output dir exists