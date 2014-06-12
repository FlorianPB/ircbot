#!/usr/bin/env false

liblist+=("admin");
HOOKS["cmd_received"]+="admin_flags;"

conf_admin="$global_confdir/admin.cfg";

admin_flags()
{
	[ $(echo "$LINE"|grep "JOIN"|wc -l) -eq 0 ] && return;
	local flags;
	local user_=$(echo "${LINE}"|sed 's|^:\([^!]*\)!.*$|\1|');
	msg "$user_ joined ! Applying flags…"
	touch "$conf_admin";

	flags="$(grep "^${user_}=" $conf_admin|cut -d= -f2)"
	if [ "$flags" != "" ] ; then
		send "MODE #bronycub ${flags} ${user_}"
	fi
}
admin_getflag()
{
	local user_="$1";
	if [ "$user_" == "" ]; then
		send "PRIVMSG $irc_back :Paramètre requis: nom d'utilisateur"
		return;
	fi
	touch "$conf_admin";

	flags="$(grep "^${user_}=" "$conf_admin"|cut -d= -f2)"
	if [ "$flags" != "" ] ; then
		send "PRIVMSG $irc_back :${user_} a le(s) flag(s) : ${flags}"
	fi
}
admin_setflag()
{
	local user_="$2";
	local flags_="$1";
	if [ "$user_" == "" ] || [ "$flags_" == "" ]; then
		send "PRIVMSG $irc_back :Paramètres requis: flags, username"
		return;
	fi
	touch "$conf_admin"
	if [ $(grep "^$user_=" "$conf_admin"|wc -l) -gt 0 ]; then
		grep -v "^$user_=" "$conf_admin" > "$conf_admin".1
		mv "$conf_admin".1 "$conf_admin"
	fi
	echo "$user_=$flags_" >> $conf_admin;
	send "PRIVMSG $irc_back :Flags de $user_ modifiés en $flags_";
}
admin_modflag()
{
	local flags_="$1";
	local user_="$2";
	if [ "$flags_" == "" ]; then
		send "PRIVMSG $irc_back :Paramètres requis: flags, username"
		return;
	fi
	msg "$user_: Modified flags ($flags_)"
	send_sec "MODE #bronycub $flags_ $user_";
	send "PRIVMSG $irc_back :Flags de $user_ modifiés : $flags_";
}
admin_flagcmd()
{
	if [ "$1" == "" ]; then
		set -- "zzz"
	fi
	case "$1" in
		"get")
			shift;
			admin_getflag "${@}";;
		"set")
			shift;
			admin_setflag "${@}";;
		"mod")
			shift;
			admin_modflag "${@}";;
		*)
			admin_getflag "$irc_user";
			send "PRIVMSG $irc_back :Gère les flags user"
			send "PRIVMSG $irc_back :Options:"
			send "PRIVMSG $irc_back :- get <user>: récupère les flags de user"
			send "PRIVMSG $irc_back :- set <user> <flags>: modifie les flags de user"
			send "PRIVMSG $irc_back :- mod <user> <flag>: modifie les flags de user maintenant";;
	esac
}
