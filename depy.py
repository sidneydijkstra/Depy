import os
import time
import subprocess
import argparse
import logging

import git

# Import the Mailer class from the mailer module
from mailing import Mailer

# Set the path to the log file
log_file = './log.txt'

# Configure the logger
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# Parse command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repo-path", required=True, help="path to the local repository")
parser.add_argument("-u", "--repo-url", required=True, help="URL of the remote repository")
parser.add_argument("-b", "--branch-name", required=True, help="name of the branch to clone")
parser.add_argument("-is", "--init-script-path", required=True, help="path to the script to run on init")
parser.add_argument("-ps", "--pull-script-path", required=True, help="path to the script to run on pull")
parser.add_argument("-s", "--sleep-time", required=False, help="time to sleep after each repo check")
parser.add_argument("-murl", "--mail-url", required=False, help="url to mail client")
parser.add_argument("-musr", "--mail-user", required=False, help="user for mail client")
parser.add_argument("-mpsw", "--mail-password", required=False, help="password for mail client")
parser.add_argument("-mto", "--mail-to", required=False, help="user to mail status to")
args = parser.parse_args()

# Assign the arguments to the variables
repo_path = args.repo_path
repo_url = args.repo_url
branch_name = args.branch_name
init_script_path = args.init_script_path
pull_script_path = args.pull_script_path
sleep_time = args.sleep_time if args.sleep_time else 60
mail_url = args.mail_url
mail_user = args.mail_user
mail_password = args.mail_password
mail_to = args.mail_to

# Create a Mailer object
mailer = Mailer(mail_url, 587, mail_user, mail_password)

# Log varaibles
logging.info(f"Starting Depy with variables: {{\n\trepo_path = {repo_path}\n\trepo_url = {repo_url}\n\tbranch_name = {branch_name}\n\tinit_script_path = {init_script_path}\n\tpull_script_path = {pull_script_path}\n\tsleep_time = {sleep_time}\n\tmail_url = {mail_url}\n\tmail_user = {mail_user}\n\tmail_to = {mail_to}\n}}")

# Check if the repository already exists
if not os.path.isdir(repo_path):
    # Clone the repository
    logging.info(f"Cloning repo from {repo_url} to directory {repo_path}")
    git.Repo.clone_from(repo_url, repo_path, branch=branch_name)
    logging.info(f"Cloning completed")
    
    # Run pull script
    try:
        logging.info(f"Running ssh init script {init_script_path}")
        subprocess.run(["sh", init_script_path], cwd=repo_path)
    except:
        logging.info(f"Not running ssh init script {init_script_path}")

# Open the repository
repo = git.Repo(repo_path)

logging.info(f"Starting depy loop")

# Enter an infinite loop
while True:
    # Fetch the latest changes from the remote repository
    repo.remotes.origin.fetch()

    # Compare the local and remote branches to see if there are any differences
    local_sha = repo.head.object.hexsha
    remote_sha = repo.remotes.origin.refs[branch_name].commit.hexsha

    if local_sha != remote_sha:
        # Pull the changes
        repo.remotes.origin.pull()
        logging.info("Changes detected and pulled")
    
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        # Check if mail values are set
        if mail_url and mail_user and mail_to:
            # Send an email
            mailer.send_email(
                from_addr=mail_user,
                to_addr=mail_to,
                subject=f'New version pulled from remote branch ({repo_path})',
                body=f'A new version was pulled from the remote branch at {current_time}\n\n'
            )
        #end if

        # Run pull script
        try:
            logging.info(f"Running ssh pull script {pull_script_path}")
            subprocess.run(["sh", pull_script_path], cwd=repo_path)
        except:
            logging.info(f"Not running ssh pull script {pull_script_path}")
        #end try
    #end if

    time.sleep(60)
#end while