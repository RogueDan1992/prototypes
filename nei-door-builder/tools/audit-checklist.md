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

## Mahogany (M), page 06 — done (batch 2)

| Slab | Catalog check | Status |
|---|---|---|
| P00-M01, P00-M02-N SL | flush | unchanged |
| P00-M01 #2 | full lite 2264 | rebuilt |
| P02-M01 | 2 panel plank, top panel slightly arched | rebuilt (was wobbly); planks as V-grooves |
| P02-M03 | rustic arch-top plank panels, speakeasy grille, clavos | relit; grille and studs shaded dark iron |
| P02-M04 | 2 panel | rebuilt |
| P02-M04 #2 | 2248 lite + bottom panel | rebuilt (was blurry, relief disabled) |
| P02-M08 | arch-top 2 panel | relit (drawing matched) |
| P02-M11 | 2 plank panels | rebuilt with V-grooves |
| P02-M15 SL | 2 panel sidelite | rebuilt |
| P02-M17 | 2 panel, narrower panels (7.7–28.3") | rebuilt (was wobbly, bottom panel misplaced) |
| P03-M01 | bell top + inverted-bell bottom, scroll panels | relit (drawing matched) |
| P03-M01 #2 | **catalog's 2nd P03-M01 cell: same with oval lite — not in the app** | art built; needs a database row |
| P03-M02 / #2 | Craftsman: flat panels / 2215 lite | rebuilt (P03-M02 was blurry) |
| P03-M05 | bell top + 2 small panels | rebuilt (was wobbly; same geometry as P03-K01) |
| P05-M01 | 5 vertical planks in one raised frame | rebuilt |
| P06-M01 | 6 panel | relit |
| P07-M01 | horizontal boards | rebuilt as grooves |
| P08-M01, #2, P08-M02 | 8 panel | relit; #2 gets its arch-top lite frame |
| FG00-M01 SL, FG00-M02 | full lite | rebuilt |
| FG00-M06 | 2264 lite, 2 × 4 grid | **rebuilt — old drawing and glass were stretched to the bottom edge.** VERIFY: grid bars drawn as wood muntins; may be a grille |
| FG00-M07 SL | 0764 lite, 4 panes | rebuilt (relief was disabled) |
| FG00-M10 | narrow lite | **rebuilt — was stretched to the bottom edge** |
| FG02-M01, FG03-M02 | — | done in the earlier batch |
| FG02-M05 | 2248 lite, 2 × 3 grid + bottom panel | **rebuilt — was stretched (panel ran to the bottom edge)** |
| FG02-M07 SL … FG02-M18 SL | glass sidelites | rebuilt, lites match the database |
| FG02-M09, FG02-M21, FG03-M01, FG04-M01 | glass doors | rebuilt, lites match the database |
| FG05-M01 | 5 horizontal lites | **rebuilt — old drawing and glass ran past the right edge** |

## Smooth (MS), page 11 left — done (batch 3)

Glass sizes here were measured from the catalog's glass fill colour (more reliable than reading lines).

| Slab | Catalog check | Status |
|---|---|---|
| P00-MS04, #2, #4 | flush / 2264 / narrow lite on the lock side | rebuilt |
| P00-MS04 #3 | **4 small lites stacked on the lock side** — app had it flush with no glass | rebuilt; needs glass in the database. VERIFY lite size |
| P00-MS04 SL | catalog cell is a **door** with a centered narrow lite, not a sidelite | art built as P00-MS04 #5; SL to hide |
| P02-MS01 | 2 plank panels | **rebuilt — old drawing was stretched sideways** |
| P02-MS02 / #2 | 2 panel / 2248 lite | rebuilt |
| P02-MS06 SL, P02-MS13 SL | 2 panel sidelites (raised / flat) | rebuilt |
| P02-MS07 | arch-top 2 panel (lower than P02-M08) | rebuilt (was wobbly) |
| P02-MS09 | flat 2 panel, tall top rail-free layout | rebuilt (was wobbly) |
| P02-MS11 | 2 panel, same layout as P02-M17 | rebuilt (was wobbly) |
| P03-MS04 | Craftsman flats | rebuilt (relief was disabled) |
| P04-MS01 | 4 panel BT, plus the same 3 glass versions as oak P04-K01 | rebuilt (was faint); glass versions art built as #2–#4 |
| P04-MS01 SL, SL #2 | no matching catalog drawing (same misread as oak) | to hide |
| P06-MS04 | 6 panel | rebuilt (was smudged) |
| P06-MS04 #2 | catalog: **2236 cutout over 2 panels** — app had a 6 panel with no glass | rebuilt; needs glass in the database |
| P06-MS04 SL | catalog cell is a **door with 2 tall lites** (like P04-K03-TN) | art built as P06-MS04 #3; SL to hide |
| FG00-MS02, -MS04, -MS06 SL, -MS09 | full / narrow / 3/4 lites | rebuilt |
| FG00-MS10 | 8-pane full lite — **stretched to the bottom edge** like FG00-M06 | rebuilt; database glass to fix |
| FG00-MS11 SL, FG02-MS02 SL … FG02-MS13 SL | glass sidelites | rebuilt |
| FG02-MS03, FG02-MS04 | glass + bottom panel | rebuilt |
| FG02-MS12 | 2236 lite + panel — **old drawing stretched** | rebuilt; database glass to fix |
| FG03-MS02, -MS05, -MS07 | Craftsman glass over 2 flat panels | rebuilt (were blurry) |
| FG03-MS06 | **3 lites over 2 flat panels — not in the app** | art built; needs a database row |

Correction to earlier batches: FG00-M06's 8-pane lite is 22.8" wide (measured from the glass fill), not 20";
P04-K01 #2's half-round lite starts at 5.0", P04-K01 #4's round top at 5.3".

## Line-drawing blur score, all slabs (mid-gray ÷ dark pixels; clean ≈ 1, bad > 4)

Oak, mahogany and MS are fixed; the rest is the worklist for the next batches (worst first). "inf" = drawn in light gray only.

```
P04-LS01_2.png     inf
P00-LS01_3.png     inf
P02-LS10_SL.png    inf
P00-LS01_SL.png    40.04
P03-LS02_3.png     11.62
P03-LS02.png       10.63
P02-LS01.png       9.73
P02-LS07.png       9.68
P00-F02.png        6.83
FG03-F03.png       6.12
P02-LS04.png       5.84
P04-LS01.png       5.60
P03-LS03.png       4.97
P02-LS03.png       4.44
P04-LS02.png       4.42
FG02-LS04.png      4.34
P02-LS02_2.png     4.23
P00-LS01_4.png     4.21
P03-F01.png        4.12
P03-LS01.png       4.11
FG05-LS02.png      4.05
FG06-LS01.png      3.63
CG02-LS01.png      3.56
FG03-F02.png       3.39
FG03-LS03.png      3.38
FG05-LS01.png      3.27
P06-LS01_2.png     3.12
P02-LS09_SL.png    2.96
FG03-F04.png       2.78
P03-LS02_2.png     2.61
```
