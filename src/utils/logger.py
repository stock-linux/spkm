class Logger:
    def __init__(self, config: dict):
        self.config = config
        self.cyan = '\033[94m'
        self.red = '\033[31m'
        self.green = '\033[92m'
        self.reset = '\033[00m'
        
    def log_header(self, header: str):
        msg = self.cyan
        
        if self.config['general']['colors'] == False:
            msg += self.reset

        msg += f'SPKM - {header}{self.reset}'

        print(msg)
        print()

    def log_err(self, err: str, err_content = False):
        msg = self.red
        
        if self.config['general']['colors'] == False:
            msg += self.reset

        msg += f'{"ERROR " if not err_content else ""}- {err}{self.reset}'

        print(msg)

    def log_info(self, info: str):
        msg = self.cyan
        
        if self.config['general']['colors'] == False:
            msg += self.reset

        msg += f'INFO - {info}{self.reset}'

        print(msg)

    def log_success(self, success: str):
        msg = self.green
        
        if self.config['general']['colors'] == False:
            msg += self.reset

        msg += f'SUCCESS - {success}{self.reset}'

        print(msg)

    def log_add(self, pkg: str):
        colors = self.config['general']['colors']
        print('[' + self.cyan + (self.reset if not colors else '') + '+' + self.reset + '] ' + pkg)

    def log_del(self, pkg: str):
        colors = self.config['general']['colors']
        print('[' + self.red + (self.reset if not colors else '') + 'D' + self.reset + '] ' + pkg)

    def log_up(self, pkg: str):
        colors = self.config['general']['colors']
        print('[' + self.green + (self.reset if not colors else '') + 'U' + self.reset + '] ' + pkg)

    def log(self, content: str):
        print(content)
        print()
