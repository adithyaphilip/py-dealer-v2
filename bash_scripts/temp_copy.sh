ROOT_NAME="/users/aphilip/pydealer-client"
RESULTS_FOLDER="pydealer-client-results"
STDOUT_ERR_FOLDER="pydealer-client-stdouterr"
LOCAL_RESULTS_FOLDER="client_results"
SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

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
