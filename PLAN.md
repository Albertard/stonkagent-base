# Base Stocks Maxxing Season — PLAN

Pemilik: Albert Ardira Prasetyo (solo, tim 1 orang — saya, Cailin, sebagai agen).
Dibuat: 27 Nov 2026. Status: RISET + RENCANA SELESAI — menunggu persetujuan sebelum build.

## 1. Aturan resmi (terverifikasi dari sumber primer, 27 Nov 2026)

Sumber:
- Halaman resmi: https://base.org/stocksmaxxing (di-crawl 26 Nov 22:52 UTC)
- Aturan resmi: https://www.base.org/stocksmaxxing/rules (di-crawl 26 Nov 22:52 UTC)
- Sponsor: Coinbase Technologies, Inc. ("Base").

### Deadline — PENTING: ada perpanjangan
- **Periode Quest resmi: 5 Nov – 12 Des 2026 (UTC).** Aturan §2: "The Quest begins on November 5, 2026 and ends December 12, 2026... All submissions must be received during the Quest Period... all times are in Coordinated Universal Time (UTC)."
- Halaman resmi: "Nov 5 to Dec 12", timeline: "Nov 13–Dec 12 Build & launch", "Dec 12 Submit your project".
- **Semua artikel berita 5–12 Nov (dan pengumuman X @base 5 Nov) masih menulis 5 Des** — deadline ASLI 5 Des, kemudian DIPERPANJANG ke 12 Des di halaman + aturan resmi. Aturan juga bilang tanggal bisa berubah.
- **Keputusan: target internal submit 5 Des 2026** (tenggat asli, jadi buffer aman); tenggat keras 12 Des 2026 UTC. Sisa waktu dari 27 Nov: 8 hari ke target internal, 15 hari ke tenggat keras.

### Cara masuk (Aturan §5) — 3 langkah, semuanya wajib
1. **Post publik di X** berisi video demo proyek (mis. rekaman Loom) yang menjelaskan cara kerjanya, dan **tag @buildonbase**. Halaman bisa mewajibkan tag/konten tambahan.
2. **Isi + kirim formulir submission resmi** yang tertaut di halaman Quest ("Apply Now" → Google Forms). Berisi link post X, track yang dimasuki, dan info lain yang diminta form.
3. Penuhi syarat tambahan di Track Section untuk tiap track yang dimasuki.
- Satu submission per track per entrant/tim. Satu proyek boleh menang hanya di SATU track (kecuali halaman bilang lain).
- **Testnet DIIZINKAN dan "tidak akan dinilai lebih rendah"** karena dibangun di testnet (§5). Tidak perlu purchase, funding wallet, holding token, atau pembayaran apa pun untuk ikut.
- Usia 18+, bukan residen negara yang disanksi OFAC. Solo atau tim maks 5 orang. Hadiah dibayar **USDC di Base**.
- Pemenang diverifikasi dalam 7 hari setelah pemberitahuan: bukti identitas/usia/domisiil, screening sanksi, IRS W-9/W-8, alamat wallet, surat pernyataan (§9).

### Track (3, masing-masing dinilai + diberi hadiah terpisah)
1. **Meme and Community Economies** — cara baru mengorganisir meme/komunitas di sekitar tokenized equities. Partner: Stonks Exchange, o1 Exchange, Feel.cash, Hydropump by Hydrex.
2. **Agentic Stock Finance** — agen (program, bukan hanya manusia) yang riset / earn / trading di sekitar tokenized stocks. Partner: Bankr, BaseStonk.
3. **Programmable Stock Markets** — building block pasar saham baru: portfolio kustom, index, structured product, financing, prediction market, infrastruktur. Partner: BaseStonk, Bankr.
- Total hadiah: **$100.000+** (tiga track) + **$6.000 khusus proyek terbaik yang dibangun di publik**. Pembagian hadiah PER TRACK tidak tertulis di teks halaman yang bisa diekstrak (kemungkinan di-render sebagai gambar/JS) — total $100k+ sudah pasti; split per track belum diketahui, bukan blocker.

