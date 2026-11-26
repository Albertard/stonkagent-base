# StonkAgent — STATUS

## 27 Nov 2026 (~06:10 WIB) — Build hari 28 Nov selesai (sehari lebih cepat)

Albert menyetujui rencana 05:57 WIB, lalu memberi persetujuan berdiri 06:02 WIB
(lanjutkan sampai submit form tanpa persetujuan per langkah; X post, wallet
connect, bayar, dan buat akun tetap butuh dia).

### Selesai + terverifikasi
- **Data layer**: `src/fetch_tokens.py` (138 token bersupply > 0 dari Coinbase
  Tokenized Stocks API), `src/fetch_prices.py` (DexScreener Base/Aerodrome,
  54/138 token ber-pair — 84 sisanya mint debu tanpa likuiditas),
  `src/signals.py` (momentum + volume + NAV-gap → picks; floor volume $1.000
  + likuiditas $10.000). Pipeline `src/run_daily.py` jalan end-to-end.
- **NAV live**: 14/14 Chainlink NAV feed terbaca via `latestAnswer()` di RPC
  publik Base (8 desimal).
- **Briefing pertama**: `data/briefing-2026-11-26.json` + `logs/briefing-2026-11-26.md`
  — 28 eligible, top pick MRVLc (score +0.92, vol $38,8rb), paper portfolio
  $10.000 (hari pertama, P&L 0%).
- **Kontrak**: `contracts/AgentJournal.sol` ter-compile (solc 0.8.20, 4.024 byte,
  7 entri ABI). `contracts/deploy.py`, `src/log_decision.py` (tulis 5 picks
  harian onchain; skip bersih kalau kontrak belum deploy),
  `contracts/faucet.py` selesai.
- **Dashboard v1**: `dashboard/index.html` (self-contained, 10,6 KB) —
  picks, most active, cheapest vs NAV, avoid, paper portfolio, bagian jurnal.
- **Repo**: `README.md`, `requirements.txt`, `.gitignore` (wallet agen +
  build + venv tidak ikut ke repo publik).

### SATU BLOCKER: deploy kontrak butuh Base Sepolia ETH
- Wallet agen (testnet saja, $0, BUKAN wallet Albert):
  `0xDe5c5C23a1dEE05F4828125B1718f30F6460528B` — saldo 0 ETH.
- Yang sudah dicoba (curl): Coinbase faucet (Cloudflare 403), Chainstack (404),
  l2faucet (butuh device attestation), Triangle (503), Chainlink (butuh wallet
  connect + captcha), Alchemy (butuh 0,001 mainnet ETH + aktivitas — wallet
  baru tidak memenuhi), thirdweb (butuh wallet connect).
- Jalur tercepat: **browser task** klaim di QuickNode faucet
  (https://faucet.quicknode.com/base-sepolia — tanpa akun, tanpa saldo
  mainnet, hanya bot check) dengan alamat di atas, lalu jalankan
  `contracts/deploy.py`. Butuh ~0,01 ETH (deploy ~0,001 ETH + jurnal harian
  ~50k gas per tulis — cukup berbulan-bulan).
- Alternatif yang diteliti tapi belum dikerjakan: PoW faucet Sepolia
  (pk910.de, API /api/getSession + /api/claim) → bridge Sepolia ETH ke Base
  Sepolia via L1StandardBridge — bisa dikerjakan kalau jalur browser tidak
  tersedia.

### Berikutnya (sesuai jadwal)
- 29 Nov: deploy kontrak + tulis jurnal pertama (menunggu faucet) + runner harian.
- 30 Nov: polish dashboard + siapkan repo GitHub (butuh browser task: buat repo
  `Albertard/stonkagent-base` + push + GitHub Pages).
- 1 Des: siklus harian penuh + draft post build-in-public #1 (Albert post dari X).
- 2–3 Des: uji end-to-end + video demo. 4 Des: Albert post video di X.
- 5 Des: submit form (target internal; keras 12 Des UTC).
