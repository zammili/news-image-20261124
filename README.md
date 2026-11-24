# The World Ledger — 24 November 2026

[![Bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/zammili/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/zammili/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-image newspaper front page summing up Tuesday 24 November 2026 in
world news, built for the make.fun bounty
[news-image-20261124](https://make.fun/bounty/news-image-20261124).

## The stories

- **Lead — "HUANG IS BACK":** Nvidia reinstated Jensen Huang as CEO less
  than two weeks after he was forced out, after President Trump
  intervened. Markets surged: S&P 500 +4.73%, Nasdaq +6.51%, Seoul +6%,
  Nikkei +3.91%. The page carries a hand-drawn bar chart of the day's
  index jumps and a "Markets at a Glance" strip.
- **Iran standoff deepens:** JD Vance and Marco Rubio met Qatar's prime
  minister at the White House as Iran vowed to use all tools to confront
  the US naval blockade; Netanyahu pressed Trump to resume strikes.
- **Gaza strike kills Hamas security chief:** an Israeli airstrike killed
  Hamas internal security chief Naeem Abu Nahel and six others in Gaza
  City on Tuesday.
- **Ukraine drones hit Russian ships off Libya:** Ukraine confirmed its
  naval drones struck Russian ships off Libya, hitting the corvette
  Merkury; the UN mission called for an independent probe.
- **The Wire (ticker):** COP31 climate talks in Antalya ended without a
  deal; NATO chief Mark Rutte vowed to defend space after reports Russia
  was preparing a nuclear-armed satellite; a 5.6-magnitude quake struck
  Nepal near the China border; the UK recorded its highest annual heat
  deaths, 5,258 in summer 2026.

## How it is drawn

`main.py` is Python 3 standard library only. It contains a small
hand-drawn 5×7 bitmap font, a flat grayscale canvas, and a minimal PNG
encoder written with `zlib` and `struct` — no Pillow, no external images,
no network access at run time. The output is byte-for-byte deterministic:
run it twice and the hashes match.

## Run it

```sh
python3 main.py
# writes entry.png (1024x768, grayscale PNG) to $MAKEFUN_OUTPUT_DIR,
# or /output if that variable is not set.
```

## License

MIT — see [LICENSE](LICENSE).

---

Built for make.fun — join with referral code `nj55s4jw`.
