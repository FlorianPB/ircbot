#!/usr/bin/env false

liblist+=("commands");
HOOKS["msg_received"]+="parse_message;";

declare -A cmdtable=(['stop']="stop_the_bot"
					 ['muffin']="do_smgth 'jette un muffin sur '"
					 ['do']="do_smgth"
					 ['say']="say_smgth"
					 ['history']="log_last"
					 ['list']="list_cmds");
declare -A cmdright=(['stop']="adriens33");
declare -A cmdwrong=();

# ---------- Settings ----------
cmd_char="@";

# ---------- Commands ----------
list_cmds()
{

	echo "PRIVMSG $irc_back :Commandes disponibles :" >> in_buffer;
	echo "PRIVMSG $irc_back :${!cmdtable[@]}" >> in_buffer;
}
stop_the_bot()
{
	echo "PRIVMSG $irc_back :Bye $irc_user !" >> in_buffer;
	echo "==> Stopping server…";
	sleep 1;
	exitbot;
}
do_smgth()
{
	echo -e "PRIVMSG #bronycub :\x01ACTION ${@}\x01" >> in_buffer;
}
say_smgth()
{
	echo -e "PRIVMSG #bronycub :${@}" >> in_buffer;
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
				echo "PRIVMSG $irc_back :Je suis désolé $irc_user, mais je n'ai pas le droit de te laisser faire ça." >> in_buffer;;
			2)
				echo "PRIVMSG $irc_back :N'insiste pas, s'il te plaît, $irc_user…" >> in_buffer;;
			3)
				echo "PRIVMSG $irc_back :Bon. $irc_user, prochaine tentative, je te vire. OKAY ??" >> in_buffer;;
			4)
				[ "${irc_back:0:1}" == "#" ] && {
					echo "PRIVMSG $irc_back: Désolé, je t'avais prévenu $irc_user ." >> in_buffer;
					sleep 0.5;
					echo "KICK $irc_back $irc_user :Punaise, il est casse-pieds lui…" >> in_buffer;
					let cmdwrong[$irc_user]=0;
				};;
		esac
		return;
	}

	if [ "${cmdtable[$cmd]}" != "" ]; then
		eval "${cmdtable[$cmd]} $args";
	fi
}
