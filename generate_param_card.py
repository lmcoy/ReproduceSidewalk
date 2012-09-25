#!/usr/bin/python

import argparse
import sys

def CharginoMass(m_gluino, m_lsp, r):
	"""Calculate mass of the chargino."""
	return m_lsp + r*(m_gluino-m_lsp)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--m_gluino', dest='m_gluino', type=float, required=True, help='gluino mass')
	parser.add_argument('--m_lsp', dest='m_lsp', type=float, required=True, help='LSP mass')
	parser.add_argument('--r', dest='r', type=float, required=True, help='specifies the chargino mass via m = m_lsp + r*(m_gluino - m_lsp).' )
	args = vars(parser.parse_args())
	
	m_gluino = args['m_gluino']
	m_lsp = args['m_lsp']
	m_chargino = CharginoMass(m_gluino, m_lsp, args['r'])

	for line in sys.stdin:
		line = line.replace("@M_GLUINO@", "%.8E" % m_gluino )
		line = line.replace("@M_LSP@", "%.8E" % m_lsp )
		line = line.replace("@M_CHARGINO@", "%.8E" % m_chargino )
		sys.stdout.write(line)

if __name__ == '__main__':
	main()
