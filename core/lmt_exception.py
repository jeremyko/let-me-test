
class LmtException(Exception): 
    def __init__(self, value): 
        self.message = value 

    def __str__(self): 
        return self.message

