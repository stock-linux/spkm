''' Exceptions' module. '''

class PkgNotFoundException(Exception):
    ''' Raised when a package is not found. '''

class PkgDownloadError(Exception):
    ''' Raised when an error occured during a download. '''

class PkgExtractionError(Exception):
    ''' Raised when an error occured during the extracting process. '''
