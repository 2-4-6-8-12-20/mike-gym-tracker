# Mike Gym Tracker (phone PWA)

Offline-friendly workout logger for Days A–D. Data stays on your phone via `localStorage`.

## Open on your computer

From this folder:

```bash
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
- A small looping form clip beside each exercise (tap it for a larger view)
- Rest timer (75s) after marking a set done
- History + last weights
- Night-before gym-bag checklist
- Export / import JSON backup

## Form clips

Each exercise has a looping GIF in `media/`. Thumbnails sit beside the exercise name; tap one to open the same clip larger. Clips are served from relative paths and cached by `sw.js` with the rest of the app, so they stay available offline after the first load.

Drawings are by **Everkinetic** (Greg Priday), via [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Weight_training_diagrams), under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). They were scaled onto a white square and looped (about 0.7s per pose). Poses were not redrawn. The GIFs stay under that same license — see `media/NOTICE.md`. `scripts/build-demos.py` lists the source file for each exercise id.

Where the program uses a machine variant and the library only has the standard version, the clip is the closest matching movement and the exercise name is unchanged. The larger view says so in one line (for example lat pulldown for the assisted pull-up, Romanian deadlift for the dumbbell RDL, chest-supported T-bar row for the Hammer Strength row).

## Files

- `index.html` — app
- `sw.js` — offline cache for the page, icons, and form clips
- `media/*.gif` — form clips (CC BY-SA 3.0, Everkinetic)
- `manifest.json` — PWA manifest
- `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` — icons
