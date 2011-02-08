#!/bin/bash

echo "Date"
date > test_date_$1.log
echo "Waiting"
sleep 10  
echo "Starting netperf"
netperf -t TCP_RR -D 1 -H 10.0.0.67 -l 60 &> netperf_$1.log
echo "Killing batman"
sudo killall batmand

