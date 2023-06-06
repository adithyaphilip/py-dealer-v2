if [ "$#" -ne 3 ]; then
  echo "Usage: init.sh SERVER_IP SERVER_PORT_NUMBER MAX_PARALLEL_PER_NODE"
  exit 1
fi

ROOT_NAME='/tmp/pydealer-client'
RESULTS_FOLDER="pydealer-client-results"
STDOUT_ERR_FOLDER="pydealer-client-stdouterr"
#INIT_TAR_NAME="init.tar"
BUILD_SH_NAME="pydealer-client-build.sh"
CLIENT_PY_NAME="client.py"
CLIENT_PY_ARGS="$1 $2 \$PSSH_NODENUM $3" # $PSSH_NODENUM is a special variable that parallel-ssh sets per host starting from 0 upwards
LOCAL_RESULTS_FOLDER="client_results"
PSSH_OPTIONS="-O UserKnownHostsFile=/dev/null -O StrictHostKeyChecking=no -p 100000"
SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
USER_NAME="aphilip"

# parallel ssh and 1. change shell to bash
# TODO: Allow compatibility with other shells
parallel-ssh $PSSH_OPTIONS -h input_files/clients "sudo chsh -s /bin/bash $USER_NAME;"
# 2. create the initial folder
parallel-ssh $PSSH_OPTIONS -h input_files/clients "rm -Rf $ROOT_NAME; mkdir $ROOT_NAME && mkdir $ROOT_NAME/$RESULTS_FOLDER && mkdir $ROOT_NAME/$STDOUT_ERR_FOLDER"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because initial folder creation failed!"
  exit 1
fi
echo "Created initial folders!"

# copy over client.py, pydealer-client-build.sh and the tar ball to the initial folder
parallel-scp -t 300 $PSSH_OPTIONS -h input_files/clients client.py "$ROOT_NAME"
# Commented out while we rework our init file setup
# && parallel-scp $PSSH_OPTIONS -h input_files/clients user_scripts/$BUILD_SH_NAME $ROOT_NAME
#&& parallel-scp $PSSH_OPTIONS -h input_files/clients user_scripts/$INIT_TAR_NAME $ROOT_NAME

status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because copying initial files failed!"
  exit 1
fi
echo "Copied initial files!"

# untar the tarball, and call the user's build file with the initial folder as the PWD
# TODO: Commented out for Ray
#parallel-ssh -t 0 $PSSH_OPTIONS -h input_files/clients "cd $ROOT_NAME && tar -xvf $INIT_TAR_NAME && bash $BUILD_SH_NAME"
#status=$?
#if [ $status -ne 0 ]; then
#  echo "Exiting because tarball unwrapping and user script execution failed!"
#  exit 1
#fi
#echo "Unwrapped tarball and built initial build!"

# TODO: Remove this requirement by migrating client starting to dealer.py
# set AcceptEnv on the server to accept PSSH_NODENUM

echo "Setting AcceptEnv on remote hosts if necessary!"
parallel-ssh $PSSH_OPTIONS -h input_files/clients -t 0 "grep -qF 'AcceptEnv PSSH_NODENUM' /etc/ssh/sshd_config || echo 'AcceptEnv PSSH_NODENUM # added by pydealer' | sudo tee -a /etc/ssh/sshd_config"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because setting AcceptEnv on remote hosts failed!"
  exit 1
fi
echo "Finished setting AcceptEnv!"


parallel-ssh $PSSH_OPTIONS -h input_files/clients "echo 'AcceptEnv PSSH_NODENUM' | sudo tee -a /etc/ssh/sshd_config && sudo service ssh restart"

# now start client.py
CLIENT_CMD="cd $ROOT_NAME && python3 $CLIENT_PY_NAME $CLIENT_PY_ARGS > pydealer-client.out 2> pydealer-client.err"
echo "Starting clients with cmd: " $CLIENT_CMD
parallel-ssh $PSSH_OPTIONS -h input_files/clients -t 0 "$CLIENT_CMD"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because client.py starting failed!"
  exit 1
fi
echo "Finished executing all commands!"

# once all the clients have returned, accumulate the results and stdout folders
# NOTE: We've moved this into dealer.py since it handles starting the clients
mkdir -p $LOCAL_RESULTS_FOLDER
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because creating local results folder failed!"
  exit 1
fi

while read ip; do
  scp $SSH_OPTIONS -r $ip:/$ROOT_NAME/$RESULTS_FOLDER $LOCAL_RESULTS_FOLDER
  scp $SSH_OPTIONS -r $ip:/$ROOT_NAME/$STDOUT_ERR_FOLDER $LOCAL_RESULTS_FOLDER
done <input_files/clients
