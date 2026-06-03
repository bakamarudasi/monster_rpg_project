# CCNA 実践ラボ — モンスターRPGを「到達ターゲット」にする

このリポジトリの Flask 製ゲームを **ネットワークの終端サーバ**に見立て、その手前のインフラ
（スイッチ・ルータ）を **自分で設計・設定**して、クライアントからゲームに到達させるラボ。
「設定が正しいと、最後にブラウザでゲームが起動する」＝ end-to-end のご褒美が出るのがポイント。

> コードは書かない。**Cisco IOS の設定とサブネット設計が主役**。ゲームは「動く確認用ターゲット」。

---

## 🎓 ねらい（カバーする CCNA 200-301 トピック）

| ドメイン | この課題で触る内容 |
|---|---|
| Network Fundamentals | IPv4 アドレッシング / **サブネット設計** / OSI とカプセル化 |
| Network Access | VLAN・トランク(802.1Q)・access/trunk ポート・SVI |
| IP Connectivity | inter-VLAN ルーティング(router-on-a-stick) / **OSPFv2 単一エリア** / 経路確認 |
| IP Services | **DHCP** / **NAT・PAT** / (発展)宛先NAT=ポートフォワード |
| Security | **拡張ACL(L4フィルタ)** / **SSH** 管理 / (発展)port-security |
| Automation | (発展)`curl` で REST/JSON を観察 → コントローラAPIの予行 |

---

## 🧰 必要ツール

- **GNS3** または **EVE-NG**（実 Docker/VM をトポロジに繋げられるもの。Packet Tracer は実 Flask を動かせないので不可）
- Cisco IOS イメージ（IOSv / vIOS-L2 など）
- 本リポジトリ（`backend/Dockerfile` をゲームサーバとして使用）
- (任意) Wireshark

---

## 🗺 トポロジ

```
 [Client PC]                                              [Game Server]
  VLAN10                                                  Docker(実Flask)
 192.168.10.0/24                                          172.16.50.10/24
      │ access vlan10                                          │
   f0/1│                                                       │g0/0
   ┌───┴───┐  trunk(dot1q)   g0/1┌──────┐10.0.0.0/30┌──────┐g0/0
   │  SW1  │────────────────────│  R1  │───OSPF────│  R2  │
   └───────┘ g0/1          g0/0 └──────┘  area 0   └──────┘
            VLAN10/20            inside        outside  gw=172.16.50.1
                                 PAT・ACL・DHCP
```

- **R1 = 支店 (inside)**：VLAN間ルーティング / クライアントへ DHCP / 外向き PAT / ACL で「ゲームだけ通す」
- **R2 = サーバ拠点 (outside)**：ゲームサーバのデフォルトGW / OSPF
- **Game = R2 配下の実サーバ**（`backend/Dockerfile` がそのまま使える＝gunicorn `0.0.0.0:5000`）

---

## 📐 アドレッシング設計

| セグメント | ネットワーク | 機器 | IP |
|---|---|---|---|
| VLAN10 Users | 192.168.10.0/24 | R1 g0/0.10 (GW) / Client | .1 / DHCP(.11〜) |
| VLAN20 Mgmt  | 192.168.20.0/24 | R1 g0/0.20 (GW) / SW1 | .1 / .2 |
| WAN R1–R2 | 10.0.0.0/30 | R1 g0/1 / R2 g0/1 | .1 / .2 |
| Server | 172.16.50.0/24 | R2 g0/0 (GW) / **Game** | .1 / **.10** |

### 📝 事前課題（サブネット計算 — 紙とペンで）

1. `192.168.10.0/24` の利用可能ホスト数・ネットワークアドレス・ブロードキャストは？
2. WAN リンクを `/30` にする理由は？ 利用可能アドレスとブロードキャストを列挙せよ。
3. OSPF の `network` 文で使う **ワイルドカードマスク**：`192.168.10.0/24` と `10.0.0.0/30` はそれぞれ？
4. 仮に VLAN10 を「最大 50 ホスト」に最適化するとき、最小のプレフィックス長は？
5. `172.16.50.0/24` を 4 つの等しいサブネットに分割すると、各プレフィックスと第3・第4サブネットのネットワークアドレスは？

