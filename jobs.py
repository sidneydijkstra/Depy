import os
import time
import subprocess

import yaml

class Jobs:
    def __init__(self, stages, jobs, repo):
        self.stages = stages
        self.jobs = jobs
        self.repo = repo
        # Define the step_handlers dictionary as a class variable
        # This maps step names to the corresponding functions that should be called
        self.step_handlers = {
            'pull': self.handle_pull,
            'run': self.handle_run,
        }

    def handle_pull(self):
        """Implement repository pull action."""
        print("pulling repository")
        self.repo.pull()
        pass

    def handle_run(self, command):
        """Run shell command"""
        if '\n' in command:
            parsedCommand = command.rstrip().replace("\n", " && ")
            print(f"string is a plain scalar string running command: {parsedCommand}")
            os.system(parsedCommand)
        elif '.sh' in command:
            print(f"string is not a plain scalar string running script {command}")
            #subprocess.run(["sh", command], cwd=self.repo.repo_path)
        else:
            print(f"invalid command: {command}")
            
        

    def tryRunJobs(self):
        # Iterate over the stages
        for stage in self.stages:
            print(f'Running tasks for stage {stage}')
            # Check if the current stage exists in the jobs dictionary
            if stage in self.jobs:
                # Run all steps inside the stage
                self.runSteps(self.jobs[stage]['steps'])
            else:
                print(f"{stage} is not in jobs.")
                return False

    def runSteps(self, steps):
        # Iterate over the steps in the current stage
        for step in steps:
            if isinstance(step, dict):
                step_name = list(step.keys())[0]
                step_args = step[step_name]
                if step_name in self.step_handlers:
                    self.step_handlers[step_name](step_args)
                else:
                    print(f"{step_name} is not a valid step.")
            elif isinstance(step, str):
                step_name = step
                if step_name in self.step_handlers:
                    self.step_handlers[step_name]()
                else:
                    print(f"{step_name} is not a valid step.")