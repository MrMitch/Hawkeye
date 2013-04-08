from json import dump
from os import path
import modules.twitter_api as twitter
from modules.rdcli import ask_credentials


BASE = path.join(path.abspath(path.expanduser('~')), '.config', 'hawkeye')
BASE = '/etc/hawkeye'
CONF = path.join(BASE, 'hawkeye.conf.json')


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
    rd_user, rd_password = ask_credentials()

    conf = {
        'real-debrid': {
            'username': rd_user,
            'password': rd_password
        },
        'oauth': {
            'token': oauth_token,
            'token_secret': oauth_token_secret
        }
    }

    with open(CONF, 'wb') as output:
        dump(conf, output, indent=4)