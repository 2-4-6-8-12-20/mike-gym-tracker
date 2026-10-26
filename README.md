# Mike Gym Tracker (phone PWA)

Offline-friendly workout logger for Days A–D. Data stays on your phone via `localStorage`.

## Open on your computer

From this folder:

```bash
cd /workspace/mike-gym-tracker
python3 -m http.server 8765
```

Then open: http://127.0.0.1:8765/

Or open `index.html` directly in a browser (file:// works for logging; Add to Home Screen needs https or localhost).

## Add to Home Screen (iPhone)

1. Host this folder somewhere you can open over **https** (or use a Mac/PC on the same Wi‑Fi serving localhost and tunnel — simplest is any static host).
2. On your iPhone, open the tracker URL in **Safari** (not Chrome).
3. Tap the **Share** button.
4. Tap **Add to Home Screen**.
5. Name it (e.g. **Gym**) → **Add**.
6. Open the new icon. After the first load it works offline.

### Quick host options

- Drop the whole `mike-gym-tracker` folder on any static host (GitHub Pages, Netlify, Cloudflare Pages, your own server).
- Or from a Mac on the same Wi‑Fi: `python3 -m http.server 8765` and open `http://YOUR-MAC-IP:8765` in Safari (Add to Home Screen may still prefer https).

## What’s included

- Day A Press / B Pull / C Upper Isolation / D Light Legs (30‑min lifts)
- Set logging: weight, reps, Done — saved automatically
- Rest timer (75s) after marking a set done
- History + last weights
- Night-before gym-bag checklist
- Export / import JSON backup

## Files

- `index.html` — app
- `manifest.json` — PWA manifest
- `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` — icons
