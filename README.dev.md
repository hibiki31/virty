## フォルダ構成



| パス         | 言語   | 種別  | 用途                                           |
| ------------ | ------ | ----- | ---------------------------------------------- |
| .github      | yaml   | Dev   | マスターブランチのなどのイメージをビルド       |
| agent        | golang | Agent | 各ノードにインストールして利用、高速化やip操作 |
| api★         | python | API   | Fastapiで記述しているバックエンド              |
| feature      | python | Agent | 各ノードにインストールして利用nuiktaでビルド   |
| next★        | react  | Front | WEBUI                                          |
| nginx★       | conf   | Front | API、Next、Proxyなどを1つのパスにまとめる      |
| proxy★       | python | API   | VNC用のコンテナ                                |
| pylib★       | Python | Lib   | virtyパッケージとして利用、OpenAPIで自動生成   |
| vctl         | golang | CLI   | クライアント                                   |
| vctl_python★ | python | CLI   | クライアント                                   |
| web          | Vue    | Front | 旧UI                                           |

