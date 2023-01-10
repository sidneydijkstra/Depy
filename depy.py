import os
import time
import subprocess
import argparse
import logging

import yaml
import git

# Import the Mailer class from the mailer module
from mailing import Mailer
# Import the Repository class from the repository module
from repository import Repository
# Import the Jobs class from the jobs module
from jobs import Jobs

# Open the YAML file
with open("depy.config.yaml", "r") as file:
    # Load the contents of the file
    config = yaml.safe_load(file)

# Get log file path and configure the logger
log_file = './depy.log' if ('log_file' not in config) else config['log_file']
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# Check repo variables
if 'repository' not in config or 'path' not in config['repository'] or 'url' not in config['repository'] or 'branch' not in config['repository']:
    raise ValueError("Missing required configuration parameters for the repository: path, url, branch")

# Create repo variables
repo_path = config['repository']['path']
repo_url = config['repository']['url']
branch_name = config['repository']['branch']

# Check mailer variables
if 'mailer' in config and 'enable' in config['mailer'] and config['mailer']['enable']:
    if 'url' not in config['mailer'] or 'user' not in config['mailer'] or 'password' not in config['mailer'] or 'to' not in config['mailer']:
        raise ValueError("Missing required configuration parameters for mailing: url, user, password and to. Disable the mailing component or enter the required parameters")
        
# Create mailer variables
mailer_enable = config['mailer']['enable']
mailer_url = config['mailer']['url']
mailer_user = config['mailer']['user']
mailer_password = config['mailer']['password']
mailer_to = config['mailer']['to']

# Check stages and jobs variables
if 'stages' not in config or 'jobs' not in config:
    raise ValueError("Missing required configuration parameters for handling stages and jobs: stages, jobs")

# Create stages and jobs variables
init = config['init']
stages = config['stages']
jobs = config['jobs']


# Create a Mailer object
mailer = Mailer(mailer_enable, mailer_url, 587, mailer_user, mailer_password)

# Create a Repository object
repo = Repository(repo_path, repo_url, branch_name)

# Create a Jobs object
jobs = Jobs(stages, jobs, repo)

# Log varaibles
#logging.info(f"Starting Depy with variables: {{\n\trepo_path = {repo_path}\n\trepo_url = {repo_url}\n\tbranch_name = {branch_name}\n\tinit_script_path = {init_script_path}\n\tpull_script_path = {pull_script_path}\n\tsleep_time = {sleep_time}\n\tmail_url = {mail_url}\n\tmail_user = {mail_user}\n\tmail_to = {mail_to}\n}}")

# Try to clone the repository
if repo.tryClone():
    if init:
        # Run pull script
        logging.info(f"Running init steps")
        jobs.runSteps(init)
        logging.info(f"Completed init steps")

logging.info(f"Starting depy loop")

# Enter an infinite loop
while True:
    # Try to fetch a new commit
    if repo.tryFetch():
        # Pull the changes
        logging.info("Changes detected and pulled")
        
        logging.info("--Running jobs--")
        jobs.tryRunJobs()
        logging.info("--Jobs completed--")
    
        # Get current time
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        # Send an email
        mailingStatus = mailer.send_email(
            from_addr=mailer_user,
            to_addr=mailer_to,
            subject=f'New version pulled from remote branch ({repo_path})',
            body=f'A new version was pulled from the remote branch at {current_time}\n\n'
        )

        # Check if mail is send
        if mailingStatus:
            logging.info(f"Send mail to from {mail_user} to {mail_to}")
        #end if
    #end if

    time.sleep(60)
#end while