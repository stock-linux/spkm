class PackagesNotFoundException(Exception):
    pkgs: list[str] = []

    def __init__(self, pkgs: list[str]):
        self.pkgs: list[str] = pkgs

class PkgDownloadError(Exception):
    pass

class PkgExtractionError(Exception):
    pass