<details><summary>答え合わせ</summary>

1. ホスト **254**（2^8−2）/ ネットワーク **192.168.10.0** / ブロードキャスト **192.168.10.255**
2. P2P リンクは 2 ホストあれば足り、`/30` は利用可能 2 でちょうど＝アドレス節約。利用可能 **10.0.0.1, 10.0.0.2** / ブロードキャスト **10.0.0.3**
3. `0.0.0.255` と `0.0.0.3`
4. **/26**（62 ホスト利用可能。/27 は 30 で不足）
5. 各 **/26**。サブネット境界は .0 / .64 / .128 / .192 →（第3）**172.16.50.128/26**、（第4）**172.16.50.192/26**
</details>

---

## フェーズ0 — ゲームサーバをトポロジに刺す

🎯 **目標**：実 Flask アプリを 172.16.50.10 で待受させ、R2 セグメントに接続する。

📝 **タスク**
```bash
# リポジトリ直下で
docker build -t monster-rpg ./backend     # gunicorn 0.0.0.0:5000 で起動するイメージ
```
- GNS3 に `monster-rpg` を Docker テンプレートとして登録
- ノードを R2 の g0/0 セグメントへ接続
- ノードの eth0 を **172.16.50.10/24 / gw 172.16.50.1** に設定（GNS3 のノード設定 or 起動スクリプト）

✅ **チェックポイント**：サーバノードのコンソールで `ip addr` が 172.16.50.10、`curl -s localhost:5000` が HTML を返す。

---

## フェーズ1 — L2：VLAN とトランク (SW1)

🎯 **目標**：VLAN10(Users)/VLAN20(Mgmt) を作り、クライアントは access、R1 へは trunk。

📝 **タスク**：VLAN 作成 → f0/1 を access vlan10 → g0/1 を trunk → 管理用 SVI(vlan20)。

<details><summary>設定例（詰まったら）</summary>

```
hostname SW1
vlan 10
 name USERS
vlan 20
 name MGMT
interface g0/1
 switchport trunk encapsulation dot1q   ! 機種により必要（dot1q専用機では不要/不可）
 switchport mode trunk
interface f0/1
 switchport mode access
 switchport access vlan 10
interface vlan 20
 ip address 192.168.20.2 255.255.255.0
 no shutdown
ip default-gateway 192.168.20.1
```
</details>

✅ **チェックポイント**
- `show vlan brief` → f0/1 が VLAN10
- `show interfaces trunk` → g0/1 が trunking、Allowed/Active に 10,20
- `show cdp neighbors` → R1 が見える

---

## フェーズ2 — L3：inter-VLAN ルーティング & OSPF (R1, R2)

🎯 **目標**：router-on-a-stick で VLAN 間を通し、R1↔R2 を OSPF area 0 で繋ぐ。

📝 **タスク**
- R1：g0/0 を `no shutdown`、g0/0.10 / g0/0.20 に dot1Q + IP
- R1：g0/1 に WAN IP（10.0.0.1/30）
- R1/R2：`router ospf 1` で各ネットワークを area 0 に（ワイルドカードに注意）

<details><summary>設定例（R1 のL3部分）</summary>

```
interface g0/0
 no shutdown
interface g0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
interface g0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
interface g0/1
 ip address 10.0.0.1 255.255.255.252
 no shutdown
!
router ospf 1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
```
</details>

<details><summary>設定例（R2 全体）</summary>

```
hostname R2
interface g0/1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
interface g0/0
 ip address 172.16.50.1 255.255.255.0
 no shutdown
router ospf 1
 network 10.0.0.0 0.0.0.3 area 0
 network 172.16.50.0 0.0.0.255 area 0
```
</details>

