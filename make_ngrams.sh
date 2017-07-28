set -u
set -o pipefail
set -e

export NGRAM_MODEL="/Users/ffuuugor/IdeaProjects/deephack/europarl.en.srilm"
export SRILM="/Users/ffuuugor/IdeaProjects/deephack_mine/srilm-1.7.2"

dialogs=$1
out=$2

python -m turing.submit.flatten -d $dialogs -o df.csv -t sentences

echo "logprob,ppl" > ppl_scores
$SRILM -lm $NGRAM_MODEL -ppl sentences -debug 1 | fgrep logprob | awk '{print $4,$6}' | tr ' ' ',' >> ppl_scores
lines=`wc -l ppl_scores | awk '{print $1}'`
lines=$(( $lines - 1 ))

cat ppl_scores | head -n $lines > ppl_scores2

paste df.csv ppl_scores2 | tr '\t' ',' > $out

rm ppl_scores
rm ppl_scores2
rm sentences
