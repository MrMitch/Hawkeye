import logging
import threading


class Factory(object):
    """
    http://code.activestate.com/recipes/86900/
    """
    def register(self, methodName, constructor, *args, **kwargs):
        """register a constructor"""
        _args = [constructor]
        _args.extend(args)
        setattr(self, methodName, Functor(*_args, **kwargs))

    def get(self, key, *args, **kwargs):
        return getattr(self, key)(*args, **kwargs)

    def unregister(self, methodName):
        """unregister a constructor"""
        delattr(self, methodName)


class Functor(object):

    def __init__(self, function, *args, **kwargs):
        assert callable(function), "function should be a callable obj"
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """call function"""
        _args = list(self._args)
        _args.extend(args)
        _kwargs = self._kwargs.copy()
        _kwargs.update(kwargs)
        return self._function(*_args, **_kwargs)


class Command(object):

    def __init__(self, options):
        self.options = options

    def execute(self, tweet):
        pass


class CommandError(BaseException):
    """
    Base exception for command-related errors
    """

    def __init__(self, cause):
        super(CommandError, self).__init__(cause)
        self.cause = cause


class CommandPreHookError(CommandError):
    pass


class CommandExecutionError(CommandError):
    pass


class CommandPostHookError(CommandError):
    pass


class Error(Command):
    """
    Error command, generates errors.
    """

    def __init__(self, options):
        super(Error, self).__init__(options)

    # def pre_hook(self, *args):
    #    raise BaseException('This error is thrown during pre-hook')

    def execute(self, tweet):
        pass
        # raise RuntimeError('This error is thrown during execution')

    def post_hook(self, *args):
        raise RuntimeError('This error is thrown during post-hook')


class Executor(object):

    commands = Factory()
    __error_message = '%s during %s command: %s.\nTweet to process was: %s'

    def __init__(self):
        super(Executor, self).__init__()

    def load(self, command_name, command_options):
        self.command = Executor.commands.get(command_name, command_options)

    def __run_command_life_cycle(self, tweet, twitter_client):
        result = None

        print "%s started" % self.command.__class__.__name__

        try:
            try:
                self.command.pre_hook(tweet, twitter_client)
            except AttributeError:
                pass
            except BaseException as e:
                raise CommandPreHookError(e)

            try:
                result = self.command.execute(tweet)
            except AttributeError:
                pass
            except BaseException as e:
                raise CommandExecutionError(e)

            try:
                self.command.post_hook(result, tweet, twitter_client)
            except AttributeError:
                pass
            except BaseException as e:
                raise CommandPostHookError(e)

        except CommandError as e:
            logging.error(Executor.__error_message % (e.__class__.__name__, self.command.__class__.__name__,
                                                      str(e.cause), tweet['text']))

    def process(self, tweet, twitter_client):
        thread = threading.Thread(target=self.__run_command_life_cycle, args=(tweet, twitter_client))
        thread.start()
