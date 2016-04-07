#/bin/bash
COVERAGE=coverage
$COVERAGE erase

for file in test_*.py; do
    echo $file;
    $COVERAGE run $file;
    done

SUMATRA_SRC=$HOME/sumatra/sumatra_dev_fix_tests/sumatra
echo $SUMATRA_SRC
$COVERAGE report $SUMATRA_SRC/*.py  $SUMATRA_SRC/*/*.py $SUMATRA_SRC/*/*/*.py ./test_*.py
$COVERAGE annotate $SUMATRA_SRC/*.py  $SUMATRA_SRC/*/*.py $SUMATRA_SRC/*/*/*.py
