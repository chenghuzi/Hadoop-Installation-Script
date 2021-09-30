#!/bin/bash
ssh-keygen -q -t rsa -N '' <<< ""$'\n'"y" 2>&1 >/dev/null
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
cat ~/id_rsa.pub >> ~/.ssh/authorized_keys