✅ **チェックポイント**
- `show ip ospf neighbor` → R1↔R2 が **FULL**
- R1 `show ip route ospf` → `O 172.16.50.0/24` が見える
- R1 から `ping 172.16.50.10` が成功

---

## フェーズ3 — IP Services：DHCP & NAT/PAT (R1)

🎯 **目標**：クライアントへ IP を自動配布し、inside→outside を PAT で R1 の WAN IP に変換。

📝 **タスク**
- VLAN10 用 DHCP プール（GW を配る、.1〜.10 は除外）
- g0/0.10・g0/0.20 を `ip nat inside`、g0/1 を `ip nat outside`
- standard ACL で inside サブネットを定義し、`interface overload` で PAT

<details><summary>設定例</summary>

```
ip dhcp excluded-address 192.168.10.1 192.168.10.10
ip dhcp pool VLAN10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
!
interface g0/0.10
 ip nat inside
interface g0/0.20
 ip nat inside
interface g0/1
 ip nat outside
!
access-list 1 permit 192.168.10.0 0.0.0.255
access-list 1 permit 192.168.20.0 0.0.0.255
ip nat inside source list 1 interface g0/1 overload
```
</details>

✅ **チェックポイント**
- Client `ipconfig`/`ip addr` → 192.168.10.11 など取得、GW 192.168.10.1
- Client から `ping 172.16.50.10` 成功後、R1 `show ip nat translations` に `192.168.10.x → 10.0.0.1` の変換が出る

---

## フェーズ4 — Security：拡張ACL & SSH

🎯 **目標**：「VLAN10 からサーバへは **ゲーム(TCP/5000) と ping だけ** 許可、他は遮断」。装置は SSH 管理に。

📝 **タスク**
- 拡張 ACL `USERS-TO-GAME` を作り、g0/0.10 の **in** に適用
- R1/R2/SW1 を SSH 化（domain-name → RSA 鍵 → ローカルユーザ → vty）

<details><summary>設定例（ACL）</summary>

```
ip access-list extended USERS-TO-GAME
 permit icmp 192.168.10.0 0.0.0.255 host 172.16.50.10
 permit tcp  192.168.10.0 0.0.0.255 host 172.16.50.10 eq 5000
 permit udp  any any eq bootps          ! DHCP を妨げない
 deny   ip   any host 172.16.50.10      ! 他のサーバ宛は遮断
 permit ip   any any                    ! それ以外は通す
!
interface g0/0.10
 ip access-group USERS-TO-GAME in
```
</details>

<details><summary>設定例（SSH・各装置共通）</summary>

```
ip domain-name lab.local
username admin privilege 15 secret StrongPass1
crypto key generate rsa modulus 2048
line vty 0 4
 login local
 transport input ssh
```
</details>

✅ **チェックポイント**
- `show access-lists` でヒットカウントが増える
- 別ホスト/別ポート宛が落ちること、ゲーム(5000)と ping は通ること
- `ssh -l admin 10.0.0.2`（R2）でログインできる

---

## フェーズ5 — End-to-End 検証 🎉

🎯 **目標**：クライアントのブラウザでゲームが開く＝設計が全部正しい証明。

✅ **最終チェック**
1. Client `curl http://172.16.50.10:5000/` → HTML が返る
2. **ブラウザで `http://172.16.50.10:5000/` → ゲーム画面が表示される**
3. (任意) サーバ手前リンクに Wireshark → **TCP 3-way ハンドシェイク**と HTTP のカプセル化を観察し、OSI を実物で確認

---

## 🔥 チャレンジ課題

### A. ACL break-fix（L3/L4 切り分けの体得）
`USERS-TO-GAME` の `eq 5000` を **`eq 80`** に書き換えて適用 → どうなる？
- 予想を書いてから試す：`ping` は？ ゲームは？
- `show access-lists` のヒットカウントで原因を特定し、5000 に戻す

<details><summary>狙い</summary>
ping(ICMP)は通るのにゲーム(TCP/5000)だけ落ちる＝「到達性はあるがアプリ層が不通」。
L3 疎通と L4 ポートフィルタを切り分ける、現場で最頻出のトラブルシュート。
</details>

