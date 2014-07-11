#!/usr/bin/env bash

#cat old_logs/#bronycub* \#bronycub.log|sort -n|sed "s@\(\[1;37m\|F[lL]ushing\).*\[0m@@g"|grep "http"|sed "s@^ *\([0-9\-]*T[0-9:]*\).*\(https\?://[^ \$]*\).*\$@\1 <a href=\"\2\">\2</a>@g"|sed "s@\$@<br/>@g" > links.txt
cat \#bronycub.log|sort -n|sed "s@\(\[1;37m\|F[lL]ushing\).*\[0m@@g"|grep "http"|sed "s@^ *\([0-9\-]*T[0-9:]*\).*\(https\?://[^ \$]*\).*\$@\1 <a href=\"\2\">\2</a>@g"|sed "s@\$@<br/>@g" >> links.txt