### Penilaian (dari post resmi @base 5 Nov + berita)
- **50% Traction** — pemakaian onchain nyata, terverifikasi onchain.
- **25% Product** — utilitas, kreativitas, eksekusi.
- **25% Build in public** — post progres bertanggal + pertumbuhan komunitas.
- Panel juri pilihan sponsor; keputusan final dan mengikat (§7). Kalau sebuah track menerima <3 submission yang eligible, sponsor boleh memberi hadiah lebih sedikit di track itu.

### Persyaratan submission (§6)
- Dibangun di / terintegrasi bermakna dengan jaringan Base, dan cocok dengan track yang dimasuki.
- Karya orisinal entrant/tim (boleh pakai kode/produk pre-existing milik sendiri, asalkan form menjelaskan dengan jelas apa yang dibangun SELAMA periode Quest; komponen open-source boleh dipakai sesuai lisensinya).
- Tidak melanggar IP/privasi, tidak ada malware/konten yang dilarang, patuh hukum (termasuk sekuritas, derivatif, lending, prediction market, sanksi, data protection).
- **Tidak boleh mengklaim memberi hak atas perusahaan publik** (mis. voting rights) yang tidak diberikan asetnya, dan tidak boleh mengklaim endorsement dari Base/partner/issuer.

## 2. Data yang tersedia (terverifikasi langsung, 27 Nov 2026)

### Tokenized Stocks API (resmi, publik, tanpa API key)
- Base URL: `https://api.coinbase.com/v1/tokenized-stocks` — **SUDAH DITES LANGSUNG, HIDUP**.
- Endpoint: `GET /` (list), `/chains`, `/nav-feeds`, `/total-supply/{contract}`, `/metadata/{ticker}`, `/images/{symbol}`, `/prospectus/{ticker}`, `/prospectuses`, `/corporate-actions/{id}`. Paginasi via `page_token`, `page_size` maks 500.
- **138 token saham dengan supply positif** saat ini (Coinbase-issued, suffix "c"): AAPLc, TSLAc, NVDAc, MSFTc, AMZNc, METAc, GOOGLc, NFLXc, AMDc, PLTRc, HOODc, MSTRc, GMEc, dll. Field: contract address, symbol, nama, decimals (8), multiplier, total_supply, ISIN, icon_url, first_mint_date.
- **CATATAN: hanya 13 dari 138 token yang punya `nav_price`** (Chainlink NAV feed). Jadi sinyal produk TIDAK BOLEH bergantung pada NAV untuk semua token — harga live harus dari DEX (Aerodrome di Base mainnet, via DexScreener API publik) untuk sebagian besar token.
- Token adalah standar B20 (perpanjangan ERC-20): multiplier berubah saat dividen/split (mis. dividen → multiplier 1.00 → 1.02); saldo holder tidak berubah.

### Harga live
- Tokenized stocks Coinbase diperdagangkan di Aerodrome (DEX utama Base). DexScreener punya pair Base untuk token-token ini (endpoint publik, tanpa key). Dipakai untuk harga + volume + momentum.

## 3. Produk yang dibangun: "StonkAgent"

### Pilihan track: **Agentic Stock Finance** (partner: Bankr, BaseStonk)
Alasan: (1) ini yang paling cocok dengan kemampuan nyata kami — saya sendiri agen AI, dan pengoperasian harian agen itu gratis + bisa diandalkan, tanpa perlu merekrut pengguna eksternal dalam 15 hari; (2) build-in-public natural (log harian agen + post X); (3) memakai API resmi Base (tanpa key) + kontrak testnet.

### Apa itu StonkAgent
Agen riset AI untuk saham tokenisasi Coinbase di Base, yang setiap hari:
1. **Menarik data** 138 token dari Tokenized Stocks API resmi + harga/volume live dari DexScreener/Aerodrome (Base mainnet).
2. **Menganalisis**: momentum (perubahan harga 1j/24j), gap vs NAV (untuk 13 token yang NAV-nya ada), volume, dan "picks" harian (top gainer, paling aktif, paling murah vs NAV).
3. **Mencatat keputusan onchain**: setiap keputusan harian (ticker, aksi BUY/SELL/HOLD paper, alasan) ditulis ke kontrak pintar kecil **AgentJournal** di **Base Sepolia testnet** — transaksi onchain nyata, terverifikasi di Basescan Sepolia, gas $0 (ETH testnet dari faucet). Ini jejak "traction" kami.
4. **Mempublikasikan briefing harian** di dashboard web publik: daftar token + harga, picks agen, portfolio paper + P&L, dan log jurnal onchain dengan link Basescan.

