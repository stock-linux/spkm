'''This module is a simple Logger to log messages to stdout.'''

class Logger:
    '''
    A class representing a Logger.

    Attributes:
        config (dict): SPKM Configuration
        cyan (str): Cyan color code
        red (str): Red color code
        green (str): Green color code
        reset (str): Reset color code
    '''

    def __init__(self, config: dict):
        self.config = config
        self.cyan = '\033[94m'
        self.red = '\033[31m'
        self.green = '\033[92m'
        self.reset = '\033[00m'

    def log_header(self, header: str):
        '''
        Logs a "header" to stdout.

        :param str header: Header message

        :return: None
        '''

        msg = self.cyan

        if self.config['general']['colors'] is False:
            msg += self.reset

        msg += f'SPKM - {header}{self.reset}'

        print(msg)
        print()

    def log_err(self, err: str, err_content = False):
        '''
        Logs an error to stdout.

        :param str err: Error message
        :param bool err_content: Is the message an error content ?

        :return: None
        '''

        msg = self.red

        if self.config['general']['colors'] is False:
            msg += self.reset

        msg += f'{"ERROR " if not err_content else ""}- {err}{self.reset}'

        print(msg)

    def log_info(self, info: str):
        '''
        Logs an info to stdout.

        :param str info: Info message

        :return: None
        '''

        msg = self.cyan

        if self.config['general']['colors'] is False:
            msg += self.reset

        msg += f'INFO - {info}{self.reset}'

        print(msg)

    def log_success(self, success: str):
        '''
        Logs a successful operation to stdout.

        :param str success: Success message

        :return: None
        '''

        msg = self.green

        if self.config['general']['colors'] is False:
            msg += self.reset

        msg += f'SUCCESS - {success}{self.reset}'

        print(msg)

    def log_add(self, pkg: str):
        '''
        Logs a package add to stdout.

        :param str pkg: Package name
        
        :return: None
        '''

        colors = self.config['general']['colors']
        print('[' + self.cyan + (self.reset if not colors else '') + '+' + self.reset + '] ' + pkg)

    def log_del(self, pkg: str):
        '''
        Logs a package deletion to stdout.

        :param str pkg: Package name
        
        :return: None
        '''

        colors = self.config['general']['colors']
        print('[' + self.red + (self.reset if not colors else '') + 'D' + self.reset + '] ' + pkg)

    def log_up(self, pkg: str):
        '''
        Logs a package update to stdout.

        :param str pkg: Package name

        :return: None
        '''

        colors = self.config['general']['colors']
        print('[' + self.green + (self.reset if not colors else '') + 'U' + self.reset + '] ' + pkg)

    def log(self, content: str):
        '''
        Logs a simple output to stdout.

        :param str content: Content to display

        :return: None
        '''

        print(content)
        print()
