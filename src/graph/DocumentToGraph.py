import os
from .IndexFile import IndexFile
from .UploadIndexToGraph import UploadIndexToGraph

class DocumentToGraph:

    def run(self,folder):
        IndexFile().run(folder)
        UploadIndexToGraph().run(folder)