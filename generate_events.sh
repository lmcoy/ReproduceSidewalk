

# path to madgraph
MADGRAPH_PATH=/home/lo/Source/testmad/MadGraph5_v1_4_7
# simplified models path
MODEL_PATH=SIMPLIFIED_GLUINO_PRODUCTION
# background paths
BG_TT_PATH=SIMPLIFIED_tt
BG_WJ_PATH=SIMPLIFIED_wj
BG_ZJ_PATH=SIMPLIFIED_zj
BG_ZBB_PATH=SIMPLIFIED_zbb
BG_WBB_PATH=SIMPLIFIED_wbb
BG_JJJJ_PATH=SIMPLIFIED_jjjj

# Card templates for madevent
PARAM_CARD_TEMPLATE=param_card_template.dat
PYTHIA_CARD_TEMPLATE=pythia_card_template.dat
RUN_CARD_TEMPLATE=run_card_template.dat
ME_CONFIG_TEMPLATE=me5_configuration_template.txt 

M_GLUINO=400
M_LSP=200
# use this madevent configuration
cp $ME_CONFIG_TEMPLATE $MADGRAPH_PATH/$MODEL_PATH/Cards/me5_configuration.txt

# use different gluino,lsp masses
for M_GLUINO in {100..900..150}
do
	for ((M_LSP=100 ; M_LSP < $M_GLUINO; M_LSP+=150 ))
	do
		# use specific pythia card: IMSS(22)=24 should be in it to read in the decay tables from slha file
		cp $PYTHIA_CARD_TEMPLATE $MADGRAPH_PATH/$MODEL_PATH/Cards/pythia_card.dat
		# copy run_card
		cp $RUN_CARD_TEMPLATE $MADGRAPH_PATH/$MODEL_PATH/Cards/run_card.dat
		# insert the gluino, lsp and chargino mass into the param_card
		cat $PARAM_CARD_TEMPLATE | python generate_param_card.py --m_gluino $M_GLUINO --m_lsp $M_LSP --r 0.5 > $MADGRAPH_PATH/$MODEL_PATH/Cards/param_card.dat
		# generate events
		$MADGRAPH_PATH/$MODEL_PATH/bin/generate_events "mgluino${M_GLUINO}_mlsp${M_LSP}" --laststep=pgs -f --multicore
	done
done

