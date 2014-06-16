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

	[ $(ls -1 "${LOGARCHDIR}/*.log"|wc -l) -ge ${NB_ROTATIONS} ] && {
		archivedate="$(date +%Y%m%d)"
		tar -cf "${LOGARCHDIR}/\#bronycub.week-${archivedate}.tar" $(ls -1t "${LOGARCHDIR}/*.log")
		xz -ze9 "${LOGARCHDIR}/\#bronycub.week-${archivedate}.tar"
		rm "${LOGARCHDIR}/*.log"
	}
}

params;
make_dirs;
base_rotation;
