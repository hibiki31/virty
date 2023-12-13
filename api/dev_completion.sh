function vtc() {
  python3 tests/test_command.py $@
}

### 補完関数。
_vtc(){
  COMPREPLY=( $( \
      tests/test_compreply.py $COMP_CWORD ${COMP_WORDS[@]} \
  ))
}
### 補完関数と関数の関連付け
complete -F _vtc vtc


function vtdb() {
  ./tests/dev.sh
}

function vttest() {
  ./tests/test.py 
}