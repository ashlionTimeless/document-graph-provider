import os
from .IndexFile import IndexFile
from .UploadIndexToGraph import UploadIndexToGraph

class DocumentToGraph:

    def run(self):
        IndexFile().run()
        UploadIndexToGraph().run()