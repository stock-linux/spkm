class Logger:
    def __init__(self, config: dict):
        self.config = config
        self.cyan = '\033[94m'
        self.red = '\033[31m'
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

    def log(self, content: str):
        print(content)
        print()
