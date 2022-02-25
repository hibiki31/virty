# Virty

### Node

- 対応OS
  - Ubuntu
  - CentOS

### Network

- OVSでVLAN対応
- Internal対応

### Storage

- 今のところPosixだけ対応
- 現在使っている容量とMAX値を算出

### Image

- どのVMが所有しているかを把握

### VM

- Cloud-init対応したいよね

### User

- Adminグループにいると特権操作が可能
  - チケットを通さずにリソースを使える
  - ノードの追加作業など

### Group

- Unixのユーザとグループの簡易版
  - 操作できるかYes or Noのみ
- 例
  - VMがUser01所有でGroup01だった場合
  - User01とGroup01は同じ操作ができる

### Resource

- プールのような概念
- Resourceで定義するとそこに作ったVMは同じものが得られる
- ネットワークが同じでCPU,RAM,Storageの性能は問わない
- CPUやRAM,ストレージが厳密なリソースなど

### Ticket

- Resourceから切り出して定義される
- ユーザに同じ物を複数割り当て可能
- 例
  - 3VM, 8GB, 8CPU
  - 無制限も可能
  - ネットワークはリソースで固定だから決められない



