#!/bin/bash
/usr/bin/mysql -h ${1} -u ${2} -p${3}<< eof
${4}
eof
