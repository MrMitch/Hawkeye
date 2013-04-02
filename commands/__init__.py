import logging


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
        self.pre_hook = None
        self.post_hook = None
        self.options = options

    def execute(self, tweet):
        pass


class CommandPreHookError(BaseException):
    pass


class CommandExecutionError(BaseException):
    pass


class CommandPostHookError(BaseException):
    pass


class Executor(object):

    commands = Factory()

    def __init__(self):
        super(Executor, self).__init__()

    def load(self, command_name, command_options):
        self.result = None
        self.command = Executor.commands.get(command_name, command_options)

    def process(self, tweet, twitter_client):

        try:
            if self.command.pre_hook is not None:
                self.command.pre_hook(tweet, twitter_client)

            self.result = self.command.execute(tweet)

            if self.command.post_hook is not None:
                self.command.post_hook(self.result, tweet, twitter_client)

        except CommandPreHookError as e:
            logging.error('Error during pre-hook for %s command: %s. Tweet to process was: %s'
                          % (type(self.command).__name__, str(e), tweet['text']))
        except CommandExecutionError as e:
            logging.error('Error during main execution for %s command: %s. Tweet to process was: %s'
                          % (type(self.command).__name__, str(e), tweet['text']))
        except CommandPostHookError as e:
            logging.error('Error during post-hook for %s command: %s. Tweet to process was: %s'
                          % (type(self.command).__name__, str(e), tweet['text']))