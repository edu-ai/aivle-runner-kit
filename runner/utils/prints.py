import os, sys
import io

class Output:
    value = None 

class RedirectPrints:
    def __init__(self, output=None):
        self.output = output

    def __enter__(self):
        self._original_stdout = sys.stdout
        if self.output is not None:
            sys.stdout = io.StringIO()
        else:
            sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.output is not None:
            self.output.value = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = self._original_stdout