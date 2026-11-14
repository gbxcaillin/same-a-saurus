# Same-o-saurus

A dinosaur matching puzzle game for ages 3 to 5. A sentence at the top asks the child to
"Match all the dinosaurs that are the same colour" (or species, shape, size, number of legs,
number of horns) and they tap every dinosaur that matches the example. Every fourth level is a
silly bonus round: matching sunglasses or matching hairstyles.

**Play it:** open `index.html` in any modern browser. It is one self-contained file (about 7.5 MB)
with all art, animation, video, music and sound built in. No server or internet needed.

## How it plays

- An opening video plays when the game loads: a lonely T-Rex finds its matching twin and the matching
  pairs pile in for a dance. The logo appears over the ending, then the camera tilts up into the sky
  and comes back down onto the title page. It can be skipped, and the camera button on the title page
  replays it. It is one square video with all the action staged in the centre, so it crops cleanly to
  9:16 phones, 4:3 and tablets in either orientation. The video starts silent (browsers require a tap before sound); the first tap starts the music.

- No timer and no way to fail. A wrong tap gets a gentle wobble; after two wrong taps, or 9 seconds
  of waiting, one correct dinosaur wiggles as a hint.
- The question ("Match all the dinosaurs that are the same colour") is read aloud by a recorded friendly
  female voice at the start of each level; tap the speaker to hear it again. That is the only speech in
  the game. A plain-words hint such as "Find the purple ones!" shows under it as text, and the operative
  word (colour, size, number of horns...) is enlarged, colour-coded and gently wiggles.
- Tapped matches dance (sprite-sheet animation), and finishing a level triggers the celebration:
  party video, fanfare, confetti cannons, stars and a cheer. Tapping the party screen fires more confetti.
- 1 to 3 stars per level (3 for no wrong taps). Progress and stars are saved on the device.
- Difficulty ramps from 4 dinosaurs up to 12, and from "only one thing differs" to "everything varies".
- Spelling follows the device region: `color` for US devices, `colour` elsewhere. Grown-ups can override it.
- Layout is fluid: everything is sized from the short screen edge, the grid re-packs for any
  aspect ratio, and landscape moves the question to a side panel. Tested from 320x568 phones to
  1180x820 tablets, both orientations, including rotating mid-level.

## Money

- Free to play with a short ad break after every 3 completed levels (never more often).
- "Grown-ups" (behind a multiplication gate) offers **Remove ads, $0.99** and Restore purchase.
- This web build has no real store or ad network attached, so the ad is a clearly labelled 5 second
  placeholder and the purchase is a labelled simulation. A native wrapper (Capacitor, Cordova,
  TWA, WKWebView) plugs the real ones in by defining this object before the game loads:

```js
window.SameOSaurusBridge = {
  showInterstitial: () => Promise,        // show one short ad, resolve when it closes
  purchaseRemoveAds: () => Promise,       // resolve true when the $0.99 purchase succeeds
  restorePurchases: () => Promise,        // resolve true if already owned
  getPrice: () => Promise,                // localised price string, e.g. "$0.99"
  speak: (text, lang) => {}               // optional native text-to-speech
};
// the wrapper can also call window.SameOSaurus.setAdFree(true) at start-up
```

Things to know before store submission:

- A game aimed at under-5s falls under Google Play's Families policy and Apple's Kids category
  rules: use a certified kids ad SDK, no personalised ads, and keep purchases behind the parent gate.

## Voice

8 recorded lines per accent (one per question type), generated with Kokoro (open-source text-to-speech, Apache-2.0 licence):
`af_heart` for US devices and `bf_emma` (British) everywhere else, following the same region rule as
the spelling. The clips are built into the file, so the voice works offline and inside app wrappers.
If a clip is ever missing the game falls back to the device's own speech engine and prefers a female voice.
Lines live in `tools/voice_lines.json`; regenerate with `tools/make_voice.py`.

## Art

All art, sprite animation and video was generated with OpenArt:

| Asset | Model |
| --- | --- |
| 8 dinosaur species, accessories, background, logo, icon, party scenes | Seedream 5.5 (transparent PNG) |
| 64 accessory sprites (every species redrawn wearing each of the 4 wigs and 4 sunglasses, so they fit the head) | Seedream 5.5 image-to-image |
| 8 dance loops (cut into sprite strips) | PixVerse V6 image-to-video on a magenta key colour |
| 2 celebration clips and the 10 second opening video (3 shots, started from a frame built from the game's own art) | Kling 3 Omni image-to-video |

Each species is drawn once in green; the game recolours it at run time (red, orange, yellow,
green, blue, purple), so colours are always exact. Number of legs and horns were checked by eye
per species. Pterodactyl and Parasaurolophus are left out of horn rounds because their crests are ambiguous.

## Repository layout

```
index.html            the built game (commit this, ship this)
src/game.html         source template (edit this)
assets/               processed art, sprite strips, video
masters/              full-resolution originals not built into the game (1440px opening video)
tools/build.py        inlines assets/ into index.html
tools/make_assets.py  raw OpenArt downloads -> assets/ (cut-outs, keying, sprite strips, video encode)
tools/dance_frames.json  which video frames make each dance loop
tools/make_voice.py   voice_lines.json -> assets/voice/<us|uk>/*.mp3
tools/playtest.py     automated playthrough (Playwright): puzzle correctness over 4,800 generated
                      rounds, touch input, ads every 3 levels, purchase flow, save/reload, rotation
```

Rebuild after editing: `python3 tools/build.py`
