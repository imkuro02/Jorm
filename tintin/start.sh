#!/bin/bash
firejail --private ttyd -p 8080 tt++ -e "#DELAY {1} {#SPLIT 0 0};" -e "#SESSION {3k} {127.0.0.1} {4001};" -e "#DELAY {1} {#SPLIT 0 0};"