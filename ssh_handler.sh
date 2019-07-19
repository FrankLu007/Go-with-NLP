#!/bin/bash

if [ $# -eq 1 ] && [ "$1" = "help" ]; then
	echo "Usage : "
	echo -e "\t remote   : ./worm.sh [IP] [ACCOUNT] [PASSWD]"
	echo -e "\t allow users to login without password.\n"
	echo -e "\t transmit : ./worm.sh transmit [IP] [ACCOUNT] [file]"
	echo -e "\t #need to complete above command.\n"
elif [ $# -eq 4 ] && [ "$1" = "transmit" ]; then
	printf "Transmit the files to the target ... "
	scp $PWD/$4 $3@$2:.
elif [ $# -eq 3 ]; then
	printf "Generate ssh key ... "
	echo "" | ssh-keygen > /dev/null
	printf "\nTransmit the public key to the target ... "
	export SSHPASS=$3
	#sshpass -e ssh -o StrictHostKeyChecking=no $2@$1 'mkdir .ssh'
	#sshpass -e ssh $2@$1 'chmod 700 .ssh'
	#sshpass -e ssh $2@$1 'echo "" > .ssh/authorized_keys'
	sshpass -e scp ~/.ssh/id_rsa.pub $2@$1:~/.ssh/
	sshpass -e ssh $2@$1 'cat .ssh/id_rsa.pub >> .ssh/authorized_keys'
else
	echo -e "Error usage !"
	echo "Try \"sudo ./worm.sh help\" for help."
fi