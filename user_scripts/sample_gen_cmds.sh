#!/bin/bash
# Output one line per command to be run on a worker node. The command should be self-contained i.e navigate to the desired working directory, execute the command, and copy any relevant files over to /tmp/pydealer-client/pydealer-client-results
# This sample script will output a number to stdout, write a file containing the same number to /tmp, and then copy this file to /tmp/pydealer-client/pydealer-client-results
# Odd-numbered jobs will return a non-zero error code to simulate a failed job

for i in {1..10}; do
  ecode=$(expr $i % 2)
  echo "cd ~; sleep 10; echo Output: $i; echo Result: $i > /tmp/result_$i; echo Err: $i >&2; mv /tmp/result_$i /tmp/pydealer-client/pydealer-client-results/; exit $ecode"
done

# Once pydealer finishes executing, we expect to find all our results in the LOCAL_RESULTS_FOLDER defined in init.sh