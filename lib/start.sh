#!/usr/bin/env false
liblist+=("start");
HOOKS["connect"]+="identify; sleep 0.1; joinchannel;";

identify()
{
	local txt="$1";
	while [ $(echo "$txt"|grep ":\*\*\* Checking Ident"|wc -l) -eq 0 ]; do
		sleep 0.1;
		txt="$(read_line_outbuffer_wait)";
	done

	msg "Starting authentication";
	send "USER ${NICK} ${HOST} ${SRVNAME} :Berry-Punch";
	sleep 1;
	send "NICK ${NICK}";

	txt="$(read_line_outbuffer_wait)";
	while [ $(echo "$txt"|grep "This nickname is registered"|wc -l) -lt 1 ] ; do
		sleep 0.1;
		txt="$(read_line_outbuffer_wait)";
	done
	msg "Received password invite from NickServ. Logging in…";
	send "PRIVMSG NickServ :IDENTIFY ${NICK} ${PASSW}";

	txt="$(read_line_outbuffer_wait)";
	if [ $(echo "$txt"|grep "You are now identified"|wc -l) -eq 1 ]; then
		msg "Successfuly identified to NickServ service.";
	fi
}
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
