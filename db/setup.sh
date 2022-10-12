#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

datadir="${1:-data/}"
if [ ! -d $datadir ] ; then
    echo "$datadir does not exist under $mybase"
    exit 1
fi

source ../.flaskenv
dbname=$DB_NAME

if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    dropdb $dbname
fi
createdb $dbname

for createSqlFile in $mybase/sqlCreate/*; do
    psql -af $createSqlFile $dbname
done

cd $datadir
for loadSqlFile in $mybase/sqlLoad/*; do
    psql -af $loadSqlFile $dbname
done
