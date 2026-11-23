USFans rebrand of the earlier GTBuy videos (originals stay untouched in the repo root).
Rules from the creator: brand GTBuy -> USFans everywhere on screen, GTBuy logo removed, PayPal -> Klarna (own type, pink),
offer numbers (2x40 %, 2x30 %, 4 statt 3 Coupons, 6-7 / 1-3 Tage, "seit Monaten") removed from the picture but left in the
spoken audio, the spoken word "GTBuy" (and "PayPal" in v8/v9) soft-muted with a short swoosh (mute_words.py).
Done: v4, v5, v6, v7, v11 (render scripts here; v5/v6/v7/v11 = original scripts with the text swap, render4_us.py for v4).
Prepared, waiting for new link screenshots + USFans logo: v8, v9, v10, v12, v13 (render*_us.py created by patch_th.py;
logo file img/brand_logo.png, screenshot highlight boxes in hl_us.json).
Mute windows (output seconds): v4 9.74-10.44 | v8 1.42-1.84, 5.15-5.50, 15.70-16.14, PayPal 17.32-17.92 |
v9 GTBuy 3.24-3.68, PayPal 1.84-2.26, 6.12-6.46, 11.70-11.94 | v10 18.47-19.04 | v12 7.02-7.46 | v13 0.00-0.75

Update: the creator recorded "USFans" himself (voice/take1-6.wav, cut from his recording, light denoise).
splice_words.py mutes the old word and drops a take in its place (time-fitted with atempo, level-matched).
v4 now uses take6 at 9.74-10.44 (stretch x1.10). PayPal in v8/v9 stays muted (no Klarna recording).
Planned splice windows for the remaining videos: v8 1.42-1.88, 5.15-5.55, 15.70-16.14 | v9 3.24-3.70 | v10 18.47-19.04 |
v12 7.02-7.50 | v13 0.00-0.75.

Update: creator recorded "Klarna" (voice/klarna_a.wav, klarna_b.wav = cleanest takes 3+4, ~0.5 s).
PayPal spots in v8 (17.32-17.92) and v9 (1.84-2.26, 6.12-6.46, 11.70-11.94 -> widen to ~11.66-12.02)
will be spliced with these instead of muted.
