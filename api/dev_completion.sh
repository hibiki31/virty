function virty() {
  python3 tests/test_command.py $@
}

### 補完関数。
_virty(){
  COMPREPLY=( $( \
      tests/test_compreply.py $COMP_CWORD ${COMP_WORDS[@]} \
  ))
}
### 補完関数と関数の関連付け
complete -F _virty virty


function virty-dev() {
  ./tests/dev.sh
}

function virty-test() {
  ./tests/test.py 
}