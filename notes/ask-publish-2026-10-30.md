# Ask for a cert-machine chat: publish claimbox's landing page (2026-10-30)

*Paste into a cert-machine chat. The operator's word, 2026-10-30: the page goes live "like Machinidae" — published at
carlostoledo.co/claimbox/, listed in the sitemap, linked from no page yet.*

---

claimbox has a landing page built the way Machinidae's is: its own repository builds and checks it, and cert-machine serves
a byte copy as a foreign zone. Please publish it.

- **Source:** `~/Projects/claimbox/web/dist/` (one self-contained `index.html`; fonts from Google Fonts only), built by
  `make web` in `~/Projects/claimbox`. Its own check: `python3 -m web.build --check` (every value re-read from its record
  address, WARRANT's five dashes, greys and one red only, no other host, no unaddressed number in a measured section, a
  legend wherever a standing is marked, COPY.md's internal words refused; nine red controls).
- **Register the zone** in `design/zones.js` `FOREIGN`, beside Machinidae:
  `{ dir: 'claimbox/', owner: '~/Projects/claimbox', build: 'make web → web/dist/', src: '~/Projects/claimbox/web/dist', sitemap: true }`,
  with a dated line in the file's header comment.
- **Publish** with `tools/publish-zone.js` (it writes the pin `corpus/zones/claimbox.json` and one commit holding only the
  zone), then `--check`.
- **Sitemap:** listed (`sitemap: true`). **Links:** none from any page yet.
- The page's nav links point to `../index.html`, `../reports/index.html` and `../grammar/index.html`; its canonical URL is
  `https://carlostoledo.co/claimbox/`.
- Nothing else in cert-machine changes. The grammar is re-expressed in claimbox (`web/grammar.css`), nothing imported; the
  five cert-machine files it was read from are pinned in claimbox's `web/PINS.json`.
