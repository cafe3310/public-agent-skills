---
description: "Generate a one-shot single-file HTML website -- cinematic, self-contained, CodePen/Vercel-ready"
agent: build
---

# One-Shot Website Generator

Load the oneshot-website skill for the full generation instructions, theme repertoire, and techniques reference:

```
skill({ name: "oneshot-website" })
```

## Theme

```
$ARGUMENTS
```

**If a theme was provided above**, use it. It can be one of the preset themes (restaurant, perfume, bookshop, deep-sea, jazz, botanical, mineral, observatory, night-market, distillery, architecture) or any custom concept.

**If no theme was provided**, pick one from the skill's theme repertoire that would make a strong showcase. Prefer Tier 1 themes for maximum visual impact.

## Instructions

1. Generate the `PROMPT.md` -- the reproducible one-shot prompt
2. Follow ALL instructions from `PROMPT.md` to generate a SINGLE index.html
3. After generating, open the index.html file for local preview:
   ```bash
   open index.html
   ```
