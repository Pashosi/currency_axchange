class DatabaseUnavailable(Exception):
    def __init__(self, message='Database unavailable'):
        self.message = message
        super().__init__(self.message)

