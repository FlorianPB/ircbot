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

	echo "==> Starting Authentication…";
	echo "USER ${NICK} ${HOST} ${SRVNAME} :Berry-Punch" >> in_buffer;
	sleep 1;
	echo "NICK ${NICK}" >> in_buffer;

	txt="$(read_line_outbuffer_wait)";
	while [ $(echo "$txt"|grep "This nickname is registered"|wc -l) -lt 1 ] ; do
		sleep 0.1;
		txt="$(read_line_outbuffer_wait)";
	done
	echo "==> Received password invite from NickServ. Logging in…";
	echo "PRIVMSG NickServ :IDENTIFY ${NICK} ${PASSW}" >> in_buffer;

	txt="$(read_line_outbuffer_wait)";
	if [ $(echo "$txt"|grep "You are now identified"|wc -l) -lt 1 ]; then
		echo "==> Successfuly identified to NickServ service.";
	fi
}
joinchannel()
{
	echo "==> Joining #bronycub";
	echo "JOIN #bronycub" >> in_buffer;
	sleep 1;

	nb=$(cat in_buffer|wc -l);
	idx=$(cat $IN_IDX);

	echo "==> Parsing welcome messages";
	while [ $idx -lt $nb ] ; do
		let idx++;
		echo -n $idx > $IN_IDX;
	done;

	echo "==> Done. I'm now fully operationnal.";
	echo 'PRIVMSG #bronycub :Salut tout le monde !' >> in_buffer;
}
exitbot()
{
	echo "PART #bronycub :Bye bye :)" >> in_buffer;
	sleep 1;
	echo "QUIT :bye" >> in_buffer;
	sleep 1;
	rm pidfile;
	exit 0;
}