### Yang TIDAK dilakukan
- Tidak ada mainnet, tidak ada dana nyata, tidak ada wallet Albert yang di-connect, tidak ada pembayaran apa pun. Semua $0.
- Tidak ada token baru yang diluncurkan (tidak diwajibkan aturan, dan tidak perlu).
- Tidak mengklaim hak atas saham underlying; dashboard menampilkan data referensi + disclaimer yang jelas.

### Komponen build
| # | Komponen | Teknologi | Catatan |
|---|----------|-----------|---------|
| 1 | Data layer | Python, `requests` | Tokenized Stocks API (tanpa key) + DexScreener API (tanpa key); cache harian ke JSON |
| 2 | Signal engine | Python | Momentum, volume, NAV-gap (bila ada); aturan picks transparan + terdokumentasi |
| 3 | AgentJournal contract | Solidity (sederhana, ~60 baris) | `logDecision(ticker, action, reasonHash, navPrice)`; deploy Base Sepolia via faucet ETH; alamat + ABI publik di repo |
| 4 | Agent runner | Python + cron harian | Siklus harian: tarik data → analisis → tulis jurnal onchain → update dashboard data → draft post X |
| 5 | Dashboard web | HTML statis + JS (artifact / GitHub Pages) | Daftar token, harga live, briefing harian, portfolio paper + P&L, log jurnal + link Basescan |
| 6 | Repo publik | GitHub `Albertard/stonkagent-base` | Kode + README + log build-in-public bertanggal |
| 7 | Video demo + post X | Rekaman layar dashboard + narasi | Albert post dari HP-nya, tag @buildonbase (X diblokir di browser saya) |
| 8 | Submission form | Google Forms (link "Apply Now") | Diisi setelah video + repo + dashboard jadi; HANYA setelah persetujuan Albert |

## 4. Jadwal (target internal 5 Des; keras 12 Des)

| Hari | Tanggal | Pekerjaan |
|------|---------|-----------|
| 1 | 27 Nov | Riset + rencana (SELESAI hari ini) → lapor ke agen utama |
| 2 | 28 Nov | Scaffold repo + data layer (API + DexScreener) + signal engine v1 |
| 3 | 29 Nov | AgentJournal contract + deploy Base Sepolia (faucet) + runner harian v1 |
| 4 | 30 Nov | Dashboard v1 (token, harga, briefing, portfolio, log jurnal) |
| 5 | 1 Des | Polish dashboard + siklus harian pertama penuh + post build-in-public #1 (Albert) |
| 6 | 2–3 Des | Uji end-to-end + perbaiki + rekam video demo |
| 7 | 4 Des | Video demo selesai → Albert post di X (tag @buildonbase) |
| 8 | 5 Des | **SUBMIT form (target internal)** — setelah persetujuan Albert |
| Buffer | 6–12 Des | Perbaikan + post lanjutan bila perlu; tenggat keras 12 Des UTC |

## 5. Yang butuh Albert (sesuai instruksinya 27 Nov 05:52: "jika butuh gmail twitter wallet bilang saja")
1. **Post X**: video demo + tag @buildonbase (dia post dari HP; saya siapkan video + caption). Juga post build-in-public harian (saya draft, dia post) — ini 25% nilai + hadiah $6.000.
2. **Form submission**: saya siapkan semua isinya; dia setujui sebelum saya kirim (form Google — pengiriman form mungkin butuh browser; akan saya sampaikan kalau perlu dia yang klik kirim).
3. **Hanya kalau menang**: alamat wallet Base untuk USDC + verifikasi identitas/W-8 (sesuai §9). Bukan sekarang.
4. TIDAK butuh: Gmail, wallet connect, pembayaran, dana mainnet.

