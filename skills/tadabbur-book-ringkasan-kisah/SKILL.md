---
name: tadabbur-book-ringkasan-kisah
description: Gunakan skill ini saat menulis atau merapikan bagian Ringkasan Kisah dan Tafsir Singkat untuk tadabbur ayat-ayat kisah Al-Qur'an. Fokusnya adalah menyusun alur kisah berdasarkan ayat secara kronologis, tematik, ringkas, dan mudah dipahami, dengan tafsir secukupnya hanya untuk menjernihkan makna penting.
metadata:
  short-description: Menulis ringkasan kisah untuk Tadabbur Book
---

# Menulis Ringkasan Kisah

## Tujuan Skill

Membantu AI menulis bagian **Ringkasan Kisah dan Tafsir Singkat** dalam catatan tadabbur Al-Qur'an.

Hasil akhirnya harus berupa narasi bertahap yang:

- Berdasarkan ringkasan tafsir pada rentang ayat yang sesuai di [[Tafsir Ar-Razi/AI Summary]] dan/atau [[Tafsir Al-Manar/AI Summary]].
- Jika ringkasan tafsir belum tersedia, jangan lanjutkan.
- Mengikuti alur kisah dalam ayat.
- Memakai subjudul tematik yang jelas.
- Menempatkan kutipan ayat dekat dengan penjelasan yang relevan.
- Memformat kutipan ayat dengan skill `$tadabbur-book-quran-quote`.
- Menggunakan tafsir hanya untuk menjernihkan istilah, konteks, atau hubungan sebab-akibat yang penting.
- Tetap ringkas, edukatif, dan mudah diikuti pembaca umum.

## Kapan Digunakan

Gunakan skill ini ketika pengguna meminta AI untuk:

- Membuat ringkasan kisah dari rangkaian ayat.
- Merapikan bagian **Ringkasan Kisah dan Tafsir Singkat**.
- Mengubah poin-poin kisah menjadi narasi kronologis.
- Menentukan subjudul untuk tahapan kisah.
- Menempatkan ayat dan penjelasan tafsir secara proporsional.

## Prinsip Utama

### 1. Gunakan Ringkasan Tafsir yang Sesuai

Konten harus dibuat berdasarkan ringkasan tafsir pada rentang ayat yang sesuai di [[Tafsir Ar-Razi/AI Summary]] dan/atau [[Tafsir Al-Manar/AI Summary]].

Sebelum menulis, agen AI wajib memastikan ringkasan tafsir untuk rentang ayat yang digunakan sudah tersedia. Jika belum tersedia, hentikan penulisan dan minta pengguna menyediakan ringkasan AI terlebih dahulu.

Jangan mengarang isi tafsir untuk menggantikan ringkasan yang belum tersedia.

### 2. Kisah Dulu, Tafsir Secukupnya

Fokus utama adalah alur kisah berdasarkan ayat. Tafsir tidak boleh mengambil alih narasi.

Gunakan tafsir hanya ketika diperlukan untuk:

- Menjelaskan istilah yang berpotensi membingungkan.
- Menjelaskan hubungan sebab-akibat antarperistiwa.
- Memberi konteks yang membuat alur kisah lebih jelas.
- Mencegah pembaca salah memahami maksud ayat.

Hindari pembahasan tafsir yang terlalu panjang, bercabang, atau keluar dari alur kisah.

### 3. Alur Kronologis

Susun kisah sesuai urutan peristiwa dalam ayat.

Pola dasar:

1. Pembuka singkat tentang tema besar kisah.
2. Tahap pertama peristiwa.
3. Kutipan ayat yang relevan.
4. Penjelasan ringkas.
5. Tahap berikutnya dengan subjudul baru.
6. Penutup singkat yang mengikat keseluruhan alur.

### 4. Subjudul Tematik

Gunakan subjudul yang menggambarkan tahap peristiwa, bukan judul yang terlalu abstrak.

Contoh pola subjudul:

- `### Iblis menolak sujud pada Adam`
- `### Iblis diusir dari Surga`
- `### Permintaan Iblis untuk Ditangguhkan`
- `### Iblis bersumpah untuk menyesatkan anak Adam`

Subjudul harus membantu pembaca memahami posisi bagian tersebut dalam alur kisah.

### 5. Ayat Dekat dengan Penjelasan

Letakkan kutipan ayat tepat sebelum atau sesudah penjelasan yang membahas ayat tersebut.

Jangan mengumpulkan semua ayat di awal lalu menjelaskan panjang di bawahnya. Pembaca harus bisa melihat hubungan langsung antara ayat dan narasinya.

### 6. Format Kutipan Ayat Mengikuti Aturan Kutipan Al-Qur'an

Semua kutipan ayat harus diproses dengan skill `$tadabbur-book-quran-quote` dan memakai kotak kuning muda berbasis HTML `<div>` dengan style inline, bukan blockquote Markdown `>`.

Gunakan pola berikut:

```markdown
<div style="background-color: #fff8d6; border-left: 4px solid #f2c94c; padding: 12px 16px; border-radius: 6px; margin: 1em 0;">

[Teks Arab ayat atau potongan ayat]<br>
[Terjemahan bahasa Indonesia yang sinkron] (QS. [Nama Surat]: [Nomor Ayat])

</div>
```

