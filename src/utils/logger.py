class Logger:
    def __init__(self, config: dict):
        self.config = config
        self.cyan = '\033[94m'
        self.reset = '\033[00m'
        
    def log_header(self, header: str):
        msg = self.cyan
        
        if self.config['general']['colors'] == False:
            msg += self.reset

        msg += f'SPKM - {header}{self.reset}'

        print(msg)
        print()

    def log(self, content: str):
        print(content)
        print()
