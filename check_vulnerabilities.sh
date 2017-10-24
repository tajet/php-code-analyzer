#!/bin/bash

grep -n -E '(m(y|s)sqli?)(_db)?_query ?\(.*\$_(GET|POST).*\)' -r $1 | awk -F ':' '{print "filename: "$1"\nline "$2": "$3"\n"}';
grep -n -E 'mssql_bind ?\(.*\$_(GET|POST).*\)' -r $1 | awk -F ':' '{print "filename: "$1"\nline "$2": "$3"\n"}';
grep -n -E '(oci|ora)_parse ?\(.*\$_(GET|POST).*\)' -r $1 | awk -F ':' '{print "filename: "$1"\nline "$2": "$3"\n"}';
grep -n -E 'odbc_(prepare|exec(ute)?) ?\(.*\$_(GET|POST).*\)' -r $1 | awk -F ':' '{print "filename: "$1"\nline "$2": "$3"\n"}';
