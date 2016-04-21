#!/bin/sh
#version 0.01
#Enumeration test
#./code/systemTest.sh

echo "Target\tResult\tExpected\tFound" | column -t
for f in datasets/measurement+gt/*; do
    echo -n "$(basename $f)\t";
    cut -f1,2,3,5 $f>/tmp/systemTest.input
    expected=$(head -2 $f | tail -1 | cut -f2)
    ./igreedy -i /tmp/systemTest.input | grep Instances | awk -v expe=$expected '{if($2==expe){printf "\033[0;32m OK \033[0m"}else printf "\033[0;31m ERROR \033[0m"; print "\t"expe"\t"$2}';
done;
