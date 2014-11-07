#!/usr/bin/env bash

source config/SHBot.cfg

params()
{
	declare -Ag LOGDIR LOGARCHDIR LOGBASENAME NB_ROTATIONS

	LOGDIR=$(dirname "$0")
	LOGARCHDIR=${LOGDIR}/old_logs
	LOGBASENAME="${CHAN}"
	NB_ROTATIONS=7
}
make_dirs()
{
	[ -d "$LOGDIR" ] || mkdir "$LOGDIR"
	[ -d "$LOGARCHDIR" ] || mkdir "$LOGARCHDIR"
}
base_rotation()
{
	local i curlog archlog;

	curlog="${LOGDIR}/${LOGBASENAME}.log"
	archlog="${LOGARCHDIR}/${LOGBASENAME}.$(date +%Y%m%d).log"

	mv "${curlog}" "${archlog}"
	touch "${curlog}"
}

params;
make_dirs;
base_rotation;
