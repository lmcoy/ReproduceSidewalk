ReproduceSidewalk
=================
These scripts are used to reproduce the plots in arXiv:1102.5338v2

Requirements
------------
* MadGraph5 (Pythia, PGS) tool chain
* python

Usage
-----
1. Insert MadGraph5 commands in templates/me5_input.txt
2. Modify config/generate_events.config
3. use generate_events.sh config/generate_events.config to generate events (this may take a long time.).
4. Produce background processes
5. modify apply_cuts.py: add background processes in CalculateDeltaB, MadGraph path, model in ApplyCuts
