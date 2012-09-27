
import re
import commands
import math
import os

lhcoanalysis='/home/lo/Devel/workspace/LHCOAnalysis/build/src/LHCOAnalysis'
MADGRAPH_PATH='/home/lo/Source/testmad/MadGraph5_v1_4_7'
pb = 1000.0

def CalculateDeltaB(filename, cross_section, lumi):
	print "Calculating number of background events:"
	N = lumi*cross_section
	result = {}
	models = []
	models.append( ("SIMPLIFIED_tt", "run_04", 45.04*pb) )
	models.append( ("SIMPLIFIED_wj", "run_02", 1.45*10000.0*pb) )
	models.append( ("SIMPLIFIED_zj", "run_02", 4918.0*pb) )
	models.append( ("SIMPLIFIED_wbb", "run_02", 151.1*pb) )
	models.append( ("SIMPLIFIED_zbb", "run_02", 239.8*pb) )
	for model in models:
		print "  using background %s with sigma = %f fb" % (model[0],model[2])
		N = lumi*model[2]
		for jmult in range(2,5):
			for met in range(100,600,50):
				for ht in range(met,1200,50):
					epsilon = GetEpsilon( '%s/%s/Events/%s/tag_1_pgs_events.lhco.gz' %(MADGRAPH_PATH,model[0],model[1]), jmult, ht, met )
					prev = 0.0
					if (jmult,met,ht) in result:
						prev = result[(jmult,met,ht)]
					result[(jmult,met,ht)] = epsilon*N + prev

	for key in result:
		result[key] = 2.0*math.sqrt( (0.3*result[key])**2 + result[key] )

	return result


def GetEpsilon(filename,jmult,ht,met):
	out = commands.getoutput("zcat %s | %s --jet_mult %d --min_ht %f --min_met %f | grep 'efficiency' | awk '{print $2}'" %(filename,lhcoanalysis,jmult,ht,met))
	epsilon = float(out)
	return epsilon

def ApplyCuts():
	print "Applying cuts for simplified model:"
	model="SIMPLIFIED_GLUINO_PRODUCTION"
	dirlist = os.listdir('%s/%s/Events/' % (MADGRAPH_PATH,model) )
	result = {}
	for fname in dirlist:
		masses = re.match( "mgluino([0-9]+)_mlsp([0-9]+)",fname )
		if masses:
			m_gluino = float(masses.group(1))
			m_lsp = float(masses.group(2))
			eps_table = {}
			print "  using m_gluino = %f, m_lsp = %f:" % (m_gluino, m_lsp)
			for jmult in range(2,5):
				for met in range(100,600,50):
					for ht in range(met,1200,50):
						epsilon = GetEpsilon( '%s/%s/Events/%s/tag_1_pgs_events.lhco.gz' %(MADGRAPH_PATH,model,fname), jmult, ht, met )
						eps_table[(jmult,met,ht)] = epsilon
#						print "%d %f %f %f" % (jmult,met,ht,epsilon)
			result[(m_gluino,m_lsp)] = eps_table
	return result

	

if __name__ == '__main__':
	model="SIMPLIFIED_tt"
	deltaB = CalculateDeltaB('%s/%s/Events/run_01/tag_1_pgs_events.lhco.gz' %(MADGRAPH_PATH,model), 554.5*pb, 1.0)
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
			if s < best_s:
				best_s = s
				j = cuts[0]
				MET = cuts[1]
				HT = cuts[2]
		print "m_gluino = %f m_lsp = %f s*B = %f fb (jet_mult = %d, MET > %f, HT > %f) " % (masses[0], masses[1], best_s, j, MET, HT)