### B. 宛先NAT＝ポートフォワード（発展）
R2 を「公開ルータ」に見立て、外部からゲームを公開：
```
ip nat inside source static tcp 172.16.50.10 5000 <R2のoutside側IP> 5000
```
→ `docker-compose.yml` の `5000:5000` と同じ概念を、ルータ上の NAT で再現する。

### C. 自動化のさわり（Automation ドメイン）
`curl -s http://172.16.50.10:5000/battle-json/1` などで **JSON レスポンス**を観察。
GET/POST・ステータスコード・JSON 符号化＝Cisco DNA Center 等の **REST API** を叩く筋肉の予行。

---

## ✅ 達成チェックリスト

- [ ] サブネット事前課題を解いた
- [ ] SW1：VLAN/トランク/SVI（`show vlan brief` / `show interfaces trunk` OK）
- [ ] R1/R2：OSPF 隣接 FULL、`O 172.16.50.0/24` 学習
- [ ] DHCP でクライアントが採番、GW 疎通
- [ ] PAT 変換を `show ip nat translations` で確認
- [ ] 拡張 ACL でゲーム/ping のみ許可、SSH 管理可
- [ ] **ブラウザでゲーム起動（E2E 成功）**
- [ ] ACL break-fix を体験
- [ ] (発展) 宛先NAT / Wireshark / JSON 観察

---

## 付録 — 全コンフィグ（答え）

<details><summary>R1 全体</summary>

```
hostname R1
ip domain-name lab.local
username admin privilege 15 secret StrongPass1
crypto key generate rsa modulus 2048
line vty 0 4
 login local
 transport input ssh
!
interface g0/0
 no shutdown
interface g0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 ip access-group USERS-TO-GAME in
interface g0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 ip nat inside
interface g0/1
 ip address 10.0.0.1 255.255.255.252
 ip nat outside
 no shutdown
!
ip dhcp excluded-address 192.168.10.1 192.168.10.10
ip dhcp pool VLAN10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
!
router ospf 1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
!
access-list 1 permit 192.168.10.0 0.0.0.255
access-list 1 permit 192.168.20.0 0.0.0.255
ip nat inside source list 1 interface g0/1 overload
!
ip access-list extended USERS-TO-GAME
 permit icmp 192.168.10.0 0.0.0.255 host 172.16.50.10
 permit tcp  192.168.10.0 0.0.0.255 host 172.16.50.10 eq 5000
 permit udp  any any eq bootps
 deny   ip   any host 172.16.50.10
 permit ip   any any
```
</details>

<details><summary>R2 全体</summary>

```
hostname R2
ip domain-name lab.local
username admin privilege 15 secret StrongPass1
crypto key generate rsa modulus 2048
line vty 0 4
 login local
 transport input ssh
!
interface g0/1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
interface g0/0
 ip address 172.16.50.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 10.0.0.0 0.0.0.3 area 0
 network 172.16.50.0 0.0.0.255 area 0
```
</details>

<details><summary>SW1 全体</summary>

```
hostname SW1
ip domain-name lab.local
username admin privilege 15 secret StrongPass1
crypto key generate rsa modulus 2048
vlan 10
 name USERS
vlan 20
 name MGMT
interface g0/1
 switchport trunk encapsulation dot1q
 switchport mode trunk
interface f0/1
 switchport mode access
 switchport access vlan 10
interface vlan 20
 ip address 192.168.20.2 255.255.255.0
 no shutdown
ip default-gateway 192.168.20.1
line vty 0 4
 login local
 transport input ssh
```
</details>

---

### メモ：なぜ「ゲーム」を使うのか
到達性確認を `ping` だけで終わらせず、**実在のアプリ（TCP/5000）が開く**ことをゴールにすると、
L1〜L4 の設定ミスが「ゲームが開かない」という形で即フィードバックされる。
設定 → 検証 → 動くご褒美、のループが回るのがこのラボの狙い。
