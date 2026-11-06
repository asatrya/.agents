# Aturan Kutipan Al-Qur'an

Setiap kutipan Al-Qur'an dalam Tadabbur Book harus mengikuti standar ini.

## Isi yang wajib ada

- Sertakan teks Arab dan terjemahan bahasa Indonesia.
- Sinkronkan potongan teks Arab dan terjemahan ketika hanya mengutip sebagian ayat.
- Sertakan nama surat dan nomor ayat, misalnya `(QS. Al-Baqarah: 33)`.
- Gunakan potongan terpendek yang tetap mendukung penjelasan.
- Jangan mengarang atau mengubah teks Al-Qur'an maupun terjemahannya secara diam-diam.

## Format yang wajib digunakan

Gunakan kotak HTML standar proyek, bukan blockquote Markdown:

```md
<div style="background-color: #fff8d6; border-left: 4px solid #f2c94c; padding: 12px 16px; border-radius: 6px; margin: 1em 0;">

...teks Arab...<br>
...terjemahan Indonesia... (QS. Nama Surah: nomor)

</div>
```

## Gerbang pemeriksaan

Sebelum menyelesaikan catatan, periksa teks Arab, terjemahan, rujukan, sinkronisasi potongan, dan format HTML. Jangan menghapus prosa di sekitarnya hanya untuk memformat ulang kutipan.

Gunakan skill `refine-quran-quote` yang tersedia ketika kutipan memerlukan perbaikan atau pelengkapan aktif.
