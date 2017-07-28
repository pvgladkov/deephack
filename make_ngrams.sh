set -u
set -o pipefail
set -e

export NGRAM_MODEL="/Users/ffuuugor/IdeaProjects/deephack/europarl.en.srilm"
export SRILM="/Users/ffuuugor/IdeaProjects/deephack_mine/srilm-1.7.2"

python src/turing/submit/flatten.py -d $1 -o df.csv -t sentences

echo "logprob,ppl" > ppl_scores
$SRILM/bin/macosx/ngram -lm $NGRAM_MODEL -ppl sentences -debug 1 | fgrep logprob | awk '{print $4,$6}' | tr ' ' ',' >> ppl_scores
lines=`wc -l ppl_scores | awk '{print $1}'`
lines=$(( $lines - 1 ))

cat ppl_scores | head -n $lines > ppl_scores2

paste df.csv ppl_scores2 | tr '\t' ',' > ppl_df.csv
