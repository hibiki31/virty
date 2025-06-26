# Expoter

VirtyはPrometheus向けのメトリクスとして以下を提供します。

- WebダッシュボードのIP/metrics
  - タスクの実施状況
  - メモリの総予約量
  - コア数の総予約量
  - ノードの数

仮想マシンごとのメトリクスは以下のOSSを組み合わせることで実現します。
[inovex GmbH](https://github.com/inovex)に感謝します。

[inovex/prometheus-libvirt-exporter](https://github.com/inovex/prometheus-libvirt-exporter)

## ノードへのExpoterインストール

[Githubのリリースページ](https://github.com/inovex/prometheus-libvirt-exporter/releases)にアクセスします。
最新のイメージIDをコピーします。

```bash
mkdir prometheus-libvirt-exporter
cd prometheus-libvirt-exporter
```

`compose.yaml`を作成します。

```yaml
services:
  expoter:
    image: ghcr.io/inovex/prometheus-libvirt-exporter:2.1.1-amd64
    volumes:
      - /var/run/libvirt/libvirt-sock-ro:/var/run/libvirt/libvirt-sock-ro:ro
    ports:
      - 9177:9177
    restart: always
```

!!! note
  `docker run --rm ghcr.io/inovex/prometheus-libvirt-exporter:2.1.1-amd64 -h`でオプションを確認できます。

```bash
docker compose up -d
```

## Prometheusに設定を追加

- 192.168.10.1はノードのIPです
- 192.168.10.200はvirtyのIPです

!!! note
    上記のIPは同じとなるケースもあります

```yaml
  - job_name: 'libvirt'
    scrape_interval: 10s
    metrics_path: /metrics
    static_configs:
      - targets:
        - '192.168.10.1:9177'
  - job_name: 'virty-fastapi'
    scrape_interval: 10s
    metrics_path: /api/metrics-fastapi
    static_configs:
      - targets:
        - '192.168.10.200:8765'
  - job_name: 'virty-api'
    scrape_interval: 10s
    metrics_path: /api/metrics
    static_configs:
      - targets:
        - '192.168.10.200:8765'
```

Grafanaで可視化を行いたい場合、以下のダッシュボードを利用します。

https://grafana.com/grafana/dashboards/20737-libvirt-dashboard/

!!! note
  このダッシュボードは以下のIssueで議論されている通り、貢献者のPR待ちのステータスです。仮であり、公式のものではないことに注意が必要です。
  https://github.com/inovex/prometheus-libvirt-exporter/issues/17


!!! warning
  virty関連のダッシュボードは作成中です。