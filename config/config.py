from ConfigParser import SafeConfigParser
import twitter
from os import path
import sqlite3
from rdcli import RDWorker

BASE = path.join(path.abspath(path.expanduser(u'~')), '.config', 'hawkeye')
BASE = path.join(path.abspath(path.expanduser('./')))
CONF = path.join(BASE, 'hawkeye.conf')
SQLITE = path.join(BASE, 'hawkeye.db')

RDCLI_COOKIE = path.join(BASE, 'rdcli.cookie')

APP_NAME = 'Hawkeye Server'
CONSUMER_KEY = 'OzICYfiYXDZlo41cMBr1yQ'
CONSUMER_SECRET = '7mN5kptD3Qc14Jb5KWJnTMcICG6FXf5cAAJdX7MA'


def _parse_oauth_tokens(raw):
    for r in raw.split('&'):
        k, v = r.split('=')
        if k == 'oauth_token':
            oauth_token = v
        elif k == 'oauth_token_secret':
            oauth_token_secret = v
    return oauth_token, oauth_token_secret


def _oauth_dance():

    api = twitter.Twitter(auth=twitter.OAuth('', '', CONSUMER_KEY, CONSUMER_SECRET), format='', api_version=None)

    oauth_token, oauth_token_secret = _parse_oauth_tokens(api.oauth.request_token())
    oauth_url = ('http://api.twitter.com/oauth/authorize?oauth_token=' + oauth_token)

    print("Please ALLOW %s to access your Twitter account and enter the PIN given here:\n%s ." % (APP_NAME, oauth_url))

    pin = raw_input("Please enter the PIN: ").strip()

    api = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET), format='',
                          api_version=None)

    raw_tokens = api.oauth.access_token(oauth_verifier=pin)
    return _parse_oauth_tokens(raw_tokens)


def write_configuration_file():
    oauth_token, oauth_token_secret = _oauth_dance()

    parser = SafeConfigParser()
    parser.add_section('hawkeye')
    parser.set('hawkeye', 'oauth_token', oauth_token)
    parser.set('hawkeye', 'oauth_token_secret', oauth_token_secret)

    rd_worker = RDWorker(RDCLI_COOKIE, CONF)
    rd_info = rd_worker.ask_credentials()

    parser.add_section('rdcli')
    parser.set('rdcli', 'username', rd_info['user'])
    parser.set('rdcli', 'password', rd_info['pass'])

    with open(CONF, 'wb') as conf:
        parser.write(conf)


def initialize_db():
    with sqlite3.connect(SQLITE, detect_types=sqlite3.PARSE_DECLTYPES) as connection:
        cursor = connection.cursor()

        cursor.execute('DROP TABLE IF EXISTS refs')
        cursor.execute('DROP TABLE IF EXISTS failed')

        cursor.execute('CREATE TABLE refs(tweet_id INT, creation_date timestamp, processing_date timestamp)')
        cursor.execute('CREATE TABLE failed(sender text, url text, processing_date timestamp)')
