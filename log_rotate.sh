#!/usr/bin/env bash

params()
{
	declare -Ag LOGDIR LOGARCHDIR LOGBASENAME NB_ROTATIONS

	LOGDIR=/home/berry-punch
	LOGARCHDIR=/home/berry-punch/old_logs
	LOGBASENAME=\#bronycub
	NB_ROTATIONS=4
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

	[ $(ls -1 "${LOGARCHDIR}"|wc -l) -gt ${NB_ROTATIONS} ] && {
		ls -1t "${LOGARCHDIR}"|sed -urne "$((${NB_ROTATIONS}+1)),\$p"|xargs xz -ze9
	}
}

params;
make_dirs;
base_rotation;
