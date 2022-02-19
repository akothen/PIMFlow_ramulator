#!/bin/bash

for f in $1/*; do
  g="$(basename "$f")";
  if [[ $g == Conv* ]] || [[ $g == GlobalAveragePool* ]]; then
    #echo $f;
    ../ramulator ../configs/HBM-config.cfg --mode=dram $f | grep Cycle | sed -r 's/Cycle\s([0-9]+)/\1/'
  fi
done
  
