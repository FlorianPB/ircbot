#!/usr/bin/env bash

source config/SHBot.cfg

disp()
{
	sed 's/\(^[0-9]*-[0-9]*-[0-9]*T[0-9]*:[0-9]*:[0-9]*  \?\)\(<[^>]*>\)\(.*\)/\1[32m\2[0m\3/' |\
	sed 's/\(^[0-9]*-[0-9]*-[0-9]*T[0-9]*:[0-9]*:[0-9]*  \?\)\(\*\(\*\*\)\?.*$\)/\1[33m\2[0m/' |\
	less -cNRS
}

if [ "$1" == "-a" ]; then
	cat old_logs/* "./${CHAN}".log | disp
else
	cat old_logs/${CHAN}.$(date +%Y%m)* ./"${CHAN}".log | disp
fi

