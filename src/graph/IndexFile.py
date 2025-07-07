import os
from graphrag.cli.index import run_index


default_args = {
    "root": os.environ.get("MS_GRAPHRAG_ROOT"),         # Path to your project root
    "config": None,              # Optional path to settings.yml
    "workflows": None,           # Override workflow steps if needed
    "loglevel": "INFO",          # Log level: DEBUG, INFO, etc.
    "force": False,              # Whether to overwrite outputs
    "reset": False,              # Whether to clear previous index state
}
class IndexFile:

    def __init__(self, ):
        self.args = default_args

    def getArgs(self):
        return self.args
    
    def run(self):
        run_index(self.getArgs())



