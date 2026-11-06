---
name: tadabbur-book-menulis-pelajaran
description: "Menulis atau menilai bagian Pelajaran Tadabbur dalam Tadabbur Book dengan membaca ayat per unit, menautkan lafaz dan tafsir ke refleksi masa kini, serta merumuskan subjudul yang memadukan jangkar ayat dan pelajaran praktis."
---

# Tadabbur Book Menulis Pelajaran

Gunakan skill ini saat menulis, melengkapi, merapikan, atau menilai bagian
`## Pelajaran Tadabbur` dalam Tadabbur Book.

## Tujuan

Hasilkan refleksi yang berangkat dari ayat dan tafsir, bukan salinan ringkasan
tafsir atau daftar keluaran AI. Pelajaran harus membantu pembaca memahami teks,
memeriksa diri, dan melihat bagaimana prinsip ayat bekerja dalam kehidupan.

Periksa seluruh ayat atau potongan ayat dalam rentang yang dikerjakan. Ini tidak
berarti setiap ayat harus menghasilkan satu poin.

## Prasyarat

1. Tentukan surat dan rentang ayat.
2. Cari seluruh ringkasan yang mencakup rentang tersebut di:
   - `Tafsir Ar-Razi/AI Summary/`
   - `Tafsir Al-Manar/AI Summary/`
3. Gunakan semua sumber yang tersedia; tidak perlu memaksakan kedua tafsir jika
   salah satunya memang tidak tersedia. Jika tidak ada ringkasan yang relevan,
   berhenti dan beri tahu pengguna.
4. Dari setiap ringkasan, baca ayat dan terjemahan, kata-kata penting, ringkasan
   tafsir, serta bagian-bagian tadabbur yang tersedia.
5. Baca catatan tujuan agar bagian ini tidak mengulang `Ringkasan Kisah dan
   Tafsir Singkat`. Ikuti aturan proyek dalam:
   - `_agents/rules/gaya-penulisan-tadabbur-book.md`
   - `_agents/rules/quran-quote.md`

## Proses Tadabbur

### 1. Baca ayat per unit

Untuk setiap ayat atau potongan ayat, tanyakan:

- Apa yang secara jelas disebutkan atau terjadi: lafaz, susunan, pertanyaan,
  kontras, pengulangan, tokoh, atau hubungan sebab-akibat?
- Pola apa yang serupa dengan pengalaman manusia atau kehidupan masa kini?
  Cari kesepadanan pola, bukan padanan modern yang dipaksakan.
- Apa yang perlu saya periksa dalam diri sendiri: sikap, keinginan, kebiasaan,
  keputusan, atau tanggung jawab?
- Pola pikir atau prinsip apa yang dapat dibawa ke konteks kehidupan lain?
- Jika pilihan kata Arab penting, apa nuansanya dan mengapa kata itu relevan
  dibanding kata yang berdekatan maknanya? Nyatakan hanya sejauh didukung
  tafsir atau analisis bahasa yang memadai.

Untuk setiap pertanyaan di atas, buat satu atau lebih kandidat poin pelajaran.

### 2. Bentuk kandidat poin pelajaran

Setiap kandidat harus memiliki:

- **Jangkar teks:** bagian ayat yang menopangnya.
- **Makna tafsir:** penjelasan sumber yang menerangi jangkar tersebut.
- **Gerak moral atau spiritual:** sikap yang dibongkar, ditinggalkan, dijaga,
  atau ditumbuhkan.
- **Relevansi:** bentuknya dalam diri, keluarga, masyarakat, pekerjaan, atau
  amanah pada masa kini.

Jika kandidat hanya terdengar seperti nasihat umum, sisihkan.

### 3. Pilih dan gabungkan

Pertahankan kandidat yang kuat secara tekstual, ditopang tafsir, berbeda dari poin
lain, relevan secara nyata, dan mendorong pemeriksaan diri atau tindakan.

Gabungkan kandidat yang memiliki poros moral dan kesimpulan yang sama. Sisihkan
calon yang mengulang tafsir tanpa refleksi, terlalu umum, spekulatif, atau
menjadikan isu kontemporer lebih penting daripada ayat. Jangan menentukan jumlah
poin terlebih dahulu.

Setiap poin harus memiliki satu tesis utama. Urutkan poin mengikuti alur ayat
atau perjalanan dari makna tekstual menuju implikasi batin, sosial, dan tindakan.

## Cara Menulis Setiap Poin

Gunakan alur berikut secara fleksibel:

`jangkar ayat -> makna tafsir -> prinsip moral -> bentuk dalam kehidupan -> respons`

### Subjudul

Setiap subjudul harus memadukan dua unsur:

1. apa yang disebutkan atau terjadi dalam ayat;
2. pelajaran, sikap, atau konteks kehidupan yang dapat dibawa ke masa kini.

Kedua unsur itu boleh ditulis secara eksplisit atau dipadatkan menjadi satu
rumusan yang alami. Subjudul tidak boleh hanya berupa nasihat umum, hanya
menceritakan ayat, atau mengejar istilah yang terdengar modern.

### Isi

- Mulai dari bagian ayat yang benar-benar sedang diperhatikan.
- Jelaskan hubungan antara makna ayat dan pelajaran; jangan melompat langsung
  ke nasihat.
- Turunkan prinsip tersebut ke satu atau dua contoh kehidupan yang konkret dan
  proporsional.
- Gunakan gaya bahasa yang mengajak pembaca berpikir dengan pertanyaan, bukan sekadar instruksi. Jelaskan alasan sebelum memberi seruan, arahan, atau doa. sesuai dengan aturan _agents/rules/gaya-penulisan-tadabbur-book.md
- Gunakan “kita” secara alami dan hindari nada menghakimi, mendikte, atau
  menggurui.
- Gunakan kutipan ayat terpendek yang menopang pembahasan dan ikuti aturan
  `_agents/rules/quran-quote.md`.

## Batasan

- Jangan menulis tanpa ringkasan tafsir yang relevan.
- Jangan memindahkan seluruh bagian tadabbur dari ringkasan AI secara otomatis.
- Jangan memaksakan satu poin untuk setiap ayat atau satu isu modern untuk setiap
  ayat.
- Jangan membuat klaim linguistik, psikologis, sosial, sejarah, sains, politik,
  atau hukum yang tidak ditopang sumber.
- Jangan menyatakan tafsir yang masih berupa kemungkinan sebagai kepastian.
- Contoh masa kini hanya menjelaskan prinsip yang sudah ditemukan dari ayat;
  contoh bukan sumber pelajaran.
- Jangan menambahkan rujukan eksternal baru kecuali diminta pengguna.

## Gerbang Akhir

Sebelum menyelesaikan bagian, pastikan:

- seluruh ayat dan ringkasan sumber yang tersedia sudah diperiksa;
- setiap poin memiliki jangkar ayat, dukungan tafsir, dan tesis yang berbeda;
- subjudul memuat jangkar ayat sekaligus pelajaran untuk masa kini;
- hubungan ayat, tafsir, refleksi, dan aplikasi dapat diikuti tanpa lompatan;
- gaya tulisan mengajak berpikir, konkret, inklusif, dan tidak formulaik;
- kutipan Al-Qur’an, terjemahan, dan rujukannya sudah diperiksa sesuai aturan
  proyek.
