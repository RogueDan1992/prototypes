# Door builder profile audit

Checked against the Fangda catalog (`Fiberglass door catalogue-2026.5.14.pdf`), one collection at a time.
Catalog drawings are small (oak cells are 52–142 px wide), so positions read from them are good to about
±0.3" (±0.5" on the smallest cells). Anything not settled by the catalog is marked **VERIFY**.

Status key: **rebuilt** = new line + relief from `doorgen.py` geometry · **relit** = geometry kept (already
matched the catalog), relief re-rendered with the new lighting · **open** = needs an answer before changing.

## Oak (K), page 08 — done (batch 1)

| Slab | Catalog check | Status |
|---|---|---|
| P00-K01 | flush | relit |
| P00-K01 #2 | full lite 2264, matches | rebuilt (lite frame) |
| P00-K01 #3 | narrow 0764 lite at hinge side, matches | rebuilt |
| P00-K05 SL | two full-height lines at 3.1" and 10.8" | **open** — VERIFY what the two lines are (V-grooves or just the sidelite frame); left as is |
| P00-K06 | horizontal planks, 10 boards in a 21.4" × 62" field | rebuilt (V-grooves) |
| P00-K07 | vertical planks, 6 boards | rebuilt (V-grooves; old drawing ran grooves through the rails) |
| P02-K01 SL | 2 raised panels, matches | relit |
| P02-K01 SL #2 | **new** — 836-lite oak glass sidelite (factory sheet MBL-K1-B/C: "P02-K01 sidelite w/ frame, lite 836") | art built; needs a database row. VERIFY lite position (drawn like CG02-K01: lite on top, P02-K01 bottom panel kept) |
| P02-K03 | 2 panel, matches | rebuilt |
| P02-K03 #2 | 2248 lite + bottom panel, matches | rebuilt (relief was disabled before) |
| P02-K05 SL | flat outlines (not raised), matches | rebuilt |
| P03-K01 | bell (cathedral) top panel + 2 small panels | rebuilt (old was wobbly) |
| P03-K01 #2 | same with oval lite inside | rebuilt (old was smudged). Glass shown clear; VERIFY the oval size (OVAL glass is in the glass catalog) |
| P03-K01 #3 | 2248 lite + 2 small panels | rebuilt |
| P03-K02 | flat outlines, 1 wide + 2 tall | rebuilt |
| P03-K03 | bell top **and** inverted-bell bottom + 2 small panels | rebuilt (old drawing was cut off) |
| P03-K03 #2 | same with oval lite | rebuilt; **database glass box is wrong** ([17.9, 12.5, 18, 44.3], lite 2248) — should match the oval |
| P04-K01 | 4 panel BT: tall top rail, panels 17.2–42.2" and 49.2–70.4" | rebuilt (old was faint) |
| P04-K01 cells b, c, d | catalog shows 3 glass versions: segment lite, camber lite, round-top lite over 2 panels | art built as P04-K01 #2/#3/#4; **not in the database** |
| P04-K01 SL, P04-K01 SL #2, P04-K03 SL | no matching catalog drawing; app images are gray smudges | **open** — the catalog cells these probably came from are the P04-K01 b–d doors above |
| P04-K03 | 4 panel, matches | relit |
| P04-K03-TN | catalog cell b: **two tall lites** over 2 panels (also the page-08 photo) | rebuilt with 2 lite frames; database has no glass for it — VERIFY lite size |
| P04-K03 #2 | 1/2 lite 2236 — same catalog image as CG02-K01 | rebuilt to match CG02-K01 |
| P06-K01 | 6 panel | **rebuilt — old drawing was stretched** (bottom panel ran into the bottom edge) |
| P06-K01 #2 | 2 small lites over 4 panels | rebuilt, lites match the database |
| P06-K10 | 6 panel, arched tops | relit (drawing already matched) |
| P08-K01, P08-K01 #2 | 8 panel arch | relit (drawing already matched); #2 gets an arch-top lite frame |
| CG02-K01 | 2236 cutout + 2 panels | relit; new relief now actually used (was on the skip list) |
| FG05-K01 | 5 horizontal lites | rebuilt; glass now clipped to each lite in the app |

## Line-drawing blur score, all slabs (mid-gray ÷ dark pixels; clean ≈ 1, bad > 4)

Oak is fixed; the rest is the worklist for the next batches (worst first). "inf" = drawn in light gray only.

```
P04-LS01_2.png     inf
P04-MS01.png       inf
P06-MS04_2.png     inf
P00-MS04_3.png     inf
P00-LS01_3.png     inf
P02-LS10_SL.png    inf
P00-MS04_SL.png    40.55
P00-LS01_SL.png    40.04
P06-MS04.png       21.28
P03-LS02_3.png     11.62
P03-LS02.png       10.63
P03-M05.png        10.49
P02-M01.png        10.44
P02-MS07.png       10.13
P02-MS11.png       10.07
P02-LS01.png       9.73
P02-LS07.png       9.68
P02-M17.png        9.56
P02-MS01.png       8.14
P00-F02.png        6.83
FG03-F03.png       6.12
P02-LS04.png       5.84
P02-MS09.png       5.77
P04-LS01.png       5.60
P03-LS03.png       4.97
P03-MS04.png       4.49
P02-LS03.png       4.44
P04-LS02.png       4.42
FG02-LS04.png      4.34
P02-LS02_2.png     4.23
P00-MS04_4.png     4.21
P00-LS01_4.png     4.21
P02-MS02_2.png     4.19
P03-F01.png        4.12
P03-M02.png        4.11
P03-LS01.png       4.11
FG05-LS02.png      4.05
P02-M04_2.png      3.97
FG00-MS04.png      3.83
FG06-LS01.png      3.63
CG02-LS01.png      3.56
FG00-M10.png       3.45
FG03-MS05.png      3.43
FG03-F02.png       3.39
FG03-LS03.png      3.38
FG05-M01.png       3.34
FG05-LS01.png      3.27
P06-LS01_2.png     3.12
P02-LS09_SL.png    2.96
P02-MS06_SL.png    2.93
P02-M15_SL.png     2.81
FG03-MS07.png      2.80
FG03-F04.png       2.78
FG00-M07_SL.png    2.68
P03-LS02_2.png     2.61
```
