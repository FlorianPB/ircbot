#!/usr/bin/env false

# Outils bien utiles sur l'irc
# Auteur: Adrien Sohier (adriens33)

liblist+=("irc_utils");
HOOKS["cmd_received"]+="ping_reply;"

# Récupération des infos d'un message: user, provenance, contenu du message
# et où répondre (en gros : c'est sur le canal ou en PV ?)
format_msg()
{
	local _line="${1}";

	[ $(echo "${_line}"|grep "PRIVMSG"|wc -l) -eq 0 ] && return;
	irc_user="$(echo "${_line}"|sed 's|:\([^!]*\)!.*$|\1|')"
	irc_target="$(echo "${_line}"|sed 's|:[^!]*![^ ]* PRIVMSG \([^ ]*\) :.*$|\1|')"
	irc_msg="$(echo "${_line}"|sed 's|:[^!]*![^ ]* PRIVMSG [^ ]* :\(.*\)$|\1|'|tr "\15\12" ":"|sed 's|::$||')"

	irc_back="$irc_target"
	[ "${irc_target:0:1}" != "#" ] && irc_back="$irc_user";

	# Ces variables sont utilisables dans n'importe quelle fonction venant juste après,
	# comme celles qui sont dans le hook msg_received par exemple.
	export irc_user irc_target irc_msg irc_back
}

# On me pingue ? Vaut mieux répondre sinon le bot va avoir des soucis de connexion…
ping_reply()
{
	# Le serveur envoie un identifiant (par ex :asimov.freenode.net)
	# que l'on doit inclure dans la réponse pour que le serveur sache
	# qu'il s'agit de la réponse à son ping et pas un pong au pif
	[ "${LINE:0:5}" != "PING " ] && return;
	send "PONG ${LINE#PING :}";
}

# Affiche un beau message coloré sur le terminal (utile pour les infos)
msg()
{
	echo "[1;37m==> ${1}[0m"
}

# Envoie une ligne de texte sur le serveur irc (bon, en fait dans le buffer d'envoi)
# Version sans les hoquettements de notre chère Berry.
send_sec()
{
	local string="$1";
	local after
	printf "$string\n" >> in_lnk

	# C'est une action ? On la met dans le log du canal alors !
	if [ "${string:0:7}" == "PRIVMSG" ]; then
		after="$(echo "$string"|sed 's|PRIVMSG [^ ]* :\(.*\)$|\1|')"
		if [ "${after:0:4}" == '\x01' ]; then
			echo "$(date +%Y-%m-%dT%H:%M:%S) * Berry-Punch $(echo "$after"|sed 's|\\x01ACTION ||;s|\\x01$||')" >> "${logdir}/${logchan}.log"
		fi
	fi
}

# Envoie une ligne de texte sur le serveur irc (bon, en fait dans le buffer d'envoi)
# Ici, le bot place un « *hic* » aléatoirement entre deux mots.
send()
{
	local before after
	local string="${@//\"/\\\"}";
	string="${string//}"

	# Berry dit quelque chose ? On le log dans le fichier de log du canal.
	if [ "${string:0:7}" == "PRIVMSG" ]; then
		before="$(echo "$string"|sed 's|\(PRIVMSG [^ ]* :\).*$|\1|')"
		after="$(echo "$string"|sed 's|PRIVMSG [^ ]* :\(.*\)$|\1|')"
		nb=$((1+$(echo "$after"|grep -o " "|wc -l)))
		nb=$((1+$RANDOM%$nb));
		after="$(echo "$after"|cut -d" " -f1-$nb) *hic* $(echo "$after"|cut -d" " -f$(($nb+1))-)"
		string="${before}${after}"

		echo "$(date +%Y-%m-%dT%H:%M:%S) <Berry-Punch> $after" >> "$logdir/${logchan}.log"
	fi

	# Et on envoie le texte ensuite (pour de vrai cette fois)
	send_sec "$string"
}
