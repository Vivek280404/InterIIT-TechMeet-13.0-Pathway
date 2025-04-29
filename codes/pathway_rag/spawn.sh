#!/bin/bash

# Specify the folder containing the scripts
SCRIPTS_FOLDER="./"

# List of scripts to run
scripts=("pw_new.py" "pw_userkb.py" "rag_server.py" "http_serve.py")

# Run each script in a new screen session
for script in "${scripts[@]}"; do
    full_path="$SCRIPTS_FOLDER/$script"
    if [ -f "$full_path" ]; then
        echo "Starting $script in a new screen session"
        screen -dmS "${script%.py}" python3 "$full_path"
    else
        echo "Error: $script not found in $SCRIPTS_FOLDER"
    fi
done

echo "All scripts have been started in separate screen sessions."
echo "Use 'screen -list' to see the running sessions."
echo "To attach to a session, use 'screen -r SESSION_NAME'."