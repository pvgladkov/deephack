set -e
set -o pipefail
set -u

export NGRAM_MODEL="/Users/ffuuugor/IdeaProjects/deephack/europarl.en.srilm"
export SRILM="/Users/ffuuugor/IdeaProjects/deephack_mine/srilm-1.7.2"

export HOME_DIR="/Users/ffuuugor/IdeaProjects/deephack/"
export SRC_DIR="$HOME_DIR/src/"
export MODEL_PATH="$HOME_DIR/model.bin"

export PYTHONPATH=$SRC_DIR
export LC_ALL="en_US.UTF-8"

dialogs_path=$1
output_path=$2

ppl_df="ppl_df.csv"
features="all_features.csv"
prelim_submit="pre_submit.csv"

echo "Making ngrams"
bash $HOME_DIR/make_ngrams.sh $dialogs_path $ppl_df

echo "Running feature extracting"
python -m turing.submit.make_features --input $dialogs_path --ppl $ppl_df --output $features

echo "Running HBO model"
python -m turing.submit.hbo --features $features --model $MODEL_PATH --output $prelim_submit

echo "Running post processing"
python -m model.rules_hbo --dialogs $dialogs_path --input $prelim_submit --output $output_path
