ReproduceSidewalk
=================
These scripts are used to reproduce the plots in arXiv:1102.5338v2

Requirements
------------
* MadGraph5 (Pythia, PGS) tool chain
* python

Usage
-----
1. Create a p p -> gluino gluino process in MadGraph
2. Modify generate_events.sh (enter the path to MadGraph...)
3. use generate_events.sh to generate events (this may take a long time.).
4. Produce background processes
5. modify apply_cuts.py: add background processes in CalculateDeltaB, MadGraph path, model in ApplyCuts