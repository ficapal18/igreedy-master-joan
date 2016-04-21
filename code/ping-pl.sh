#! /bin/bash
#  ping-pl.sh
#
#  Created by Danilo Cicalese and Diana Joumblatt.
#  Distributed measurements from PlanetLab
#Example: 
#2 PING 162.159.15.187 without checking the alive vantage points, output save in the results folder, measure RTT and TTL  
#./code/ping-pl.sh 0 162.159.15.187  results 2 0
#retrieve also the ground truth for a DNS IP:
#./code/ping-pl.sh 0 162.159.15.187  results 2 1 
#retrieve also the ground truth for a cloudflare:
#./code/ping-pl.sh 0 162.159.15.187  results 2 2 


PLKEY=".ssh/danilo_rsa" #rsa key has to be added on the PL node
SLICE_NAME="upmc_agent2" #name of the slice

#Parameters:
CheckPLNodeAlive=$1 #0: not check alives vantage points, 1: check alives vantage points
TARGET=$2 #IP Address
RESULTSFOLDER=$3 # where save the results
NUMBERPING=$4 # number of ping
MEASUREMENTTYPE=$5 #0: measure RTT and TTL, 1: DNS groundtruth, TTL and RTT, 2: cloudflare groundtruth, TTL and RTT
PLNODE=$6 #file with the list of PLnodes

######################################################
OUTPUTTEMPFOLDER=/tmp/parallelssh
LISTPLNODE=datasets/planetlab-vps-all #datasets/planetlab-vps list of all PL Vps 
OUTPUTPLNODEALIVE=datasets/planetlab-vps #default list of PL Vps used or PL Vps alive 
PLNODEALIVE=/tmp/planetlab-vps #temp file with the PL nodes, used for the measurement 
vpsParallel=200
timeout=10 #seconds
DIR="ping-$TARGET"

cut -f1 $PLNODE>$PLNODEALIVE #to avoid problem if the user wants use the whole dataset


#pssh function with all the parameters
function psshPL {
    parallel-ssh -o $RESULTSFOLDER/$DIR -p $vpsParallel -t $timeout -O StrictHostKeyChecking=no -x "-i" -x $PLKEY -x "-tt" --user $SLICE_NAME -h $PLNODEALIVE $1
}

#save results in a file
function saveResults {
        cat $RESULTSFOLDER/$DIR/*| awk -F",---" '{print $1}' | grep -v ";" | grep -v "found" | grep -v "not available" | awk 'NF==4{print $0}' >> ${fileOutput}
}

#PlanetLab nodes that are alive
if [ $CheckPLNodeAlive -eq 0 ]; then
    echo "User requested not to check which planetlab vantage points are alive today";
elif [ $CheckPLNodeAlive -eq 1 ]; then
    echo "Checking which planetlab vantage points are alive today";
    # Alive nodes in the slice
    if [ -d $OUTPUTTEMPFOLDER ]; then
        rm -Rf $OUTPUTTEMPFOLDER
        mkdir  $OUTPUTTEMPFOLDER
    fi
    echo -e "$(cut -f1 $LISTPLNODE | tail -n +2)">/tmp/hostnames
    parallel-ssh  -o $OUTPUTTEMPFOLDER -p 150 -t 30 -O StrictHostKeyChecking=no -x "-i" -x $PLKEY -x "-tt" --user $SLICE_NAME -h /tmp/hostnames 'hostname' 
    echo "#hostname"> $OUTPUTPLNODEALIVE
    cat $OUTPUTTEMPFOLDER/* | grep -v lxcsu | grep -v suexec | grep -v "not found" | grep -v "/bin/su" >> $OUTPUTPLNODEALIVE
    exit;
else
    echo "Second argument should be 1 (check alive nodes) or 0 (do not check alive nodes)"
    exit;
fi

######################################################
#Ping the IP in the list provided by the user
if [ -d $RESULTSFOLDER ]; then
    rm -Rf $RESULTSFOLDER
    mkdir  $RESULTSFOLDER
fi

if [ -d resultsPing/$DIR ]; then
    rm -Rf resultsPing/$DIR
fi

fileOutput=$RESULTSFOLDER/$TARGET

if [ $MEASUREMENTTYPE -eq 0 ]; then
    #RTT and TTL
    psshPL 'echo -e "$(ping -c '$NUMBERPING' '$TARGET'| tr "=" " " | cut -d" " -f8,10| head -n '$(($NUMBERPING+1))'| tail -n +2 | sed "s/^/$(hostname) /" )"'
    echo "#hostname ttl rtt[ms]" > $fileOutput
    cat $RESULTSFOLDER/$DIR/*| awk -F",---" '{print $1}' | grep -v ";" | grep -v "found" | grep -v "not available" >> ${fileOutput}
elif [ $MEASUREMENTTYPE -eq 1 ]; then
    #DNS groundtruth
    #GT, TTL and RTT
    psshPL 'gt=$(dig @'$TARGET' hostname.bind txt ch +short | cut -d "\"" -f 2); echo -e "$(ping -c '$NUMBERPING' '$TARGET'| tr "=" " " | cut -d" " -f8,10| head -n '$(($NUMBERPING+1))'| tail -n +2 | sed "s/^/$(hostname) $gt /" )"'
    echo "#hostname gt ttl rtt[ms]" > $fileOutput
    
    saveResults
elif [ $MEASUREMENTTYPE -eq 2 ]; then
    #HTTP head
    #GT, TTL and RTT (cloudflare): 162.159.15.187
    psshPL 'gt=$(curl -s -I '$TARGET' | grep "CF-RAY" | cut -d"-" -f3 |  sed "s/\r//" );echo -e "$(ping -c '$NUMBERPING' '$TARGET'| tr "=" " " | cut -d" " -f8,10| head -n '$(($NUMBERPING+1))'| tail -n +2 | sed "s/^/$(hostname) $gt /" )"'
    echo "#hostname gt ttl rtt[ms]" > $fileOutput
    saveResults

fi;


#--------------------------------------------------------------------------------------------
#istall dig on all the nodes, based on the fedora version:
#parallel-ssh -o $RESULTSFOLDER/$DIR --verbose -p 150 -t 150 -O StrictHostKeyChecking=no -x "-i" -x $PLKEY -x "-tt" --user $SLICE_NAME -h $PLNODEALIVE 'export SUDO_ASKPASS=echo;sudo yum --nogpgcheck -y install bind-utils'
#parallel-ssh -o $RESULTSFOLDER/$DIR --verbose -p 150 -t 150 -O StrictHostKeyChecking=no -x "-i" -x $PLKEY -x "-tt" --user $SLICE_NAME -h $PLNODEALIVE 'export SUDO_ASKPASS=echo;sudo -A yum --nogpgcheck -y install bind-utils'

