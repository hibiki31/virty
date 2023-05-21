function vc() {
  python3 tests/test.py
}

### 補完関数。
_vc(){
  COMPREPLY=( $( \
      compgen -W "show-node show-task show-vmshow-node show-task show-vm" \
              ${COMP_WORDS[COMP_CWORD]} \
  ))
}
### 補完関数と関数の関連付け
complete -F _vc vc