#!/usr/bin/env false

# Gestion du fichier de log du canal
# Auteur: Adrien Sohier (adriens33)

liblist+=("logmsg");
HOOKS["msg_received"]+="log_message;";
HOOKS["cmd_received"]+="log_action;";


# ---------- Settings ----------
logdir="./";
logchan="#bronycub";

# ---------- Fcts ----------
# Logue un message utilisateur (ou une action, ie. « * machintruc fait ceci »)
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

# Logue une arrivée/un départ utilisateur
log_action()
{
	local action name;
	
	[ $(echo "$LINE"|grep "QUIT\|JOIN\|PART"|wc -l) -lt 1 ] && return;

	action="$(echo "$LINE"|sed 's/^:\([^!]*\)![^ ]* \(QUIT\|JOIN\|PART\).*$/\2 \1/')"
	name="$(echo "$LINE"|sed 's/^:\([^!]*\)![^ ]* .*$/\1/')"
	echo -n "$(date +%Y-%m-%dT%H:%M:%S) *** $(echo "$action"|cut -d' ' -f2-) " >> "${logdir}/${logchan}.log"
	action="$(echo "$action"|cut -d' ' -f1)";

	case $action in
		"QUIT"|"PART")
			echo "est parti" >> "${logdir}/${logchan}.log";;
		"JOIN")
			echo "s'est connecté" >> "${logdir}/${logchan}.log";
			irc_back="$name";
			irc_user="$name";
			log_last;;
		*)
			;;
	esac
}

# Le plus important: la fonction qui est derrière la commande !history
# Permet de savoir ce qui s'est dit juste avant qu'on arrive.
# Il vaut mieux éviter d'envoyer trop de lignes, à moins d'aimer se faire kick
# pour avoir floodé…
log_last()
{
	local A=" ";

	send "PRIVMSG $irc_back :Voilà ce qu'il s'est passé ces 10 dernières lignes, $irc_user";
	
	tail -n 10 "$logdir/${logchan}.log" | while [ "$A" != "" ]; do
		read A;
		[ "$A" != "" ] && {
			send_sec "PRIVMSG $irc_back :${A}";
			sleep 0.1;
		}
	done
}

[ -d "$logdir" ] || mkdir -p "$logdir";