## 6. Penilaian jujur (risiko + peluang)
- **Traction (50%) adalah titik lemah struktural**: proyek baru 15 hari hampir tidak mungkin punya pengguna nyata sebanyak proyek yang sudah jalan sebulan. Kompensasi kami: aktivitas onchain harian yang nyata dan terverifikasi (jurnal testnet — aturan bilang testnet tidak dinilai lebih rendah), dashboard terbuka yang bisa diikuti siapa pun, dan build-in-public yang agresif.
- **Product (25%) + Build in public (25% + $6.000) adalah tempat kami bisa menang**: produk nyata yang bekerja tiap hari + log publik bertanggal.
- **Peluang menang jujur: rendah tapi bukan nol; biaya $0 dan ~6 hari kerja agen.** Ini taruhan yang rasional: hadiah $100k+ dan tidak ada downside finansial.
- Risiko teknis: NAV hanya 13/138 token (sudah diatasi dengan harga DEX); form Google mungkin punya field yang belum terlihat (cek saat build); tanggal bisa berubah lagi (pantau halaman resmi tiap hari).
- Risiko kepatuhan: jangan pernah menampilkan produk sebagai "saham" atau memberi nasihat investasi — selalu label "paper trading / simulasi, bukan nasihat investasi".

## 7. Status + langkah berikut
- [x] Riset aturan resmi (halaman + rules + API) — 27 Nov 2026
- [x] Rencana produk (file ini) — 27 Nov 2026
- [x] Persetujuan rencana (Albert: "Ya, bangun StonkAgent", 27 Nov 05:57 WIB)
- [x] Persetujuan berdiri (Albert 27 Nov 06:02 WIB, sebelum tidur): lanjutkan
      build sampai SUBMIT FORM tanpa minta persetujuan per langkah. Yang tetap
      butuh Albert: post video demo di X + post build-in-public harian (dia post
      dari HP saat bangun), connect wallet, bayar apa pun, buat akun atas namanya.
- [x] Build hari 28 Nov (dikerjakan 27 Nov, sehari lebih cepat):
  - [x] Scaffold repo + data layer + signal engine v1 — SELESAI + terverifikasi
        end-to-end (138 token, 14 NAV live, 54 token ber-pair, 28 eligible,
        briefing 2026-11-26: top pick MRVLc +0.92). Dua bug diperbaiki saat build:
        (1) API mengembalikan 435 token — difilter ke 138 bersupply > 0;
        (2) DexScreener memotong respons batch 30 alamat — batch dikecilkan ke
        10 + retry individual untuk token bersupply besar (41 → 54 token ber-pair);
        (3) NAV feed hanya berisi alamat aggregator — harga dibaca via
        `latestAnswer()` di RPC publik Base (14/14 live);
        (4) picks sempat didominasi token bervolume $26 — floor volume $1.000
        ditambahkan ke aturan eligible.
  - [x] Kontrak AgentJournal ditulis + ter-compile (solc 0.8.20, 4.024 byte),
        skrip deploy + skrip tulis-jurnal harian + faucet helper selesai.
  - [x] Dashboard v1 selesai (dashboard/index.html, self-contained, terverifikasi
        berisi picks + catatan jurnal).
  - [ ] Deploy kontrak ke Base Sepolia — **TERBLOKIR: wallet agen 0 ETH.**
        Semua faucet tanpa login butuh langkah browser (captcha / wallet-connect /
        device attestation) yang tidak bisa dijalankan curl. Wallet agen:
        `0xDe5c5C23a1dEE05F4828125B1718f30F6460528B` (testnet saja, $0).
        Jalur tercepat: browser task / Albert klaim di QuickNode faucet
        (tanpa akun, tanpa saldo mainnet) lalu jalankan `contracts/deploy.py`.
        Detail di `contracts/faucet.py`. Setelah terdanai, deploy + tulis jurnal
        harian otomatis lewat `src/run_daily.py`.
- [ ] Repo GitHub publik `Albertard/stonkagent-base` — butuh browser task
      (buat repo + push). Dashboard akan di-host via GitHub Pages.
- [ ] Siklus harian penuh pertama (1 Des) + draft post build-in-public #1
- [ ] Video demo + post X (Albert) — 4 Des
- [ ] Submit form — 5 Des (target), keras 12 Des UTC
