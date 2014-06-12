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
send_sec()
{
	local string="$1";
	printf "$string\n" >> in_lnk
}
send()
{
	local before after
	local string="${@//\"/\\\"}";
	string="${string//}"
	if [ "${string:0:7}" == "PRIVMSG" ]; then
		before="$(echo "$string"|sed 's|\(PRIVMSG [^ ]* :\).*$|\1|')"
		after="$(echo "$string"|sed 's|PRIVMSG [^ ]* :\(.*\)$|\1|')"
		nb=$((1+$(echo "$after"|grep -o " "|wc -l)))
		nb=$((1+$RANDOM%$nb));
		after="$(echo "$after"|cut -d" " -f1-$nb) *hic* $(echo "$after"|cut -d" " -f$(($nb+1))-)"
		string="${before}${after}"
	fi
	send_sec "$string"
}
