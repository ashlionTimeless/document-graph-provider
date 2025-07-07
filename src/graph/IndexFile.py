import os
import subprocess
MS_GRAPHRAG_ROOT = os.environ.get("MS_GRAPHRAG_ROOT")

#cmd_template = [
#        "python3", "-m", "graphrag", "index",
#        "--config", f"{MS_GRAPHRAG_ROOT}/settings.yaml",
#        "--root", f"{MS_GRAPHRAG_ROOT}/{folder}/",
#        "--output", f"{MS_GRAPHRAG_ROOT}/{folder}/output"]

class IndexFile:
    
    def run_index(self,folder):
        cmd = [
            "python3", "/var/www/html/ragtest/script.py"
        ]
        print(cmd)
        try:
            print("before")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("after")
            print(result)
            output = result.stdout
            print(output)
            return output
        except subprocess.CalledProcessError as e:
                error_message = f"An error occurred: {e.stderr}"

    def run(self,folder):
        self.run_index(folder)



