# Theme Repertoire

A curated set of concepts for oneshot website generation. Each has a distinct visual language, emotional register, and CSS/JS approach.

## Tier 1: Highest Visual Impact

### Elegant Restaurant (default)
**Concept**: Fine dining storefront for a Michelin-starred restaurant
**Palette**: Near-black (#0d0d0d), warm cream (#f5f0e8), gold (#c9a84c), deep burgundy accent
**Typography**: Cormorant Garamond (display), Inter (body)
**Key techniques**:
- Menu items revealed one by one with IO
- A parallax hero with a CSS grain overlay simulating candlelight warmth
- Horizontal scroll section for the "tasting menu"
- Animated SVG flame or candle in the footer

---

### Luxury Perfume House
**Concept**: Niche fragrance atelier -- think Diptyque meets A Lab on Fire
**Palette**: Obsidian (#0a0a0f), amber (#d4a853), mist white (#f0ede8), faint rose
**Typography**: Playfair Display (display), Raleway (body)
**Key techniques**:
- Canvas particle system simulating mist/smoke drifting upward
- Scent "notes" (top/heart/base) revealed on scroll as floating pills
- Section that inverts colors when fully in viewport
- CSS blurs that shift as you scroll (backdrop-filter manipulation)

---

### Antiquarian Bookshop at Night
**Concept**: A rare books dealer operating since the 1880s, website as an old leather ledger
**Palette**: Deep ink (#1a1410), parchment (#e8d9bb), sepia (#8b6340), aged red (#8b2020)
**Typography**: IM Fell English (display), Literata or Georgia (body)
**Key techniques**:
- CSS texture via repeating SVG paper grain pattern
- Book spines as CSS-drawn rectangles in a horizontal ticker
- Ink-bleed text reveal animation (clip-path wipe)
- Footnote-style hover definitions on certain words

---

### Deep Sea Research Station
**Concept**: A fictional oceanographic institute operating below the thermocline
**Palette**: Midnight navy (#050d1a), bioluminescent cyan (#00f5c4), abyssal purple (#1a0a2e), surface foam white
**Typography**: Space Mono or IBM Plex Mono (monospace UI feel), Lato (body)
**Key techniques**:
- Canvas with slow-drifting bioluminescent particles (sine wave paths)
- "Depth meter" sidebar that updates as you scroll
- Sonar ping animation using CSS concentric rings
- ASCII art section for the "specimen log"

---

### Jazz Club & Vinyl Lounge
**Concept**: A legendary late-night jazz venue with a curated vinyl collection
**Palette**: Near-black, bourbon amber (#c17f24), faded cream, a single electric blue accent
**Typography**: Bebas Neue or Alfa Slab (display), Libre Baskerville (body)
**Key techniques**:
- Canvas waveform visualizer (static, not real audio -- drawn procedurally)
- CSS smoke rings via `border-radius` morph animation
- Vinyl record CSS drawing that spins on hover
- Set list section with animated "playing now" indicator
- Grain/noise texture simulating old film stock

---

## Tier 2: Strong Visual Language

### Living Botanical Garden
**Concept**: A studio selling rare and architectural indoor plants
**Palette**: Moss (#3d5a3e), cream (#f7f4ed), terracotta (#c47a3d), dark soil (#1f1a14)
**Typography**: Canela or DM Serif Display (display), DM Sans (body)
**Key techniques**:
- SVG leaf/frond shapes used as dividers, not images
- Growth animation -- stems "grow" into viewport using stroke-dashoffset
- Earthy color palette transitions between sections
- Grid layout for plant specimens with tilt on hover

---

### Crystal & Mineral Specimen House
**Concept**: A collector's market for rare geological specimens and crystals
**Palette**: Deep slate (#1a1a2e), amethyst (#7b2d8b), pyrite gold (#c9b03c), rose quartz (#e8b4b8)
**Typography**: Josefin Sans (display), Nunito (body)
**Key techniques**:
- CSS `conic-gradient` to simulate crystal facets
- Rotating 3D CSS transforms on specimen "cards"
- Refraction effect using layered `backdrop-filter`
- Animated shimmer sweep across text headings

---

### Night Sky Observatory
**Concept**: A remote astronomical observatory turned educational retreat
**Palette**: Deep space (#080810), constellation silver (#c8d8e8), nebula rose (#8b3a6b), horizon amber
**Typography**: Orbitron or Exo 2 (display), Source Sans Pro (body)
**Key techniques**:
- Canvas starfield with twinkling (random opacity oscillation)
- SVG constellation lines drawn via path animation
- "Observation log" section styled as a research journal
- Moon phase indicator drawn in CSS

---

### Southeast Asian Night Market
**Concept**: A hawker market guide and food culture magazine hybrid
**Palette**: Lantern red (#d4380d), turmeric yellow (#f0a500), night charcoal (#1a1410), white steam
**Typography**: Noto Sans (multilingual support), Oswald (display)
**Key techniques**:
- Canvas steam particles rising from food sections
- Lantern string CSS drawings at the top
- Dish cards with a "rating" in a non-English script (CSS-drawn stars)
- Scroll-triggered map section using CSS grid to simulate a market layout

---

### Distillery & Whisky House
**Concept**: A small-batch spirits producer from the Scottish Highlands (or Appalachia)
**Palette**: Peat dark (#1c120a), copper (#b55a1a), aged oak (#8b6340), water clear
**Typography**: Freight Display (display), Garamond or EB Garamond (body)
**Key techniques**:
- Copper still drawn entirely in SVG/CSS
- Liquid "pour" animation on scroll (clip-path liquid curve)
- Flavor wheel drawn as SVG polar chart
- Age statement typography -- huge numerals as background texture

---

### Modernist Architecture Studio
**Concept**: A boutique architecture practice known for light and materiality
**Palette**: Concrete white (#f0eeec), graphite (#2d2d2d), a single warm accent (clay or brass)
**Typography**: Helvetica Neue or Inter (everything -- pure modernist)
**Key techniques**:
- Grid-heavy layout with deliberate whitespace
- Section dividers as single-pixel horizontal lines
- Project cards that expand on hover using CSS grid tricks
- Floor plan aesthetics -- thin lines, precise spacing

---

## Techniques Reference

### No-image textures (CSS-only)
```css
/* Grain/noise overlay */
.grain::after {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E");
  pointer-events: none;
  opacity: 0.15;
}

/* Marble-ish gradient */
background: linear-gradient(135deg, #1a1a1a 0%, #2d2520 40%, #1a1a1a 70%, #261f1a 100%);

/* Vellum/paper */
background: radial-gradient(ellipse at top left, #f0e8d0, #e8d9bb 60%, #d4c4a0);
```

### Scroll-triggered reveal (Intersection Observer)
```js
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      io.unobserve(e.target); // fire once
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```

### Canvas particle system (bioluminescence / mist)
```js
const particles = Array.from({length: 80}, () => ({
  x: Math.random() * W,
  y: Math.random() * H,
  r: Math.random() * 2 + 0.5,
  vx: (Math.random() - 0.5) * 0.3,
  vy: -Math.random() * 0.4 - 0.1,
  opacity: Math.random(),
  phase: Math.random() * Math.PI * 2
}));

function draw(t) {
  ctx.clearRect(0, 0, W, H);
  particles.forEach(p => {
    p.x += p.vx + Math.sin(t * 0.001 + p.phase) * 0.2;
    p.y += p.vy;
    if (p.y < -10) { p.y = H + 10; p.x = Math.random() * W; }
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(170, 100%, 70%, ${p.opacity * 0.6})`;
    ctx.fill();
  });
  requestAnimationFrame(draw);
}
```

### Horizontal marquee ticker
```css
.ticker-wrap { overflow: hidden; }
.ticker {
  display: flex;
  gap: 4rem;
  width: max-content;
  animation: ticker 30s linear infinite;
}
@keyframes ticker {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
```

### Stroke-draw SVG on scroll
```css
.line-draw {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  transition: stroke-dashoffset 2s ease;
}
.line-draw.visible { stroke-dashoffset: 0; }
```
