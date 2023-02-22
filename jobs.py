import os
import time
import subprocess
import json

import yaml

class Jobs:
    def __init__(self, stages, jobs, repo):
        self.stages = stages
        self.jobs = jobs
        self.repo = repo
        # Define the step_handlers dictionary as a class variable
        # This maps step names to the corresponding functions that should be called
        self.step_handlers = {
            'run': self.handle_run,
            'pull': self.handle_pull,
            'bash': self.handle_bash,
            'touch': self.handle_touch,
            'service-create': self.handle_serviceCreate,
            'service-stop': self.handle_serviceStop,
            'service-start': self.handle_serviceStart,
            'service-restart': self.handle_serviceRestart,
            'service-enable': self.handle_serviceRestart,
        }

    def handle_pull(self):
        print("pulling repository")
        self.repo.pull()
        pass

    def handle_run(self, command):
        if '\n' in command:
            print(f"string is a plain scalar string running command: {parsedCommand}")
            parsedCommand = command.rstrip().replace("\n", " && ")
            os.system(parsedCommand)
        else:
            print(f"invalid command: {command}")

    def handle_bash(self, command):
        if '.sh' in command:
            print(f"string is not a plain scalar string running script {command}")
            subprocess.run(["bash", command], cwd=self.repo.repo_path)
        else:
            print(f"invalid command: {command}")
            
    def handle_touch(self, command):
        print(f"invalid command: {command}")
    
    def handle_serviceCreate(self, command):
        if not isinstance(command, dict):
            print('Error in service-create: variable is not a dict')
            return
        elif not command['name'] or not command['directory'] or not command['description'] or not command['command']:
            print('Error in service-create: please define all variables: name, directory and description')
            return

        name = command['name']
        directory = command['directory']
        description = command['description']
        command = command['command']

        content = f"""
            [Unit]
            Description={description}

            [Service]
            WorkingDirectory={directory}
            ExecStart={command}
            Restart=always
            RestartSec=3

            [Install]
            WantedBy=multi-user.target
        """
        
        subprocess.run(["echo", content, f"> /etc/systemd/system/{name}"])

    def handle_serviceStop(self, command):
        subprocess.run(["systemctl stop", command])
        subprocess.run(["systemctl daemon-reload"])
        
    def handle_serviceStart(self, command):
        subprocess.run(["systemctl daemon-reload"])
        subprocess.run(["systemctl start", command])
        
    def handle_serviceRestart(self, command):
        subprocess.run(["systemctl restart", command])
            
    def handle_serviceEnable(self, command):
        subprocess.run(["systemctl enable", command])

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
        if not steps:
            print(f"Steps is not a valid step. {steps}")
            return

        # Iterate over the steps in the current stage
        for step in steps:
            if isinstance(step, dict):
                step_name = list(step.keys())[0]
                step_args = step[step_name]
                if step_name in self.step_handlers:
                    print(f'Running dict step {step_name} with args {step_args}')
                    self.step_handlers[step_name](step_args)
                else:
                    print(f"{step_name} is not a valid step.")
            elif isinstance(step, str):
                step_name = step
                if step_name in self.step_handlers:
                    print(f'Running str step {step_name}')
                    self.step_handlers[step_name]()
                else:
                    print(f"{step_name} is not a valid step.")