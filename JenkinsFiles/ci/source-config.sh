#!/usr/bin/env bash
set -e

# source here mean take all cfg file and turn them into variable use in this script
# .cfg must be in format var=value   . No space between

parentdir="$(dirname "$BASH_SOURCE")"
parentdir2="$(dirname "$parentdir")"
config=$parentdir2/config.cfg
source $config
#source config.cfg
while read v; do
    case $v in
        '#'* | _*) continue;;
        *) n=${v%%=*}
            export $n="${!n}";;
            #echo "Value of $n is ${!n}" ;;
    esac
done <"$config"
