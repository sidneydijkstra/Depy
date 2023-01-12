import time

def stamp(filePath, branchName, commitId, commitMessage):
    # Get current time
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    # Create the file and write the information to it
    with open(filePath, "w") as file:
        file.write(f"Time: {current_time}\n")
        file.write(f"Commit: {commitId}\n")
        file.write(f"Branch: {branchName}\n")
        file.write(f"{commitMessage}\n")