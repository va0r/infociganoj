#!/usr/bin/zsh

sudo service redis stop ;\
sudo service postgres stop ;\
sudo sysctl vm.overcommit_memory=1