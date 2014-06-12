#!/usr/bin/env false

liblist+=("commands");
HOOKS["msg_received"]+="parse_message;";

declare -A cmdtable=(['stop']="stop_the_bot"
					 ['muffin']="do_smgth 'jette un muffin sur ' \$args"
					 ['do']="do_smgth \"\$args\""
					 ['say']="say_smgth \"\$args\""
					 ['history']="log_last"
					 ['flag']="admin_flagcmd \$args"
					 ['list']="list_cmds");
declare -A cmdright=(['stop']="adriens33" ['flag']="adriens33");
declare -A cmdwrong=();

# ---------- Settings ----------
cmd_char="@";

# ---------- Commands ----------
list_cmds()
{
	local a="${!cmdtable[@]}"
	send "PRIVMSG $irc_back :Commandes disponibles :";
	send "PRIVMSG $irc_back :$a";
}
stop_the_bot()
{
	send "PRIVMSG $irc_back :Bye $irc_user !";
	msg "Stopping server…";
	sleep 1;
	exitbot;
}
do_smgth()
{
	local args="${@}"
	send "PRIVMSG #bronycub :\x01ACTION ${args}\x01";
}
say_smgth()
{
	local args="${@}"
	send "PRIVMSG #bronycub :${args}";
}

# ---------- Internals ----------
parse_message()
{
	local cmd args;
	cmd="$(echo $irc_msg|cut -d' ' -f1)"
	args="${irc_msg#${cmd}}"
	[ "${args:0:1}" == " " ] && args="${args:1}";

	[ "${cmd:0:1}" == "${cmd_char}" ] || return;
	cmd="${cmd:1}";
	
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

	if [ "${cmdtable[$cmd]}" != "" ]; then
		# args="$(echo "${args}"|sed "s|>|'&'|g;s|<|'&'|g;s|\;|'&'|g")"
		eval "${cmdtable[$cmd]}";
	fi
}
