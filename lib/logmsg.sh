#!/usr/bin/env false

liblist+=("logmsg");
HOOKS["msg_received"]+="log_message;";
HOOKS["cmd_received"]+="log_action;";

# ---------- Settings ----------
logdir="./";
logchan="#bronycub";

# ---------- Fcts ----------
log_message()
{
	[ "${irc_target:0:1}" != "#" ] && return;

	echo -n "$(date +%Y-%m-%dT%H:%M:%S) " >> "${logdir}/${logchan}.log"
	if [ $(printf "%d" \'${irc_msg:0:1}) -eq 1 ] && [ "${irc_msg:1:7}" == "ACTION " ]; then
		echo "* $irc_user $(echo "$irc_msg"|tr "\01" " "|sed 's| ACTION ||;s| $||')" >> "${logdir}/${logchan}.log"
	else
		echo "<$irc_user> $irc_msg" >> "${logdir}/${logchan}.log";
	fi
}
log_action()
{
	local action;
	
	[ $(echo "$LINE"|grep "QUIT\|JOIN\|PART"|wc -l) -lt 1 ] && return;

	action="$(echo "$LINE"|sed 's/^:\([^!]*\)![^ ]* \(QUIT\|JOIN\|PART\).*$/\2 \1/')"
	echo -n "$(date +%Y-%m-%dT%H:%M:%S) *** $(echo "$action"|cut -d' ' -f2-) " >> "${logdir}/${logchan}.log"
	action="$(echo "$action"|cut -d' ' -f1)";

	case $action in
		"QUIT"|"PART")
			echo "est parti" >> "${logdir}/${logchan}.log";;
		"JOIN")
			echo "s'est connecté" >> "${logdir}/${logchan}.log";;
		*)
			;;
	esac
}
log_last()
{
	local qty="${1-10}";
	local A=" ";

	send "PRIVMSG $irc_back :Voilà ce qu'il s'est passé ces $qty dernières lignes, $irc_user";
	
	tail -n $qty "$logdir/${logchan}.log" | while [ "$A" != "" ]; do
		read A;
		[ "$A" != "" ] && {
			send "PRIVMSG $irc_back :${A}";
			sleep 0.1;
		}
	done
}

[ -d "$logdir" ] || mkdir -p "$logdir";
