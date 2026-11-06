# revealjs-markdown examples

## Markdown mapping

**One file** (`materi.md`):

```markdown
# Judul deck          → slide 1 title
## Tata kelola        → section divider “BAGIAN 1”
### Definisi          → slide title
### Cakupan           → slide title
## Implementasi       → section divider “BAGIAN 2”
### Langkah           → slide title
```

**Several files:**

```
01-tata-kelola.md     → section “Tata kelola” (BAGIAN 1)
  ## Definisi         → slide title
  ## Cakupan          → slide title
02-implementasi.md    → section “Implementasi” (BAGIAN 2)
  ## Langkah          → slide title
```

## Title (slide 1)

```html
<section id="title" class="section-divider title" data-state="divider">
  <p class="eyebrow">Nama seri</p>
  <h1>Judul<br>Presentasi</h1>
  <p class="deck-meta">Pembicara atau metadata sumber</p>
</section>
```

## Outline (always slide 2)

```html
<section id="outline">
  <p class="eyebrow">Peta pembahasan</p>
  <h2>Alur pembahasan</h2>
  <div class="content">
    <div class="outline-flow">
      <div>
        <p class="outline-number">01</p>
        <h3>Judul bagian 1</h3>
        <p>Satu kalimat kerangka.</p>
      </div>
      <div>
        <p class="outline-number">02</p>
        <h3>Judul bagian 2</h3>
        <p>Satu kalimat kerangka.</p>
      </div>
    </div>
  </div>
</section>
```

Use two to four columns. English decks use `OUTLINE` as the eyebrow.

## Section divider

```html
<section id="divider-2" class="section-divider" data-state="divider">
  <p class="eyebrow">Bagian 2</p>
  <h1>Market landscape</h1>
  <p class="sub">Satu baris kerangka section</p>
</section>
```

## Content slide — cards + source

```html
<section id="slide-5">
  <p class="eyebrow">Bagian 1 / Tata kelola data</p>
  <h2>Definisi dan cakupan</h2>
  <p class="subtitle">Apa yang termasuk dan tidak termasuk dalam cakupan</p>
  <div class="content">
    <div class="cards two">
      <div>
        <h3>Definisi</h3>
        <p>Isi dari sumber.</p>
      </div>
      <div>
        <h3>Cakupan</h3>
        <p>Isi dari sumber.</p>
      </div>
    </div>
  </div>
  <p class="source"><b>Sumber:</b> Laporan X, hlm. 12–14</p>
</section>
```

## Quote

```html
<div class="content quote">
  <p>“Kutipan panjang dari sumber.”</p>
  <p><b>– Nama, karya</b></p>
</div>
```

Quran/Arabic inside a blockquote:

```html
<blockquote>
  <p class="quran-arabic" lang="ar" dir="rtl">…</p>
  <p>“Terjemah.” — QS. …</p>
</blockquote>
```

## Single-file head

No `styles.css`. After reveal.js CDN CSS, inline the chosen palette then [theme.css](references/theme.css):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
<style>
  /* references/themes/amiri-teal.css  (or naskhi-slate / diwan-burgundy / mishkah-indigo) */
  /* then entire references/theme.css */
</style>
```

## Counters + initialize

Count top-level horizontal sections. Strip leftover `· n / n` from eyebrows. Do not enable Reveal `slideNumber`.

```javascript
const sections = document.querySelectorAll('.reveal .slides > section');
const total = String(sections.length).padStart(2, '0');
sections.forEach((section, index) => {
  const eyebrow = section.querySelector('.eyebrow');
  if (eyebrow) {
    eyebrow.textContent = eyebrow.textContent.replace(/\s·\s\d+\s\/\s\d+\s*$/, '');
  }
  if (section.querySelector('.slide-page')) return;
  const counter = document.createElement('p');
  counter.className = 'slide-page';
  counter.textContent = `${String(index + 1).padStart(2, '0')} / ${total}`;
  section.append(counter);
});

Reveal.initialize({
  width: 1280,
  height: 720,
  margin: 0,
  controls: true,
  controlsLayout: 'bottom-right',
  progress: true,
  slideNumber: false,
  hash: true,
  transition: 'fade',
  center: false,
  plugins: [ RevealChart ],
});
```
