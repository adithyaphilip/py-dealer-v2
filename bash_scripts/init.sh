if [ -z "$1" ]; then
  echo "Usage: init.sh SERVER_PORT_NUMBER"
fi

ROOT_NAME="/users/aphilip/pydealer-client"
RESULTS_FOLDER="pydealer-client-results"
STDOUT_ERR_FOLDER="pydealer-client-stdouterr"
INIT_TAR_NAME="init.tar"
BUILD_SH_NAME="pydealer-client-build.sh"
CLIENT_PY_NAME="client.py"
CLIENT_PY_ARGS="10.10.1.1 $1"
LOCAL_RESULTS_FOLDER="client_results"
PSSH_OPTIONS="-O UserKnownHostsFile=/dev/null -O StrictHostKeyChecking=no -p 100000"
SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

# parallel ssh and create the initial folder
parallel-ssh $PSSH_OPTIONS -h input_files/clients "rm -Rf $ROOT_NAME; mkdir $ROOT_NAME && mkdir $ROOT_NAME/$RESULTS_FOLDER && mkdir $ROOT_NAME/$STDOUT_ERR_FOLDER"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because initial folder creation failed!"
  exit 1
fi
echo "Created initial folders!"

# copy over client.py, pydealer-client-build.sh and the tar ball to the initial folder
parallel-scp -t 300 $PSSH_OPTIONS -h input_files/clients client.py $ROOT_NAME && parallel-scp $PSSH_OPTIONS -h input_files/clients user_scripts/$BUILD_SH_NAME $ROOT_NAME && parallel-scp $PSSH_OPTIONS -h input_files/clients user_scripts/$INIT_TAR_NAME $ROOT_NAME

status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because copying initial files failed!"
  exit 1
fi
echo "Copied initial files!"

# untar the tarball, and call the user's build file with the initial folder as the PWD
parallel-ssh -t 0 $PSSH_OPTIONS -h input_files/clients "cd $ROOT_NAME && tar -xvf $INIT_TAR_NAME && bash $BUILD_SH_NAME"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because tarball unwrapping and user script execution failed!"
  exit 1
fi
echo "Unwrapped tarball and built initial build!"

# now start client.py
echo "Starting clients!"
parallel-ssh $PSSH_OPTIONS -h input_files/clients -t 0 "cd $ROOT_NAME && python3 $CLIENT_PY_NAME $CLIENT_PY_ARGS > pydealer-client.out 2> pydealer-client.err"
status=$?
if [ $status -ne 0 ]; then
  echo "Exiting because client.py starting failed!"
  exit 1
fi
echo "Finished executing all commands!"

# once all the clients have returned, accumulate the results and stdout folders
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
