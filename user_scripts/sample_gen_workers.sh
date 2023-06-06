#!/bin/bash
# Output the IP addresses of worker nodes to stdout - one per line
for i in {1..5}; do echo "10.10.1.$i"; done