Jika hanya memakai potongan ayat, pastikan teks Arab dan terjemahan Indonesianya merujuk pada potongan yang sama.

### 7. Tanpa Referensi Eksplisit yang Mengganggu Alur

Jangan menulis referensi eksplisit seperti:

- "Menurut Ar-Razi..."
- "Menurut Ibnu Katsir..."
- "Dalam Tafsir Ath-Thabari disebutkan..."

Jika mengambil faedah tafsir, tuliskan sebagai penjelasan yang menyatu dengan narasi, selama tidak mengubah makna atau membuat klaim yang terlalu spesifik.

## Struktur Keluaran

Gunakan outline berikut:

```markdown
## Ringkasan Kisah dan Tafsir Singkat

Paragraf pembuka singkat yang menjelaskan tema besar kisah dan posisi rangkaian ayat.

### [Subjudul tahap kisah pertama]

[Kutipan ayat yang relevan, diformat dengan `$tadabbur-book-quran-quote`]

[Penjelasan ringkas tentang peristiwa, makna penting, dan hubungan sebab-akibat.]

### [Subjudul tahap kisah kedua]

[Kutipan ayat yang relevan, diformat dengan `$tadabbur-book-quran-quote`]

[Penjelasan ringkas.]

### [Subjudul tahap kisah berikutnya]

[Kutipan ayat yang relevan, diformat dengan `$tadabbur-book-quran-quote`]

[Penjelasan ringkas.]
```

## Gaya Bahasa

- Gunakan bahasa edukatif, jernih, dan runtut.
- Dahulukan kejelasan alur daripada keindahan retorika.
- Buat paragraf pendek sampai sedang.
- Saat menyebut nama nabi dalam narasi atau subjudul, gunakan format `Nabi X a.s.`, misalnya `Nabi Saleh a.s.`, bukan hanya `Saleh`. Khusus Nabi Muhammad, gunakan `Rasulullah ﷺ` atau `Nabi Muhammad ﷺ`.
- Hindari pembahasan teknis tafsir yang tidak dibutuhkan pembaca umum.
- Hindari kalimat yang terlalu menggurui.
- Bila perlu menyederhanakan konsep, gunakan frasa seperti "Mudahnya begini..." atau "Artinya...".

### Pola Kalimat yang Harus Dihindari

- Hindari pola kontras berulang seperti “X bukan sekadar ..., tetapi ...” atau “Yang tercela bukan ..., melainkan ...”. Uraikan gagasan secara langsung dengan kalimat yang lebih alami.
- Hindari frasa yang terasa abstrak atau terlalu normatif seperti “kesempatan untuk hidup dalam keberkahan dan ketaatan” jika dapat diganti dengan penjelasan yang lebih konkret.
- Gunakan “mendustakan” ketika konteksnya adalah penolakan terhadap rasul, ayat, atau kebenaran; jangan menggantinya dengan “menolak” bila maknanya menjadi kurang spesifik. Contoh: “Jika hati terus mendustakan...”
- Tambahkan koma setelah kata hubung atau ungkapan penghubung di awal kalimat, misalnya “Namun, ...”, “Akan tetapi, ...”, “Karena itu, ...”, “Sebaliknya, ...”, dan “Selain itu, ...”.
- Pilih diksi yang konkret dan alami. Gunakan “bahkan ketika bukti telah datang”, bukan “bahkan ketika bukti telah hadir”.

## Batasan

- Jangan mengubah urutan peristiwa dalam ayat tanpa alasan yang jelas.
- Jangan menulis jika ringkasan tafsir untuk rentang ayat yang sesuai belum tersedia di [[Tafsir Ar-Razi/AI Summary]].
- Jangan menambahkan detail kisah yang tidak bersumber dari ayat atau tafsir yang kuat.
- Jangan mengubah bagian ringkasan kisah menjadi pelajaran tadabbur; pelajaran moral ditulis secukupnya saja.
- Jangan memperpanjang narasi dengan spekulasi psikologis yang tidak diperlukan.
- Jangan membuat kutipan ayat berjauhan dari penjelasan utamanya.
- Jangan memakai blockquote Markdown `>` untuk kutipan ayat; gunakan `$tadabbur-book-quran-quote`.

## Checklist Kualitas

Sebelum selesai, pastikan:

- Ringkasan tafsir untuk rentang ayat yang sesuai tersedia di [[Tafsir Ar-Razi/AI Summary]].
- Alur kisah mudah diikuti dari awal sampai akhir.
- Setiap subjudul mewakili satu tahap peristiwa.
- Ayat ditempatkan dekat dengan penjelasan yang relevan.
- Kutipan ayat memakai format kotak HTML sesuai `$tadabbur-book-quran-quote`.
- Nama nabi dalam narasi dan subjudul ditulis dengan format `Nabi X a.s.`, kecuali Nabi Muhammad yang ditulis `Rasulullah ﷺ` atau `Nabi Muhammad ﷺ`.
- Tafsir hanya muncul untuk menjernihkan bagian penting.
- Tidak ada referensi eksplisit seperti "menurut Ar-Razi" dan sejenisnya.
- Bagian ini tetap berbeda dari **Pelajaran Tadabbur**.
