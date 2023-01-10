#!/bin/bash

# Get the current commit hash
current_commit=$(git rev-parse HEAD)

# Switch to the previous commit
git reset --hard HEAD~1

# Show the new commit hash
echo "Switched to previous commit: $(git rev-parse HEAD)"

# Display message if current commit and the previous one are the same
if [ "$current_commit" == "$(git rev-parse HEAD)" ]; then
  echo "You were already on the latest commit"
fi
