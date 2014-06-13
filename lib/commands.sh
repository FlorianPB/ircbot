#!/usr/bin/env false

# Commandes utilisateur à lancer depuis le chat
# Auteur: Adrien Sohier (adriens33)

liblist+=("commands");
HOOKS["msg_received"]+="parse_message;";

# Correspondance commande ↔ fonction
declare -Ag cmdtable=(['stop']="stop_the_bot"
					 ['muffin']="do_smgth 'jette un muffin sur' \$args"
					 ['do']="do_smgth \"\$args\""
					 ['say']="say_smgth \"\$args\""
					 ['history']="log_last"
					 ['flag']="admin_flagcmd \$args"
					 ['reload']="reload_libs"
					 ['voice']="admin_flagcmd mod +v \$args"
					 ['devoice']="admin_flagcmd mod -v \$args"
					 ['welcome']="say_smgth \"Bienvenue sur le chat de BronyCUB, \$args ! Amuse-toi bien !\""
					 ['op']="admin_flagcmd mod +o \$args"
					 ['deop']="admin_flagcmd mod -o \$args"
					 ['help']="cmd_help \$args"
					 ['kick']="cmd_kick \$args"
					 ['list']="list_cmds");

# Droit d'accès à certaines commandes
# Si la commande n'est pas précisée ici, elle est considérée comme publique
declare -Ag cmdright=(['stop']="adriens33" ['flag']="adriens33 heuzef" ['reload']="adriens33"
					 ['voice']="adriens33 heuzef" ['devoice']="adriens33 heuzef" ['op']="adriens33 heuzef"
					 ["deop"]="adriens33 heuzef" ['kick']="adriens33 heuzef");
declare -Ag cmdwrong=();

# ---------- Settings ----------
# Caractère à placer au début d'une commande
# (ex !list)
cmd_char="!";

# ---------- Commands ----------
# Liste des commandes disponibles
list_cmds()
{
	local a="${!cmdtable[@]}"
	send "PRIVMSG $irc_back :Commandes disponibles :";
	send "PRIVMSG $irc_back :$a";
}

# Permet de kick quelqu'un
cmd_kick()
{
	local name reason;
	name="$1"; shift;
	reason="${@}";

	[ "$reason" != "" ] && reason=":${reason}";

	send_sec "KICK #bronycub $name ${reason}"
}

# Aide pour une commande
cmd_help()
{
	local cmd="$1"
	local helptext=();
	local cnt;

	[ "$cmd" == "" ] && {
		send "PRIVMSG $irc_back :Entrez help <commande> pour avoir de l'aide sur cette commande."
		return
	}
	case "$cmd" in
		"kick")	helptext=("Kicke (vire) quelqu'un du canal." "${cmd_char}kick <nom> [raison]")
			;;
		"stop")	helptext=("Stoppe le bot.")
			;;
		"muffin")	helptext=("Jette un muffin sur quelqu'un." "${cmd_char}muffin <user>")
			;;
		"welcome")	helptext=("Souhaite la bienvenue à quelqu'un" "${cmd_char}welcome <user>")
			;;
		"do")	helptext=("Effectue une action." "${cmd_char}do <quelque chose>")
			;;
		"say")	helptext=("Fait parler le bot." "${cmd_char}say <du texte>")
			;;
		"history")	helptext=("Affiche les 10 dernières lignes de l'historique.")
			;;
		"flag")		helptext=("Gère les flags user/canal." "flag: état de vos flags"
														   "flag get <user>: flags enregistrés pour user"
														   "flag set <flags> <user>: modifie les flags enregistrés de user en flags"
														   "flag mod <flags> [user]: modifie les flags actuels de user (ou du canal si pas d'user précisé)")
			;;
		"reload")	helptext=("Recharge le bot")
			;;
		"voice")	helptext=("Donne le flag +v à quelqu'un." "${cmd_char}voice <user>" "équivalent de ${cmd_char}flag mod +v <user>")
			;;
		"devoice")	helptext=("Sort le flag +v de quelqu'un." "${cmd_char}devoice <user>" "équivalent de ${cmd_char}flag mod -v <user>")
			;;
		"op")	helptext=("Donne les droits admins à quelqu'un." "${cmd_char}op <user>" "équivalent de ${cmd_char}flag mod +o <user>")
			;;
		"deop")	helptext=("Sort les droits admins de quelqu'un." "${cmd_char}deop <user>" "équivalent de ${cmd_char}flag mod -o <user>")
			;;
		"list")	helptext=("Liste les commandes utilisables.")
			;;
		*)	helptext=("Commande inconnue." "Essayez '${cmd_char}list'.")
			;;
	esac
	let cnt=0
	for i in "${helptext[@]}"; do
		send "PRIVMSG $irc_back :$i"
		let cnt++;
		# [ $(($cnt%5)) -eq 0 ] && sleep 1;
	done
}

# Arrête le bot (plus nécessaire depuis le commit 80f80e26)
stop_the_bot()
{
	send "PRIVMSG $irc_back :Bye $irc_user !";
	msg "Stopping server…";
	sleep 1;
	exitbot;
}
# Action sur le canal (/me)
do_smgth()
{
	local args="${@}"
	send_sec "PRIVMSG #bronycub :\x01ACTION ${args}\x01";
}
# Fait dire quelque chose au bot
say_smgth()
{
	local args="${@}"
	send "PRIVMSG #bronycub :${args}";
}

# ---------- Internals ----------
# (HOOK) parse les messages utilisateur pour extraire les commandes et leurs paramètres
parse_message()
{
	local cmd args;
	cmd="$(echo $irc_msg|cut -d' ' -f1)"
	args="${irc_msg#${cmd}}"

	# Supprime l'espace au début des arguments
	[ "${args:0:1}" == " " ] && args="${args:1}";

	# Pas de caractère de commande au début ? Ben c'est pas une commande alors.
	[ "${cmd:0:1}" == "${cmd_char}" ] || return;
	cmd="${cmd:1}";
	
	# Si vous n'avez pas le droit d'exécuter une commande, c'esst ici que le bot vous tape dessus.
	# Attention, au 4e essai il vous kickera.
	[ "${cmdright[$cmd]}" != "" ] && [ $(echo " ${cmdright[$cmd]} "|grep " $irc_user "|wc -l) -lt 1 ] && {
		let cmdwrong[$irc_user]++;
		case ${cmdwrong[$irc_user]} in
			1)
				send "PRIVMSG $irc_back :Je suis désolé $irc_user, mais je n'ai pas le droit de te laisser faire ça.";;
			2)
				send "PRIVMSG $irc_back :N'insiste pas, s'il te plaît, $irc_user…";;
			3)
				send "PRIVMSG $irc_back :Bon. $irc_user, prochaine tentative, je te vire. OKAY ??";;
			4)
				[ "${irc_back:0:1}" == "#" ] && {
					send "PRIVMSG $irc_back: Désolé, je t'avais prévenu $irc_user .";
					sleep 0.5;
					send "KICK $irc_back $irc_user :Punaise, il est casse-pieds lui…";
					let cmdwrong[$irc_user]=0;
				};;
		esac
		return;
	}

	# On exécute la commande ici
	if [ "${cmdtable[$cmd]}" != "" ]; then
		# args="$(echo "${args}"|sed "s|>|'&'|g;s|<|'&'|g;s|\;|'&'|g")"
		eval "${cmdtable[$cmd]}";
	fi
}
