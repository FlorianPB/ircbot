#!/usr/bin/env false

liblist+=("dico")
HOOKS["msg_received"]+="send_to_dico;";

python3 dic.py &
sleep 1;
dic_pid="$(cat /tmp/brain-dic.pid)"

send_to_dico()
{
	echo "$irc_user $irc_msg" | tr "[:upper:]ÉÈÊËÀÔöŒ" "[:lower:]éèêëàôÖœ" | sed "s@\([,'!?]\)@ \1 @@g;s@ \+@ @g" > /tmp/brain-dic.${dic_pid}.in
	cat /tmp/brain-dic.${dic_pid}.out
}
