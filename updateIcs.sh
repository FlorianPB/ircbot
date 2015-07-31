#!/usr/bin/env bash
let now=$(date +%s);
curl -s https://www.google.com/calendar/ical/bronycub%40gmail.com/public/basic.ics |\
	tr -d "\r\n" |\
	sed "s/END:VEVENT/&\n/g" |\
	sed "s/^.*DTSTART:\(.*\)DTEND.*LOCATION:\(.*\)SEQUENCE.*SUMMARY:\(.*\)TRANSP:.*$/\1 \3 (\2)/g" |\
	sort -u |\
	grep "^[0-9TZ]* .\+$" |\
	while read i; do 
		let t=$(date +%s -d "${i:0:4}-${i:4:2}-${i:6:2} ${i:9:2}:${i:11:2} +0000");
		if [ $t -gt $now ]; then
			echo "$t ${i:17}";
		fi;
	done
