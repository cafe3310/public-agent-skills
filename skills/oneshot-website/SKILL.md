---
name: oneshot-website
description: "Generate immersive, one-shot single-file HTML websites with embedded CSS and JS. No external images. Hostable on CodePen or Vercel. Use for writeup showcases, AI capability demos, and portfolio pieces."
author: github/jpcaparas
depends_on_skill: []
depends_on_binary:
  - python3
---

# Oneshot Website

Generate a stunning, self-contained single-file HTML website -- fully immersive, scroll-driven, cinematic. No external images, no build step. Drop into CodePen or push to Vercel as-is.

Inspired by high-end digital brand experiences and the kind of creative coding that makes people say "this was done in one shot?"

## When to invoke

Use when:
- Demonstrating an LLM's creative + technical range for writeups or articles
- Creating a stunning demo to embed in a CodePen
- Producing a portfolio piece or proof-of-concept landing page
- Showing off one-shot generation capabilities

## The Generation Prompt

When this skill is invoked, generate the full HTML file using this master approach:

---

**Write complete HTML, CSS, and JavaScript in a single self-contained file for an immersive, cinematic website about [THEME].**

The site must feel like a living brand experience -- sections that breathe as you scroll, typography that has weight and presence, and atmosphere you can almost feel.

### Theme Selection

If no theme is specified, choose one from the repertoire in `references/themes.md` that hasn't been recently used. Never default to clockwork, clocks, or time-perception themes.

**Recommended defaults** (rotate through these):
1. Elegant restaurant storefront -- dark marble, candlelight, menu sections appearing like courses being served
2. Luxury perfume house -- mist particles, scent notes drifting, amber and obsidian palette
3. Antiquarian bookshop at night -- warm amber light, floating text fragments, vellum textures in CSS
4. Deep sea research station -- bioluminescent creatures via canvas, pressure gauge UI, midnight blue
5. Jazz club and vinyl lounge -- smoke rings via SVG, waveform visualizations, sepia and amber

### Technical Constraints (NON-NEGOTIABLE)

- **Single file**: All HTML, CSS, JS in one `.html` file
- **No external images**: Use CSS gradients, SVG inline art, Canvas API, or unicode/emoji symbols only
- **No CDN dependencies** for core visuals (Google Fonts via @import is acceptable)
- **No frameworks**: Vanilla JS only. No React, Vue, Alpine, etc.
- **Static**: Must work as a static file (no server-side logic)
- **Self-hostable**: Drop into Vercel as `index.html` or paste into CodePen

### Quality Bar

This is NOT a simple landing page. It should feel like it was commissioned by a world-class brand agency. Include:

**Visual craft:**
- Scroll-triggered reveals with Intersection Observer (not scroll events -- use IO for performance)
- Parallax depth on at least 2 layers (background moves slower than foreground)
- Typography that has character -- mix of serif and sans, large display type with tight tracking
- Color palette of 3-4 tones maximum, applied with intention (not rainbow)
- Subtle animated texture or grain overlay via CSS (repeating SVG noise, pseudo-element with opacity)

**Interaction:**
- Cursor that responds subtly (not gimmicky -- a small dot or trail at most)
- Hover states that feel intentional (transforms, not just color changes)
- At least one section with a scrolling marquee or horizontal text ticker
- Navigation that changes opacity/style on scroll

**Atmosphere:**
- Hero section with large, centered typographic statement
- At minimum 5 distinct sections with scroll transitions between them
- Footer with subtle details (coordinates, a fictional address, a motto in a second language)
- A moment of surprise -- one section that does something unexpected (inverted colors, a canvas animation, text that rearranges)

**Polish details:**
- `font-display: swap` on any web fonts
- `will-change: transform` on animated elements
- Smooth scroll behavior on `html`
- Mobile-responsive (flexbox/grid, no fixed px widths on containers)
- `prefers-reduced-motion` media query to disable animations for accessibility

### Output Format

Produce **two files**:

**1. `PROMPT.md`** -- the exact one-shot prompt that will be used to generate this site. 

**2. `index.html`** -- the complete single-file website. Start with `<!DOCTYPE html>` and end with `</html>`. No explanation before or after the HTML.

Format of `PROMPT.md`:

```markdown
# One-Shot Prompt

**Theme**: [theme name]
**Generated**: [date]
**Model**: [model name and version]

## Prompt

[The complete verbatim prompt that would reproduce this exact site if fed to any capable LLM fresh]

## Notes

- [Any notable techniques used]
- [Hosting: CodePen / Vercel / local]
```

Name fictional brands with restraint: evocative, not punny. Think: "Maison Vorieux", "Sublevel 7", "The Meridian Press", not "Tasty Bistro" or "Cool Restaurant".

---

## Hosting

### CodePen
1. Create new Pen
2. Paste entire contents into the HTML panel
3. Enable "Full Page" view

### Vercel
```bash
mkdir my-site && cd my-site
# save as index.html
vercel --prod
```

### Local preview
```bash
open index.html   # macOS
# or
python3 -m http.server 3000
```

## Example Output Names

The generated site should have a real name. Examples by theme:

| Theme | Brand Name | Tagline |
|-------|-----------|---------|
| Restaurant | Maison Vorieux | Fine dining, honest cooking |
| Perfume | Atelier Obscur | Scent as memory |
| Bookshop | The Meridian Press | Est. 1887 |
| Deep Sea | Sublevel 7 | Research below the thermocline |
| Jazz | The Amber Room | Live music every Thursday |
| Botanical | Selva Studio | Plants for considered spaces |
| Mineral | Cabinet Brut | Specimen traders since 1952 |
| Observatory | Station Nuit | Watching since 1901 |
| Night Market | Hawker's Almanac | Every dish has a story |
