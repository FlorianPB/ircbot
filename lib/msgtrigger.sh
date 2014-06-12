#!/usr/bin/env false

liblist+=("msgtrigger");
HOOKS["msg_received"]+="parse_triggers;";

config_trigger="$global_confdir/trigger.cfg"

[ -f "$config_trigger" ] || touch "$config_trigger"

parse_triggers()
{
}
