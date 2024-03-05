class ReceiveError(Exception):
    def __init__(self, message="An error occurred while receiving data.", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            if self.code == 1:
                return f"{__name__}: {self.code} - Server send nothing: {self.args[0]}"
            else:
                return f"{__name__}: {self.code} - Unknown error code: {self.args[0]}"
        else:
            return f"{__name__}: {self.args[0]}"

    def get_error_code(self):
        return self.code
    
class SendError(Exception):
    def __init__(self, message="An error occurred while sending data.", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            if self.code == 1:
                return f"{__name__}: {self.code} - Pipe not writeable: {self.args[0]}"
            else:
                return f"{__name__}: {self.code} - Unknown error code: {self.args[0]}"
        else:
            return f"{__name__}: {self.args[0]}"

    def get_error_code(self):
        return self.code

class ConnectionError(Exception):
    def __init__(self, message="An error occurred while connecting to the pipe server.", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            if self.code == 1:
                return f"{__name__}: {self.code} - Pipe Server not found: {self.args[0]}"
            else:
                return f"{__name__}: {self.code} - Unknown error code: {self.args[0]}"
        else:
            return f"{__name__}: {self.args[0]}"

    def get_error_code(self):
        return self.code

class ConnectionCloseError(Exception):
    def __init__(self, message="An error occurred while closing the pipe connection.", code=None):
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            if self.code == 1:
                return f"{__name__}: {self.code} - Network Error: {self.args[0]}"
            elif self.code == 2:
                return f"{__name__}: {self.code} - Pipe Server not found: {self.args[0]}"
            else:
                return f"{__name__}: {self.code} - Unknown error code: {self.args[0]}"
        else:
            return f"{__name__}: {self.args[0]}"

    def get_error_code(self):
        return self.code