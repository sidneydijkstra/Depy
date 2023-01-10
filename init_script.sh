#!/bin/bash

# Save current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Get a list of branches, including remote branches, and switch to the previous one
git checkout $(git for-each-ref --count=2 --sort=-committerdate refs/heads/ --format='%(refname:short)' | tail -n1)

# Show current branch name
echo "Switched to previous branch: $(git rev-parse --abbrev-ref HEAD)"

# Display message if current branch is the same as the previous one
if [ "$current_branch" == "$(git rev-parse --abbrev-ref HEAD)" ]; then
  echo "You were already on the latest branch"
fi
