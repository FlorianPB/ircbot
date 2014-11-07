#!/usr/bin/env bash

tail --follow=name --retry out_lnk 2>/dev/null|sed -u "s@^@[96m@g" &
tail --follow=name --retry in_lnk 2>/dev/null|sed -u "s@^@[91m@g"
