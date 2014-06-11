#!/usr/bin/env bash

# ---------- PARAMÈTRES ----------
SERVER=chat.freenode.net
PORT=6667
# NICK=
# PASSW=
HOST=homer.art-software.fr
echo -n "User: "; read NICK;
echo -n "Pass: "; read -s PASSW;

IN_IDX=IN_IDX
OUT_IDX=OUT_IDX
declare -a liblist=();
declare -A HOOKS=(["line_received"]="" ["connect"]="" ["msg_received"]="" ["cmd_received"]="");

trap "exitbot" SIGINT

# --------- Procédures ----------
echo "==> Loading libraries…";
for i in lib/*.sh ; do
	source "$i";
done
echo "[2K[1G==> Libraries loaded"

# ---------- fonctions internes ----------
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
		[ $idx -ge 32768 ] && flush_buffer_in
	done
}
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
	[ $idx -ge 32768 ] && flush_buffer_out
}
read_line_outbuffer_wait()
{
	local idx;

	idx=$(cat $OUT_IDX);
	while [ -f pidfile ] && [ $(cat out_lnk|wc -l) -le $idx ] ; do
		sleep 0.1;
	done

	read_line_outbuffer;
}
flush_buffer_in()
{
	local cur new;
	cur="$(readlink -f in_lnk)";
	new="in_buffer.$(date +%s)";

	touch "$new";
	ln -svf "$new" "in_lnk"
	echo "0" > $IN_IDX;
	rm "$cur";
}
flush_buffer_out()
{
	local cur new;
	cur="$(readlink -f out_lnk)";
	new="out_buffer.$(date +%s)";

	touch "$new";
	ln -svf "$new" "out_lnk"
	echo "0" > $OUT_IDX;
	rm "$cur";
}
netlink()
{
	read_loop_inbuffer | nc ${SERVER} ${PORT} >> out_buffer;
}

# ---------- Main ----------
rm in_buffer out_buffer OUT_IDX IN_IDX; in_lnk out_lnk
ln -sv in_buffer in_lnk;
ln -sv out_buffer out_lnk;

touch in_lnk out_lnk;
echo -n "0" > $IN_IDX;
echo -n "0" > $OUT_IDX;
echo $$ > pidfile;

netlink &
echo "==> Started";
SRVNAME="";

while [ -f pidfile ]; do
	LINE="$(read_line_outbuffer_wait)";
	if [ "$SRVNAME" == "" ]; then
		echo "==> Looking for server name…";
		SRVNAME="$(echo "$LINE"|sed 's|^\(.*:\)\([a-zA-Z]*\.freenode\.net\)\(.*\)$|\2|')"
		echo "==> Got server name: ${SRVNAME}";
		eval "${HOOKS["connect"]}";
	fi
	eval ${HOOKS["line_received"]};
	
	irc_user="";
	irc_msg="$irc_user";
	irc_target="$irc_user";

	format_msg "${LINE}"
	if [ "$irc_user" != "" ] && [ "$irc_target" != "" ] && [ "$irc_msg" != "" ]; then
		echo "Message from $irc_user to $irc_target: '$irc_msg'"
		eval "${HOOKS["msg_received"]}"
	else
		echo "Received text:$LINE";
		eval "${HOOKS["cmd_received"]}"
	fi
done
rm IN_IDX OUT_IDX in_buffer.* out_buffer.* in_lnk out_lnk;
