#!/usr/bin/env bash

params()
{
	declare -Ag LOGDIR LOGARCHDIR LOGBASENAME NB_ROTATIONS

	LOGDIR=/home/berry-punch
	LOGARCHDIR=/home/berry-punch/old_logs
	LOGBASENAME=\#bronycub
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
