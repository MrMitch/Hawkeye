import json
from commands.repository import registered_commands
from json import dump
from os import path
import modules.twitter_api as twitter

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
    # oauth_token, oauth_token_secret = _oauth_dance()

    conf = {
        'hawkeye': {
            "oauth_token": "1163112044-QV9KrjAzj6KKBz5xj9TpVlPhQLvc9TAzaYJC6hg",
            "oauth_token_secret": "O0BH50I6q7oGRMOPNUqxpI2tM11TyGKqrtHzd2rWIs",
            "default_command": "log",

            "whitelist": [
                "__RobinBerry"
            ],

            "command_registering_strategy": "-",
            "commands": [
                "rd"
            ]
        }
    }
    print r''' _    _                _
| |  | |              | |
| |__| | __ ___      _| | _____ _   _  ___
|  __  |/ _` \ \ /\ / / |/ / _ \ | | |/ _ \
| |  | | (_| |\ V  V /|   <  __/ |_| |  __/
|_|  |_|\__,_| \_/\_/ |_|\_\___|\__, |\___|
                                 __/ |
                                |___/
    '''

    try:
        with open(CONF, 'r') as config_file:
            options = json.load(config_file)

        print 'Existing configuration found for modules: %s' % ', '.join(options.keys())
        print '/!\\ Choosing to re-configure one of these commands will erase any existing ' \
              'configuration option on save.'
    except IOError:
        options = {}

    save = True
    commands = {}

    for command in registered_commands:
        commands[command[0]] = command[1]

    while True:
        try:
            print '\nAvailable commands: '
            print "\n".join(commands.keys())

            command_name = raw_input('\nCommand to configure (empty value to save, Ctrl^C to cancel): ').strip()
            config = {}

            if command_name == '':
                break

            if command_name is not 'hawkeye':
                try:
                    for option in commands[command_name].configurable_options():
                        value = raw_input('%s > %s (%s): ' % (command_name, option[0], option[1]))

                        try:
                            converter = option[2]
                        except IndexError:
                            converter = str

                        config[option[0]] = converter(value)

                    options[command_name] = config
                except KeyError:
                    print 'Unknown command %s' % command_name
                    continue
            else:
                pass
        except KeyboardInterrupt:
            print '\nAborted, nothing was saved.'
            save = False
            break

    if save:
        s = json.dumps(options, indent=4, separators=(', ', ': '))
        #with open(CONF, 'wb') as output:
        #    dump(config, output, options, indent=4, separators=(', ', ': '))
        print "\n %s" % s
