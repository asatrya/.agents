---
name: tadabbur-book-quran-quote
description: Gunakan skill ini untuk memeriksa, memperbaiki, melengkapi, atau memformat kutipan ayat Al-Qur'an dalam catatan Tadabbur Book. Skill ini berfokus pada ketepatan teks, sinkronisasi potongan, rujukan ayat, dan format kotak HTML; gunakan skill lain untuk menulis narasi tadabbur secara keseluruhan.
metadata:
  short-description: Memformat kutipan ayat Tadabbur Book
---

# Aturan Kutipan Al-Qur'an

Setiap kutipan Al-Qur'an dalam Tadabbur Book harus mengikuti standar ini.

## Kapan Digunakan

Gunakan skill ini ketika pengguna meminta AI untuk:

- Memeriksa kutipan ayat dalam catatan.
- Memperbaiki atau melengkapi kutipan ayat.
- Mengubah blockquote Markdown menjadi kotak HTML standar proyek.
- Memastikan teks Arab, terjemahan, dan rujukan ayat tetap sinkron.
- Menentukan potongan ayat terpendek yang tetap mendukung penjelasan.

Jangan gunakan skill ini untuk menulis atau merombak narasi kisah maupun Pelajaran Tadabbur secara keseluruhan. Untuk bagian Ringkasan Kisah dan Tafsir Singkat, gunakan skill `$tadabbur-book-ringkasan-kisah` dan aktifkan skill ini ketika memproses kutipan ayat.

## Isi yang Wajib Ada

- Sertakan teks Arab dan terjemahan bahasa Indonesia.
- Sinkronkan potongan teks Arab dan terjemahan ketika hanya mengutip sebagian ayat.
- Sertakan nama surat dan nomor ayat, misalnya `(QS. Al-Baqarah: 33)`.
- Gunakan potongan terpendek yang tetap mendukung penjelasan.
- Jangan mengarang atau mengubah teks Al-Qur'an maupun terjemahannya secara diam-diam.

## Format yang Wajib Digunakan

Gunakan kotak HTML standar proyek, bukan blockquote Markdown:

```md
<div style="background-color: #fff8d6; border-left: 4px solid #f2c94c; padding: 12px 16px; border-radius: 6px; margin: 1em 0;">

...teks Arab...<br>
...terjemahan Indonesia... (QS. Nama Surah: nomor)

</div>
```

## Gerbang Pemeriksaan

Sebelum menyelesaikan catatan, periksa:

1. Teks Arab sesuai sumber yang tepercaya.
2. Terjemahan bahasa Indonesia sesuai teks yang dikutip.
3. Potongan Arab dan terjemahan merujuk pada bagian ayat yang sama.
4. Nama surat dan nomor ayat benar.
5. Kotak HTML memakai format standar di atas.
6. Prosa di sekitar kutipan tetap dipertahankan; jangan menghapusnya hanya untuk memformat ulang kutipan.

Jika kutipan memerlukan perbaikan aktif yang lebih luas, gunakan skill `quran-tadabbur:quran-refine-quote` jika tersedia.
