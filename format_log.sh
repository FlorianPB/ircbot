#!/usr/bin/env bash

file=${file-"old_logs/* ./#bronycub.log"}

[ -d logWork ] && env rm -r logWork
mkdir logWork

sed "s/^\([0-9-]*\)T\([0-9:]*\) *\(<[^>]*>\|\*\{1,3\}\) \(.*\)/[\1 \2] \3 \4/g;s/^\(\[[^]]*\]\) \*\{1,3\}/\1 <info>/g" $file | grep "^\[[^]]*\]" > logWork/tmp.log
cat logWork/tmp.log | cut -d' ' -f3 | sort | uniq > logWork/nicks.lst

let count=0
let size=222

cat logWork/nicks.lst | while read nick; do
	newNick="<[[38;5;${count}m${nick:1:$((${#nick}-2))}[0m>"
	printf "\033[2K\033[1G$nick -> $newNick"
	sed -i "s/$nick/$newNick/g" logWork/tmp.log
	printf "$newNick\n" >> logWork/coloredNicks.lst

	let count=$(($(($count+1))%$size))+1
done
echo ""
mv logWork/tmp.log chat.freenone.net-bronycub.txt
env rm -r logWork
