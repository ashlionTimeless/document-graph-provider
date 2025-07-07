import os
import subprocess

cmd = [
        "python3", "-m", "graphrag index",
        "--root", "./resume-matching",
        "--method", "local",
]

class IndexFile:
    
    def run_index(self,folder):
        cmd = [
        "graphrag index",
        "--config", "./settings.yaml",
        "--root", f"./{folder}/",
        "--output", f"./{folder}/output"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            return output
        except subprocess.CalledProcessError as e:
                error_message = f"An error occurred: {e.stderr}"

    def run(self,folder):
        self.run_index(folder)



