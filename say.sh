#!/usr/bin/env bash
init=${init-1404158760}
file=old_logs/*
tempo=${tempo-"0.095"}

[ "$1" == "-h" ] && {
	echo -e "init <unix timestamp>    The initial time
file <path to txt file>  The file to look
tempo <time in s>        1.0=normal speed, 0.1=10 times speed"
	exit 1
}

clear
cur_nick=""
old_day=""
while [ 1 ] ; do
	dte="$(date +"%Y-%m-%dT%H:%M:%S" -d "@${init}")";
	hour="$(date +%H:%M:%S -d "@$init")";
	day="$(date +"%A %-d %B %Y" -d "@$init")"

	line="$(grep -h "^${dte}" ${file})";
	lns=$(echo "$line"|wc -l)
	for i in $(eval echo {1..$lns}); do
		new_nick="$(echo "$line"|tail -n $i|head -n 1|grep -o "<[^>]*>" | head -1 | tr -d "<>")"
		txt_line="$(echo "$line"|tail -n $i|head -n 1|sed "s/^[0-9T:-]* *\(<[^>]*>\|\*\(\*\*\)\?\) \(.*\)/\3/")"
		if [ "$day" != "$old_day" ]; then
			old_day=$day
			st=$(((78-${#day})/2))
			printf "\n\033[37m$(head -c 80 /dev/zero|tr "\0" "-"|sed "s/-/─/g")\033[${st}G $day \033[0m\n"
		fi
		if [ "$new_nick" != "$cur_nick" ] && [ "$new_nick" != "" ]; then
			printf "\n \033[1;34m${new_nick}\033[0m\033[72G\033[37m$hour\033[0m\n"
			cur_nick="$new_nick"
		fi

		while [ ${#txt_line} -gt 77 ]; do
			printf "   ${txt_line:0:77}\n"
			txt_line="${txt_line:77}"
		done
		if [ "$txt_line" != "" ]; then
			printf "   $txt_line\n"
		fi
	done
	sleep ${tempo};
	let init++;
done
