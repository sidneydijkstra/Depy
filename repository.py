import os
import git

class Repository:
    def __init__(self, repo_path, repo_url, branch_name):
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch_name = branch_name
        self.repo = None

        self.ci = ""
        self.cm = ""

    def getCommitId(self):
        # Open the repository
        repo = git.Repo(self.repo_path)
        # Return the current commit id
        return self.ci
        return repo.remotes.origin.refs[self.branch_name].commit.hexsha

    def getCommitMessage(self):
        # Open the repository
        repo = git.Repo(self.repo_path)
        # Return the current commit message
        return self.cm
        return repo.remotes.origin.refs[self.branch_name].commit.message

    # Try to clone a repository if its not already cloned
    def tryClone(self):
        # Check if the repository already exists
        if not os.path.isdir(self.repo_path):
            # Clone the repository
            git.Repo.clone_from(self.repo_url, self.repo_path, branch=self.branch_name)
            return True
        #end if
        return False

    def tryFetch(self):
        try:
            # Get the repository
            repo = git.Repo(self.repo_path)

            # Fetch the latest changes from the remote repository
            repo.remotes.origin.fetch()

            # Compare the local and remote branches to see if there are any differences
            local_sha = repo.head.object.hexsha
            remote_sha = repo.remotes.origin.refs[self.branch_name].commit.hexsha

            self.ci = repo.remotes.origin.refs[self.branch_name].commit.hexsha
            self.cm = repo.remotes.origin.refs[self.branch_name].commit.hexsha

            # return state of repository
            return local_sha != remote_sha
        except:
            return False
        

    def pull(self):
        # Get the repository
        repo = git.Repo(self.repo_path)
        # Pull any changes
        repo.remotes.origin.pull()
    