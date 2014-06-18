#!/usr/bin/env false

# Gère le démarrage du bot :
# Connexion, etc
# Auteur: Adrien Sohier (adriens33)

liblist+=("start");
HOOKS["connect"]+="identify; sleep 0.1; joinchannel;";

# Gère le processus d'identification sur le serveur IRC
# (nécessite un NickServ et un pseudo enregistré)
identify()
{
	local txt="$1";
	while [ $(echo "$txt"|grep ":\*\*\* Checking Ident"|wc -l) -eq 0 ]; do
		sleep 0.1;
		txt="$(read_line_outbuffer_wait)";
	done

	msg "Starting authentication";
	send_sec "USER ${NICK} ${HOST} ${SRVNAME} :Berry-Punch";
	sleep 1;
	send_sec "NICK ${NICK}";

	if [ $WAIT_AUTH -eq 1 ]; then
		txt="$(read_line_outbuffer_wait)";
		while [ $(echo "$txt"|grep "This nickname is registered"|wc -l) -lt 1 ] ; do
			sleep 0.1;
			txt="$(read_line_outbuffer_wait)";
		done
		msg "Received password invite from NickServ. Logging in…";
		send_sec "PRIVMSG NickServ :IDENTIFY ${NICK} ${PASSW}";

		txt="$(read_line_outbuffer_wait)";
		if [ $(echo "$txt"|grep "You are now identified"|wc -l) -eq 1 ]; then
			msg "Successfuly identified to NickServ service.";
		fi
	fi
}
# Permet de rejoindre un canal
joinchannel()
{
	msg "Joining #bronycub";
	send "JOIN #bronycub";
	sleep 1;

	nb=$(cat in_buffer|wc -l);
	idx=$(cat $IN_IDX);

	msg "Parsing welcome messages";
	while [ $idx -lt $nb ] ; do
		let idx++;
		echo -n $idx > $IN_IDX;
	done;

	msg "Done. I'm now fully operationnal.";
	send 'PRIVMSG #bronycub :Salut tout le monde !';

	# lancement du hic aléatoire en arrière-plan
	random_hic &
}
exitbot()
{
	send "PART #bronycub :Bye bye :)";
	sleep 1;
	send "QUIT :bye";
	sleep 1;
	rm pidfile;
	exit 0;
}
# Recharge les libs & la  config sans devoir relancer l'appli
reload_libs()
{
	liblist=()
	HOOKS=()
	# Source toutes les libs
	for i in lib/*.sh; do
		source "$i"
	done
	msg "Libraries reloaded :"
	for i in "${liblist[@]}"; do
		echo "- $i"
	done

	# On prévient que c'est fini
	send_sec "PRIVMSG $irc_user :Rechargement terminé."
}

# Envoie un 'hic' sur le canal
# en marquant un délai aléatoire
random_hic()
{
	local hic_delay;

	while [ -f pidfile ]; do
		hic_delay=$(($RANDOM%10))m
		sleep ${hic_delay};
		send_sec "PRIVMSG #bronycub :*hic* !";
	done
}
