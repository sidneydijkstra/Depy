import os
import time
import argparse
import subprocess
import argparse
import logging

import yaml
import git

# Import the stamper module
import stamper

# Import the Mailer class from the mailer module
from mailing import Mailer
# Import the Repository class from the repository module
from repository import Repository
# Import the Jobs class from the jobs module
from jobs import Jobs

# Setup command arguments
parser = argparse.ArgumentParser(description='Depy CI/CD')
parser.add_argument("--file", required=False, help="Path to depy config gile", default="./depy.config.yaml")
args = parser.parse_args()

# Get depy config location
config_path = args.file

# Open the YAML file
with open(config_path, "r") as file:
    # Load the contents of the file
    content = file.read()
    config = yaml.safe_load(content)
    if 'variables' in config:
        for key, value in config['variables'].items():
            content = content.replace("${{ variables."+key+" }}", value)
            
        config = yaml.safe_load(content)

# Check repo variables
if 'repository' not in config or 'path' not in config['repository'] or 'url' not in config['repository'] or 'branch' not in config['repository']:
    raise ValueError("Missing required configuration parameters for the repository: path, url, branch")

# Create repo variables
repo_init = config['repository']['init'] if 'init' in config['repository'] else False
repo_forceRebuild = config['repository']['force_rebuild'] if 'force_rebuild' in config['repository'] else False
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
stages = config['stages']
jobs = config['jobs']

# Get stamp file path
stamp_path = f'{repo_path}/depy.stamp' if ('stamp_path' not in config) else f"{repo_path}/{config['stamp_path']}"

# Create sleep_time variable
sleep_time = config['sleep_time'] if 'sleep_time' in config else 60

# Create a Mailer object
mailer = Mailer(mailer_enable, mailer_url, 587, mailer_user, mailer_password)

# Create a Repository object
repo = Repository(repo_path, repo_url, branch_name)

# Create a Jobs object
jobs = Jobs(stages, jobs, repo)

# Log varaibles
#logging.info(f"Starting Depy with variables: {{\n\trepo_path = {repo_path}\n\trepo_url = {repo_url}\n\tbranch_name = {branch_name}\n\tinit_script_path = {init_script_path}\n\tpull_script_path = {pull_script_path}\n\tsleep_time = {sleep_time}\n\tmail_url = {mail_url}\n\tmail_user = {mail_user}\n\tmail_to = {mail_to}\n}}")

# Try to clone the repository if init is active
print('All services started correctly')
if repo_init:
    if repo.tryClone():
        # Run pull script
        jobs.tryRunJobs()

        # Create a new depy stamp
        stamper.stamp(stamp_path, branch_name, repo.getCommitId(), repo.getCommitMessage())
    elif repo_forceRebuild:
        # Run pull script
        jobs.tryRunJobs()

# Get log file path and configure the logger
log_path = f"{repo_path}/depy.log" if ('log_path' not in config) else f"{repo_path}/{config['log_path']}"
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(message)s')

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

        # Create a new depy stamp
        print('sleep for repo to update')
        time.sleep(5)
        print('upd')
        stamper.stamp(stamp_path, branch_name, repo.getCommitId(), repo.getCommitMessage())
    #end if

    time.sleep(sleep_time)
#end while