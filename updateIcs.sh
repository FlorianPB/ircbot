#!/usr/bin/env bash
while true; do
	echo "Fetching incoming events ($(date +%F %T))"
	let now=$(date +%s);
	curl -s http://sugarcub.bronycub.org/agenda/ics |\
		tr -d "\r\n" |\
		sed "s/END:VEVENT/&\n/g" |\
		sed "s/^.*DTSTART:\(.*\)DTEND.*SUMMARY:\(.*\)DESCRIPTION:\(.*\)UID.*$/\1 \2: \3/g" |\
		sort -u |\
		grep "^[0-9TZ]* .\+$" |\
		while read i; do 
			let t=$(date +%s -d "${i:0:4}-${i:4:2}-${i:6:2} ${i:9:2}:${i:11:2} +0000");
			if [ $t -gt $now ]; then
				echo "$t ${i:17}";
			fi;
		done |\
			cat - events.lst |\
			sort -u > events.lst.tmp
	mv events.lst{.tmp,}
	echo -e "$(cat events.lst)\n"
	sleep 5m
done
