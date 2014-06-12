#!/usr/bin/env false

liblist+=("irc_utils");
HOOKS["cmd_received"]+="ping_reply;"

format_msg()
{
	local _line="${1}";

	[ $(echo "${_line}"|grep "PRIVMSG"|wc -l) -eq 0 ] && return;
	irc_user="$(echo "${_line}"|sed 's|:\([^!]*\)!.*$|\1|')"
	irc_target="$(echo "${_line}"|sed 's|:[^!]*![^ ]* PRIVMSG \([^ ]*\) :.*$|\1|')"
	irc_msg="$(echo "${_line}"|sed 's|:[^!]*![^ ]* PRIVMSG [^ ]* :\(.*\)$|\1|'|tr "\15\12" ":"|sed 's|::$||')"

	irc_back="$irc_target"
	[ "${irc_target:0:1}" != "#" ] && irc_back="$irc_user";

	export irc_user irc_target irc_msg irc_back
}
ping_reply()
{
	[ "${LINE:0:5}" != "PING " ] && return;
	send "PONG ${LINE#PING :}";
}
msg()
{
	echo "[1;37m==> ${1}[0m"
}
send()
{
	echo "${1}" >> in_lnk
}
