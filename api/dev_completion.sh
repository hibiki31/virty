function vtc() {
  python3 tests/test_command.py $@
}

### 補完関数。
_vtc(){
  COMPREPLY=( $( \
      compgen -W "show-node show-task show-vmshow-node show-task show-vm show-user" \
              ${COMP_WORDS[COMP_CWORD]} \
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