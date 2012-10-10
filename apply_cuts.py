import re
import subprocess
import math
import os
import sys

# path to lhcoanalysis binary (https://github.com/lmcoy/LHCOAnalysis)
lhcoanalysis='/home/lo/Devel/workspace/LHCOAnalysis/build/src/LHCOAnalysis'
# path to MadGraph
MADGRAPH_PATH='/home/lo/Source/testmad/MadGraph5_v1_4_7'
# convert cross section from pb to fb e.g. x = 1.0*pb = 1000.0 [fb] 
pb = 1000.0

def CalculateDeltaB(lumi):
	"""" Calcluates Delta B 2 sigma from backgrounds 
	
	Returns a dict with (jet_mult, met, ht) from cuts as key and Delta B 2sigma as entry.
	"""
	print ("Calculating number of background events:")
	N_bkg = {}
# specify which backgrounds are used
	models = []
	models.append( ("SIMPLIFIED_ttbar_matched_c", "sample2", 10.04*pb) )
	models.append( ("SIMPLIFIED_ttbar_matched_c", "sample1_correct", 85.56*pb) )
	models.append( ("SIMPLIFIED_ttbar_matched_c", "sample3", 2.881*pb) )
	models.append( ("SIMPLIFIED_wj_c", "sample1", 1.576*10000.0*pb) )
	models.append( ("SIMPLIFIED_wj_c", "sample2", 26.91*pb) )
	models.append( ("SIMPLIFIED_wj_c", "sample3", 5.071*pb) )
	models.append( ("SIMPLIFIED_zj_c", "sample1", 4913.0*pb) )
	models.append( ("SIMPLIFIED_zj_c", "sample2", 11.06*pb) )
	models.append( ("SIMPLIFIED_zj_c", "sample3", 2.008*pb) )
	models.append( ("SIMPLIFIED_wbb_c", "sample1", 160.8*pb) )
	models.append( ("SIMPLIFIED_wbb_c", "sample2", 0.1883*pb) )
	models.append( ("SIMPLIFIED_wbb_c", "sample3", 0.04301*pb) )
	models.append( ("SIMPLIFIED_zbb_c", "sample1", 239.8*pb) )
	models.append( ("SIMPLIFIED_zbb_c", "sample2", 0.1742*pb) )
	models.append( ("SIMPLIFIED_zbb_c", "sample3", 0.03333*pb) )
	models.append( ("SIMPLIFIED_bb_matched", "run_01", 2.306e8*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j11", 2.36e5*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j21", 485.2*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j12", 9.759e4*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j22", 1.373e4*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j32", 6.648*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j13", 6121*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j23", 345.9*pb) )
	models.append( ("SIMPLIFIED_jjjj", "j14", 186.7*pb) )
	for model in models:
		print ("  using background %s (%s) with sigma = %.1f fb" % (model[0],model[1],model[2]))
# number of events
		N = lumi*model[2]
		epsilon_list = []
# calculate cut efficiencies and store them in a list 
		for jmult in [2,3,4]:
			epsilons = applyMETHTcuts( '%s/%s/Events/%s/tag_1_pgs_events.lhco.gz' %(MADGRAPH_PATH,model[0],model[1]), jmult )
			epsilon_list.append(epsilons)

# calculate number of background events from efficiencies
		for epsilons in epsilon_list:
			for key in epsilons:
				prev = 0.0
				if key in N_bkg:
					prev = N_bkg[key]
				N_bkg[key] = prev + N*epsilons[key]


# calculate 2-sigma fluctuations for each cuts
	result = {}
	for key in N_bkg:
		result[key] = 2.0*math.sqrt( (0.3*N_bkg[key])**2 + N_bkg[key] )

	return result

def applyMETHTcuts(lhcofile, jmult):
	""" Does the MET and HT cuts.

        loops over different MET and HT cuts and returns a dict with the various epsilons.
	"""
	result = {}
	for met in range(100,600,200):
		for ht in range(met,1000,200):
			sys.stdout.write("\r    jet multiplicity = %d, MET > %f, HT > %f" %(jmult,met,ht) )
			sys.stdout.flush()
			epsilon = GetEpsilon( lhcofile, jmult, ht, met )
			result[(jmult,met,ht)] = epsilon 
	sys.stdout.write("\r")
	sys.stdout.write( " "*80 )
	sys.stdout.write( "\r" )
	sys.stdout.flush()
	return result

def GetEpsilon(filename,jmult,ht,met):
	""" Starts LHCOAnalysis and gets the epsilons """
	out = subprocess.check_output(["zcat %s | %s --jet_mult %d --min_ht %f --min_met %f | grep 'efficiency' | awk '{print $2}'" %(filename,lhcoanalysis,jmult,ht,met)],shell=True)
	epsilon = float(out)
	return epsilon

def ApplyCuts():
	print ("Applying cuts for simplified model:")
	model="SIMPLIFIED_GLUINO_PRODUCTION"
	dirlist = os.listdir('%s/%s/Events/' % (MADGRAPH_PATH,model) )
	result = {}
	for fname in dirlist:
# search for all simulated models
		masses = re.match( "mgluino([0-9]+)_mlsp([0-9]+)",fname )
		if masses:
			m_gluino = float(masses.group(1))
			m_lsp = float(masses.group(2))
			print ("  using m_gluino = %f, m_lsp = %f:" % (m_gluino, m_lsp))
			for jmult in [2,3,4]:
				eps_table = applyMETHTcuts('%s/%s/Events/%s/tag_1_pgs_events.lhco.gz' %(MADGRAPH_PATH,model,fname), jmult)
			result[(m_gluino,m_lsp)] = eps_table
	return result

	

if __name__ == '__main__':
	deltaB = CalculateDeltaB(1.0)
	print ("results from background:")
	for key in deltaB:
		print ("    jet mult = %d, MET > %6.1f, HT > %6.1f: %e" % (key[0], key[1], key[2], deltaB[key]))
	efficiencies = ApplyCuts()
	for masses in efficiencies:
		best_s = 1000000000000.0
		j = 0
		MET = 0.0
		HT = 0.0
		for cuts in efficiencies[masses]:
			dB = deltaB[cuts]
			eps = efficiencies[masses][cuts]
			s = 1000000000.0
			if eps != 0.0 and dB != 0.0:
				s = dB/eps
		#	if dB == 0.0 and eps != 0.0:
		#		print ("    warning: m_gluino = %f, m_lsp = %f: eps = %f and dB = %f" % (masses[0], masses[1], eps, dB))
			if s < best_s:
				best_s = s
				j = cuts[0]
				MET = cuts[1]
				HT = cuts[2]
		print ("m_gluino = %.1f m_lsp = %.1f s*B = %8.1f fb (jet_mult = %d, MET > %.1f, HT > %.1f) " % (masses[0], masses[1], best_s, j, MET, HT))
