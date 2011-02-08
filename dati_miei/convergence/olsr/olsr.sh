#!/bin/bash

sudo olsrd -f /etc/olsrd/olsrd.conf -d 1 -i eth1 &> olsr_$1.log &
