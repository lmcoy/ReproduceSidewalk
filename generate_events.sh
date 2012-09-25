

# path to madgraph
MADGRAPH_PATH=/home/lo/Source/testmad/MadGraph5_v1_4_7
MODEL_PATH=SIMPLIFIED_GLUINO_PRODUCTION

# Card templates for madevent
PARAM_CARD_TEMPLATE=param_card_template.dat
PYTHIA_CARD_TEMPLATE=pythia_card_template.dat
ME_CONFIG_TEMPLATE=me5_configuration_template.txt 

M_GLUINO=400
M_LSP=200
# use this madevent configuration
cp $ME_CONFIG_TEMPLATE $MADGRAPH_PATH/$MODEL_PATH/Cards/me5_configuration.txt

# use different gluino,lsp masses
for M_GLUINO in {100..900..200}
do
	for ((M_LSP=100 ; M_LSP < $M_GLUINO; M_LSP+=200 ))
	do
		# use specific pythia card: IMSS(22)=24 should be in it to read in the decay tables from slha file
		cp $PYTHIA_CARD_TEMPLATE $MADGRAPH_PATH/$MODEL_PATH/Cards/pythia_card.dat
		# insert the gluino, lsp and chargino mass into the param_card
		cat $PARAM_CARD_TEMPLATE | python generate_param_card.py --m_gluino $M_GLUINO --m_lsp $M_LSP --r 0.5 > $MADGRAPH_PATH/$MODEL_PATH/Cards/param_card.dat
		# generate events
		$MADGRAPH_PATH/$MODEL_PATH/bin/generate_events "mgluino${M_GLUINO}_mlsp${M_LSP}" --laststep=pgs -f --multicore
	done
done

