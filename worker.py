#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import load
from os import path
import sqlite3
from datetime import datetime
from urllib2 import urlopen

import modules.twitter_api as twitter

from modules.rdcli import RDWorker, UnrestrictionError
from config import CONF, CONSUMER_KEY, CONSUMER_SECRET, RDCLI_COOKIE, SQLITE, write_configuration_file, initialize_db


OUTPUT_DIR = path.abspath('.')


def main():

    try:
        with open(CONF, 'r') as conf:
            options = load(conf)
            oauth_token = options['oauth']['token']
            oauth_token_secret = options['oauth']['token_secret']
            rd_user = options['real-debrid']['username']
            rd_password = options['real-debrid']['password']
            whitelist = options['hawkeye']['whitelist']
    except BaseException:
        try:
            write_configuration_file()
        except BaseException as e:
            exit('Unable to write configuration file: %s' % str(e))

    rd_worker = RDWorker(RDCLI_COOKIE)

    try:
        rd_worker.login(rd_user, rd_password)
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
                    msg = 'Failed %s, will retry later (%s)' % (link[1], e.message)
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
        for info in cursor.execute('SELECT sender, url FROM failed ORDER BY processing_date ASC'):

            if info[0] in whitelist:
                msg = download(info[1])
                try:
                    client.direct_messages.new(user=info[0], text=msg)
                except twitter.TwitterError:
                    try:
                        msg = '%s %s' % (datetime.now().strftime('%d/%m %H:%M:%S'), msg)
                        client.direct_messages.new(user=info[0], text=msg)
                    except twitter.TwitterError:
                        pass

        count = 0
        links = []

        # go through all the DMs
        for dm in client.direct_messages():

            # save a reference to the last processed DMs
            if count == 0:
                count += 1
                values = (dm['id'], datetime.strptime(dm['created_at'], '%a %b %d %H:%M:%S %z %Y'), datetime.now())
                cursor.execute("INSERT OR REPLACE INTO refs VALUES(?, ?, ?)", values)
                connection.commit()

            if dm['id'] == last_processed_dm:
                break

            if len(dm['entities']['urls']):
                for url in dm['entities']['urls']:
                    links.append((dm['sender_screen_name'], url['expanded_url']))

        # sort chronologically
        links.reverse()

        # try to download the new links
        for link in links:
            if link[0] in whitelist:
                msg = download(link)
                try:
                    client.direct_messages.new(user=link[0], text=msg)
                except twitter.TwitterError:
                    try:
                        msg = '%s %s' % (datetime.now().strftime('%d/%m %H:%M:%S'), msg)
                        client.direct_messages.new(user=link[0], text=msg)
                    except twitter.TwitterError:
                        pass

    exit(0)


if __name__ == '__main__':
    main()

# check if output dir exists
# test index conflict in SQLITE