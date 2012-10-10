#!/bin/bash

if [ -z $1 ]; then
	echo "error: no config file: use bash generate_events.sh config/generate_events.config"
	exit 1
fi

configfile=$1
configfile_secured='/tmp/config_sec.config'

# check that the config file contains variable declarations only
if egrep -q -v '^#|^[^ ]*=[^;]*' "$configfile"; then
	echo "Config file unclean, cleaning it..." >&2
	egrep '^#|^[^ ]*=[^;&]*' "$configfile" > "$configfile_secured"
	configfile="$configfile_secured"
fi

# read in config file
source "$configfile"

#------------------------------------------------------------------------------
#- Check parameters from config file ------------------------------------------
#------------------------------------------------------------------------------

# check MADGRAPH_PATH
if [ -z ${MADGRAPH_PATH} ]; then
	echo "error: MADGRAPH_PATH is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ ! -d "$MADGRAPH_PATH" ]; then
	echo "error: MadGraph directory not found! There is no directory MADGRAPH_PATH=\"$MADGRAPH_PATH\"" >&2
	exit 1
fi

if [ ! -f "$MADGRAPH_PATH/bin/mg5" ]; then
	echo "error: MadGraph executable is not in the bin directory of MADGRAPH_PATH=\"$MADGRAPH_PATH\"" >&2
	exit 1
fi

# check OUTPU
if [-z ${OUTPUT} ]; then
	echo "error: OUTPUT is not set in the config file \"$1\"." >&2
	exit 1
fi

# check MG5_INPUT
if [ ! -f "$MG5_INPUT" ]; then
	echo "error: MG5_INPUT: file \"${MG5_INPUT}\" does not exist." >&2
	exit 1
fi

# check template files
if [ ! -f "$ME_CONFIG_TEMPLATE" ]; then
	echo "error: ME_CONFIG_TEMPLATE: file \"${ME_CONFIG_TEMPLATE}\" does not exist." >&2
	exit 1
fi

if [ ! -f "$PARAM_CARD_TEMPLATE" ]; then
	echo "error: PARAM_CARD_TEMPLATE: file \"${PARAM_CARD_TEMPLATE}\" does not exist." >&2
	exit 1
fi

if [ ! -f "$RUN_CARD_TEMPLATE" ]; then
	echo "error: RUN_CARD_TEMPLATE: file \"${RUN_CARD_TEMPLATE}\" does not exist." >&2
	exit 1
fi

if [ ! -f "$PYTHIA_CARD_TEMPLATE" ]; then
	echo "error: PYTHIA_CARD_TEMPLATE: file \"${PYTHIA_CARD_TEMPLATE}\" does not exist." >&2
	exit 1
fi

# check MODEL_PATH
if [ -z ${MODEL_PATH} ]; then
	echo "error: MODEL_PATH is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -d "${MADGRAPH_PATH}/${MODEL_PATH}" ]; then
	echo "error: MODEL_PATH=\"${MODEL_PATH}\" already exists in MADGRAPH_PATH=\"${MADGRAPH_PATH}\"" >&2
	exit 1
fi

# check gluino masses
if [ -z ${M_GLUINO_MIN} ]; then
	echo "error: M_GLUINO_MIN is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -z ${M_GLUINO_MAX} ]; then
	echo "error: M_GLUINO_MAX is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -z ${M_GLUINO_STEP} ]; then
	echo "error: M_GLUINO_STEP is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -z ${M_LSP_MIN} ]; then
	echo "error: M_LSP_MIN is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -z ${M_LSP_STEP} ]; then
	echo "error: M_LSP_STEP is not set in the config file \"$1\"." >&2
	exit 1
fi

if [ -z ${RVALUE} ]; then
	echo "error: RVALUE is not set in the config file \"$1\"." >&2
	exit 1
fi

if (($M_GLUINO_MIN > $M_GLUINO_MAX - $M_GLUINO_STEP )); then
	echo "error: M_GLUINO_MIN is > M_GLUINO_MAX - M_GLUINO_STEP." >&2
	exit 1
fi

#if (( $RVALUE > 1.0 )); then
#	if (( $RVALUE < 0.0 )); then
#		echo "error: RVALUE is not in [0,1]." >&2
#		exit 1
#	fi
#fi

#------------------------------------------------------------------------------
#- Run MadGraph ---------------------------------------------------------------
#------------------------------------------------------------------------------

# create output dir
mkdir -p $OUTPUT

# remove any output cmd from MG5_INPUT and add MODEL_PATH as output.
egrep --invert-match '^output' "${MG5_INPUT}" > /tmp/mg5input.txt
echo "output $OUTPUT/${MODEL_PATH}" >> /tmp/mg5input.txt

# run mg5
$MADGRAPH_PATH/bin/mg5 /tmp/mg5input.txt


#------------------------------------------------------------------------------
#- Run MadEvent for each model ------------------------------------------------
#------------------------------------------------------------------------------

# use this madevent configuration
cp $ME_CONFIG_TEMPLATE $OUTPUT/$MODEL_PATH/Cards/me5_configuration.txt

# use different gluino,lsp masses
for (( M_GLUINO=$M_GLUINO_MIN; M_GLUINO < $M_GLUINO_MAX; M_GLUINO+=$M_GLUINO_STEP ))
do
	for (( M_LSP=$M_LSP_MIN ; M_LSP < $M_GLUINO; M_LSP+=$M_LSP_STEP ))
	do
		# use specific pythia card: IMSS(22)=24 should be in it to read in the decay tables from slha file
		cp $PYTHIA_CARD_TEMPLATE $OUTPUT/$MODEL_PATH/Cards/pythia_card.dat
		# copy run_card
		cp $RUN_CARD_TEMPLATE $OUTPUT/$MODEL_PATH/Cards/run_card.dat
		# insert the gluino, lsp and chargino mass into the param_card
		cat $PARAM_CARD_TEMPLATE | python utils/generate_param_card.py --m_gluino $M_GLUINO --m_lsp $M_LSP --r $RVALUE > $OUTPUT/$MODEL_PATH/Cards/param_card.dat
		# generate events
		$OUTPUT/$MODEL_PATH/bin/generate_events "mgluino${M_GLUINO}_mlsp${M_LSP}" --laststep=pgs -f --multicore
	done
done

