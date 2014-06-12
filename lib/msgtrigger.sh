#!/usr/bin/env false

liblist+=("msgtrigger");
HOOKS["msg_received"]+="parse_triggers;";

config_trigger="$global_confdir/trigger.cfg"

[ -f "$config_trigger" ] || touch "$config_trigger"
source $config_trigger;

parse_triggers()
{
	for i in "${!trigger_table[@]}" ; do
		[ $(echo "${irc_msg}"|grep "${i}"|wc -l) -eq 1 ] && eval "${trigger_table[$i]}";
	done
	return;
}
