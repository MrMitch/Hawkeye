import json
from commands.repository import registered_commands
from json import dump, dumps
from os import path
import modules.twitter_api as twitter

BASE = path.join(path.abspath(path.expanduser('~')), '.config', 'hawkeye')
BASE = '/etc/hawkeye'
CONF = path.join(BASE, 'hawkeye.conf.json')

APP_NAME = 'Hawkeye Server'
CONSUMER_KEY = 'OzICYfiYXDZlo41cMBr1yQ'
CONSUMER_SECRET = '7mN5kptD3Qc14Jb5KWJnTMcICG6FXf5cAAJdX7MA'


def __error_frame(msg):
    border = '*' * len(msg)
    return '\n%s' % '\n'.join((border, msg, border, ''))


def __parse_oauth_tokens(raw):
    for r in raw.split('&'):
        k, v = r.split('=')
        if k == 'oauth_token':
            oauth_token = v
        elif k == 'oauth_token_secret':
            oauth_token_secret = v
    return oauth_token, oauth_token_secret


def __get_oauth_tokens():

    api = twitter.Twitter(auth=twitter.OAuth('', '', CONSUMER_KEY, CONSUMER_SECRET), format='', api_version=None)

    oauth_token, oauth_token_secret = __parse_oauth_tokens(api.oauth.request_token())
    oauth_url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s' % oauth_token

    print('Please ALLOW %s to access your Twitter account and enter the PIN given here:\n%s' % (APP_NAME, oauth_url))

    pin = raw_input("Please enter the PIN: ").strip()

    api = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET), format='',
                          api_version=None)

    try:
        raw_tokens = api.oauth.access_token(oauth_verifier=pin)
        return __parse_oauth_tokens(raw_tokens)
    except twitter.TwitterHTTPError as e:
        print __error_frame(e.response_data)
        return None, None


def __build_hawkeye_config(commands):
    config = {}

    # Twitter access tokens
    print '\nTwitter access configuration'
    oauth_token, oauth_token_secret = __get_oauth_tokens()
    config['oauth_token'] = oauth_token
    config['oauth_token_secret'] = oauth_token_secret

    # command selection strategy
    print '\nWhat strategy should %s apply to select the allowed commands: ' % APP_NAME
    print '  - exclusive (-): every available command is allowed *except the ones specified*'
    print '  - inclusive (+): the *only allowed commands* are the one specified'
    strategy = raw_input('Command selection strategy ["+" or "-" (inclusive or exclusive)]: ').strip()

    # sugar!
    if strategy not in ('-', 'ex', 'exclusive'):
        elected = 'inclusive'
        config['command_registering_strategy'] = '+'
    else:
        elected = 'exclusive'
        config['command_registering_strategy'] = '-'

    # commands concerned by the strategy
    print '\nWhich commands should be concerned by the %s strategy ?' % elected
    print 'Available commands: %s ' % ', '.join(commands)

    config['commands'] = []
    while True:
        c = raw_input('Command name (empty value to end the list): ').strip()

        if c == '':
            break

        if c in commands:
            config['commands'].append(c)

        print '\rConcerned commands: %s' % ', '.join(config['commands'])

    # users whitelist
    config['whitelist'] = []
    print '\nFrom which user(s) should %s accept commands ?' % APP_NAME

    while True:
        name = raw_input('User name (empty value to end the list): ').strip()

        if name == '':
            break

        config['whitelist'].append(name.lstrip('@'))

        print '\rUsers: %s' % ', '.join(config['whitelist'])

    return config


def write_configuration_file():
    print r''' _    _                _
| |  | |              | |
| |__| | __ ___      _| | _____ _   _  ___
|  __  |/ _` \ \ /\ / / |/ / _ \ | | |/ _ \
| |  | | (_| |\ V  V /|   <  __/ |_| |  __/
|_|  |_|\__,_| \_/\_/ |_|\_\___|\__, |\___|
                                 __/ |
                                |___/
    '''
    save = True
    commands = {}

    for command in registered_commands:
        commands[command[0]] = command[1]

    commands['hawkeye (required)'] = None

    try:
        with open(CONF, 'r') as config_file:
            options = json.load(config_file)

        print 'Existing configuration found for commands: %s' % ', '.join(options.keys())
        print '/!\\ Choosing to re-configure one of these commands will erase any of its ' \
              'existing configuration options on save.'
    except IOError:
        print 'No configuration file found'
        options = {
            'hawkeye': __build_hawkeye_config(commands.keys())
        }

    print '\nAvailable commands:'
    print "\n".join(commands.keys())

    while True:
        try:
            command_name = raw_input('\nCommand to configure '
                                     '(? for command list, empty value to save, Ctrl^C to cancel and exit): ').strip()
            config = {}

            if command_name == '':
                break

            if command_name == '?':
                print '\nAvailable commands:'
                print "\n".join(commands.keys())
                continue

            if command_name != 'hawkeye':
                try:
                    configurable = commands[command_name].configurable_options()

                    if len(configurable) == 0:
                        print 'No option to configure'
                        continue
                    else:
                        for option in configurable:
                            value = raw_input('%s > %s (%s): ' % (command_name, option[0], option[1]))

                            try:
                                converter = option[2]
                            except IndexError:
                                converter = str

                            config[option[0]] = converter(value)
                except KeyError:
                    print __error_frame('Unknown command %s' % command_name)
                    continue
            else:
                config = __build_hawkeye_config(commands.keys())

            options[command_name] = config
            print '\n---- %s configured ----' % command_name
        except (KeyboardInterrupt, EOFError):
            save = False
            break

    if save:
        try:
            with open(CONF, 'wb') as output:
                dump(options, output, options, indent=4, separators=(', ', ': '))
            print 'Configuration saved to %s' % CONF
        except IOError as e:
            print 'Unable to write configuration to disk (%s): %s' % (CONF, e)
            print_to_term = raw_input('Would you like to output the config file\'s content here ? (y/n): ')

            if print_to_term.lower() == 'y' or print_to_term.lower() == 'yes':
                print dumps(options, indent=4, separators=(', ', ': '))
    else:
        print '\nNothing was saved'
