#!/bin/bash

for infile in $*
do
   ncpdq -P upk $infile $infile
done
