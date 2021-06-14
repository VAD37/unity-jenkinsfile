#!/usr/bin/env bash
set -e -x

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


function set_config(){
    sudo sed -i "s/^\($1\s*=\s*\).*\$/\1$2/" $CONFIG
}