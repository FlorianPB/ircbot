#!/usr/bin/env bash

# Fichier principal
# Auteur: Adrien Sohier (adriens33)

global_confdir="$(dirname "$0")/config"
source "$global_confdir/SHBot.cfg"

# Eh ben oui, le user/password est demandé au démarrage.
# J'allais quand même pas vous le donner hein ? XD
echo -n "User: "; read NICK;
echo -n "Pass: "; read -s PASSW;

# Fichiers pour les index des buffers d'entrée / sortie
IN_IDX=IN_IDX
OUT_IDX=OUT_IDX
declare -ga liblist=();
declare -gA HOOKS=(["line_received"]="" ["connect"]="" ["msg_received"]="" ["cmd_received"]="");

# Control-C ferme le bot proprement
trap "exitbot" SIGINT

# --------- Procédures ----------
# On source les scripts
for i in lib/*.sh ; do
	source "$i";
done
msg "Libraries loaded :"
for i in ${liblist[@]} ; do
	echo "- $i"
done

# ---------- fonctions internes ----------
# Lecture du buffer in en boucle (buffer à envoyer au serveur)
# En gros: tant que le fichier a autant de lignes que la position de l'index (IN_IDX), ça va.
# S'il y a différence, on envoie chaque ligne ajoutée et on met à jour l'index.
read_loop_inbuffer()
{
	local nb idx;
	while [ -f pidfile ]; do
		nb=$(cat in_lnk|wc -l);
		idx=$(cat $IN_IDX);
		while [ $idx -lt $nb ] ; do
			let idx++;
			echo -n $idx > $IN_IDX;
			sed -urne "${idx}p" in_lnk;
		done
		sleep 0.1;

		# Si le buffer est trop gros, on le vide.
		[ $idx -ge 100 ] && flush_buffer_in
	done
}

# La même chose que read_loop_inbuffer, sauf qu'on ne fait qu'une passe.
# (et que c'est sur la sortie du serveur)
read_line_outbuffer()
{
	local nb idx;
	idx=$(cat $OUT_IDX);

	nb=$(cat out_lnk|wc -l);
	if [ $idx -lt $nb ]; then
		let idx++;
		echo -n $idx > $OUT_IDX;
		sed -urne "${idx}p" out_lnk;
	fi

	# Vidage du buffer lorsqu'il est trop gros
	[ $idx -ge 100 ] && flush_buffer_out
}

# Attend qu'une ligne apparaîsse dans le buffer de sortie avant de retourner quelque chose
read_line_outbuffer_wait()
{
	local idx;

	idx=$(cat $OUT_IDX);
	while [ -f pidfile ] && [ $(cat out_lnk|wc -l) -le $idx ] ; do
		sleep 0.1;
	done

	read_line_outbuffer;
}

# Vidage du buffer d'entrée
# Cette magie marche car in_lnk est un lien qu'on met à jour puis on supprime l'ancien
# fichier qui n'est plus utilisé.
flush_buffer_in()
{
	# msg "Flushing input buffer"
	local cur new;
	cur="$(readlink -f in_lnk)";
	new="in_buffer.$(date +%s)";

	touch "$new";
	ln -sf "$new" "in_lnk"
	echo "0" > $IN_IDX;
	rm "$cur";
}

# idem que pour flush_buffer_in
flush_buffer_out()
{
	# msg "FLushing output buffer"
	local cur new;
	cur="$(readlink -f out_lnk)";
	new="out_buffer.$(date +%s)";

	touch "$new";
	ln -sf "$new" "out_lnk"
	echo "0" > $OUT_IDX;
	rm "$cur";
}

# Envoie les données dans le buffer de sortie (permet d'update le file handle au fur et à mesure
# et de  ne pas perdre la sortie au flush du buffer )
put_outputdata()
{
	while [ -f pidfile ]; do
		read -s LINE
		if ! [[ $LINE =~ ^( |	)*$ ]]; then
			echo "${LINE}" >> out_lnk;
		fi
	done
}

# Connexion entre les buffers et le serveur
# (merci netcat :D)
netlink()
{
	read_loop_inbuffer | nc ${SERVER} ${PORT} | put_outputdata;
}

# ---------- Main ----------
rm in_buffer* out_buffer* OUT_IDX IN_IDX in_lnk out_lnk
ln -sf in_buffer in_lnk;
ln -sf out_buffer out_lnk;

touch in_lnk out_lnk;
echo -n "0" > $IN_IDX;
echo -n "0" > $OUT_IDX;
echo "";
echo $$ > pidfile;

# On démarre la connexion
netlink &
msg "Started";
SRVNAME="";

while [ -f pidfile ]; do
	# Attente d'une ligne provenant du serveur
	LINE="$(read_line_outbuffer_wait)";

	if [ "$SRVNAME" == "" ]; then
		msg "Looking for server name…";
		SRVNAME="$(echo "$LINE"|sed 's|^\(.*:\)\([a-zA-Z]*\.freenode\.net\)\(.*\)$|\2|')"
		msg "Got server name: ${SRVNAME}";
		# HOOK: connexion attendue
		eval "${HOOKS["connect"]}";
	fi

	# HOOK: ligne de texte reçue
	eval ${HOOKS["line_received"]};
	
	irc_user="";
	irc_msg="$irc_user";
	irc_target="$irc_user";

	format_msg "${LINE}"
	if [ "$irc_user" != "" ] && [ "$irc_target" != "" ] && [ "$irc_msg" != "" ]; then
		echo "Message from $irc_user to $irc_target: '$irc_msg'"
		# HOOK: Message user/serveur reçu
		eval "${HOOKS["msg_received"]}"
	else
		echo "Received text:$LINE";
		# HOOK: ligne reçue (pas un message)
		eval "${HOOKS["cmd_received"]}"
	fi
done
rm IN_IDX OUT_IDX in_buffer.* out_buffer.* in_lnk out_lnk /tmp/brain-dic.pid;
