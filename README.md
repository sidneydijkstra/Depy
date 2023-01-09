# Depy
Depy stands for Deployment-Python, this program is used to create a simple CI/CD environment for linux applications.

# Example
This is a example command for running this python script:
```
# python ./depy.py -r ./billy -u https://github.com/sidneydijkstra/Billy.git -b main -is ./sh/init.sh -ps ./sh/pull.sh
```
Here we run the depy.py script using the arguments '-r' for setting the directory name, '-u' for the repository link, '-b' for the branch to use, '-is' for initializing shell script to run on clone and '-ps' for the shell script to run on pull.

