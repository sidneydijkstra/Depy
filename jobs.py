import os
import time
import subprocess

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
        repo.pull()
        pass

    def handle_run(self, command):
        """Run shell command"""
        if type(command) is yaml.scalarstring.PlainScalarString:
            print("string is a plain scalar string running command")
            os.system(command)
        else:
            print(f"string is not a plain scalar string running script {command}")
            subprocess.run(["sh", command], cwd=repo.repo_path)
        
        

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
            # Get the step name
            step_name = list(step.keys())[0]
            # Get the step arguments
            step_args = step[step_name]
            # Check if the step name exists in the step_handlers dictionary
            if step_name in self.step_handlers:
                # If it exists, call the corresponding function and pass the step_args
                print(f"{step_name} is running with args: {step_args}. ")
                self.step_handlers[step_name](step_args)
                print(f"{step_name} is completed.")
            else:
                print(f"{step_name} is not a valid step.")
                return False