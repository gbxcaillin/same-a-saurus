# Same-a-saurus

A dinosaur matching puzzle game for ages 3 to 5. A sentence at the top asks the child to
"Match all the dinosaurs that are the same colour" (or species, shape, size, number of legs,
number of horns) and they tap every dinosaur that matches the example. Every fourth level is a
silly bonus round: matching sunglasses or matching hairstyles.

**Play it:** open `index.html` in any modern browser. It is one self-contained file (about 3 MB)
with all art, animation, video, music and sound built in. No server or internet needed.

## How it plays

- No timer and no way to fail. A wrong tap gets a gentle wobble; after two wrong taps, or 9 seconds
  of waiting, one correct dinosaur wiggles as a hint.
- The question is read aloud (tap the speaker to hear it again), with a plain-words hint under it
  such as "Find the purple ones!".
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
window.SameASaurusBridge = {
  showInterstitial: () => Promise,        // show one short ad, resolve when it closes
  purchaseRemoveAds: () => Promise,       // resolve true when the $0.99 purchase succeeds
  restorePurchases: () => Promise,        // resolve true if already owned
  getPrice: () => Promise,                // localised price string, e.g. "$0.99"
  speak: (text, lang) => {}               // optional native text-to-speech
};
// the wrapper can also call window.SameASaurus.setAdFree(true) at start-up
```

Things to know before store submission:

- A game aimed at under-5s falls under Google Play's Families policy and Apple's Kids category
  rules: use a certified kids ad SDK, no personalised ads, and keep purchases behind the parent gate.
- Android WebView has no built-in speech, so supply `speak` from the wrapper there or the voice is silent.

## Art

All art, sprite animation and video was generated with OpenArt:

| Asset | Model |
| --- | --- |
| 8 dinosaur species, accessories, background, logo, icon, party scenes | Seedream 5.5 (transparent PNG) |
| 8 dance loops (cut into sprite strips) | PixVerse V6 image-to-video on a magenta key colour |
| 2 celebration clips | Kling 3 Omni image-to-video |

Each species is drawn once in green; the game recolours it at run time (red, orange, yellow,
green, blue, purple), so colours are always exact. Number of legs and horns were checked by eye
per species. Pterodactyl and Parasaurolophus are left out of horn rounds because their crests are ambiguous.

## Repository layout

```
index.html            the built game (commit this, ship this)
src/game.html         source template (edit this)
assets/               processed art, sprite strips, video
tools/build.py        inlines assets/ into index.html
tools/make_assets.py  raw OpenArt downloads -> assets/ (cut-outs, keying, sprite strips, video encode)
tools/dance_frames.json  which video frames make each dance loop
tools/playtest.py     automated playthrough (Playwright): puzzle correctness over 4,800 generated
                      rounds, touch input, ads every 3 levels, purchase flow, save/reload, rotation
```

Rebuild after editing: `python3 tools/build.py`
