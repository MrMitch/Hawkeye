#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
from os import path
import sqlite3
from datetime import datetime
from urllib2 import urlopen
from rdcli import RDWorker, UnrestrictionError
import twitter

from config import CONF, CONSUMER_KEY, CONSUMER_SECRET, RDCLI_COOKIE, SQLITE, write_configuration_file, initialize_db

OUTPUT_DIR = path.abspath('.')


def main():
    parser = SafeConfigParser()
    parser.read(CONF)

    if not parser.has_section('rdcli') or not parser.has_section('hawkeye'):
        write_configuration_file()
        parser.read(CONF)

    # retrieve OAuth token
    oauth_token = parser.get('hawkeye', 'oauth_token')
    oauth_token_secret = parser.get('hawkeye', 'oauth_token_secret')
    rd_user = parser.get('rdcli', 'username')
    rd_password = parser.get('rdcli', 'password')

    rd_worker = RDWorker(RDCLI_COOKIE, CONF)

    try:
        rd_worker.login({'user': rd_user, 'pass': rd_password})
    except Exception as e:
        exit('Unable to log into Real-Debrid: %s' % str(e))

    # twitter API client
    client = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))

    # open sqlite3 connection
    with sqlite3.connect(SQLITE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as connection:
        cursor = connection.cursor()
        last_processed_dm = 0

        # get the ID of the previously last processed DM
        try:
            cursor.execute("SELECT tweet_id FROM refs WHERE processing_date = (SELECT MAX(processing_date) FROM refs)")
            last_processed_dm = cursor.fetchone()
        except sqlite3.OperationalError:
            initialize_db()

        if type(last_processed_dm) == tuple:
            last_processed_dm = last_processed_dm[0]

        def download(link, cur=cursor, conn=connection):
            """
            Utility function to download a file
            """
            try:
                target = rd_worker.unrestrict(link[1])
                filename = rd_worker.get_filename_from_url(target)
                fullpath = path.join(OUTPUT_DIR, filename)

                stream = urlopen(target)

                with open(fullpath, 'wb') as output:
                    while True:
                        content = stream.read(10240)  # 10 KB
                        if not content:
                            break
                        else:
                            output.write(content)
                    stream.close()

                msg = '%s downloaded @ %s' % (filename, datetime.now().strftime('%d/%m/%y %H:%M:%S'))
            except UnrestrictionError as e:
                if e.code in UnrestrictionError.fixable_errors():
                    cur.execute('INSERT INTO failed VALUES(?, ?, ?)', (link[0], link[1], datetime.now()))
                    conn.commit()
                    msg = 'Will retry %s later (%s)' % (link[1], e.message)
                else:
                    msg = '%s error %i: %s ' % (link[1], e.code, e.message)
                    cur.execute('DELETE FROM failed WHERE sender = ? AND url = ?', (link[0], link[1]))
                    conn.commit()
            except Exception as e:
                try:
                    name = filename
                except UnboundLocalError:
                    name = link[1]
                msg = '%s error: %s ' % (name, str(e))

            return msg

        # try to download the previously failed downloads
        for row in cursor.execute('SELECT sender, url FROM failed ORDER BY processing_date ASC'):
            msg = download(row[1])
            client.direct_messages.new(user=row[0], text=msg)

        count = 0
        links = []

        # go through all the DMs
        for dm in client.direct_messages():

            # save a reference to the last processed DMs
            if count == 0:
                count += 1
                values = (dm['id'], datetime.strptime(dm['created_at'], '%a %b %d %H:%M:%S +0000 %Y'), datetime.now())
                cursor.execute("INSERT OR REPLACE INTO refs VALUES(?, ?, ?)", values)
                connection.commit()

            if dm['id'] == last_processed_dm:
                break

            if len(dm['entities']['urls']):
                for url in dm['entities']['urls']:
                    links.append((dm['sender_screen_name'], url['expanded_url']))

        # sort chronologically
        links.reverse()

        for link in links:
            msg = download(link)
            client.direct_messages.new(user=link[0], text=msg)

    exit(0)


if __name__ == '__main__':
    main()

# check if output dir exists
# whitelist users
# test index conflict in SQLITE