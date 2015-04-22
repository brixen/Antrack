#!/bin/bash

#PBS -l nodes=1:ppn=24,walltime=24:00:00,pmem=700mb
#PBS -N struck_filter

cd /udrive/student/ibogun2010/Research/Code/Antrack/build/bin/

nNodes=1
datasetSaveLocation="/udrive/student/ibogun2010/Research/Results"
nThreads=$((${nNodes}*24))



echo "b: ${b}"
echo "P: ${P_param}"
echo "Q: ${Q}"
echo "R: ${R}"
echo "kernel: ${kernel}"
echo "feature: ${feature}"
echo "filter: ${filter}"
./struck_filter_experiments --tmpSaveLocation=${datasetSaveLocation} --filter=${filter} --nThreads=${nThreads} --b=${b} --P=${P_param} --Q=${Q} --R=${R} --feature=${feature} --kernel=${kernel} --prefix=${prefix}