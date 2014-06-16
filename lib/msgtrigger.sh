#!/usr/bin/env false

# Répond à certains messages des utilisateurs
# (par exemple « T'es bourrée → pas vrai »)
# Auteur: Adrien Sohier (adriens33)

liblist+=("msgtrigger");
HOOKS["msg_received"]+="parse_triggers;";

config_trigger="$global_confdir/trigger.cfg"

declare -gA trigger_table=();

[ -f "$config_trigger" ] || touch "$config_trigger"

# Ne cherchez pas les messages, c'est dans le fichier qui est sourcé ci-dessous.
source $config_trigger;

# On déclenche le ou les triggers si le message correspond à l'expression régulière
# renseignée.
parse_triggers()
{
	for i in "${!trigger_table[@]}" ; do
		[ $(echo "${irc_msg}"|grep -i "${i}"|wc -l) -eq 1 ] && eval "${trigger_table[$i]}";
	done
	return;
}
