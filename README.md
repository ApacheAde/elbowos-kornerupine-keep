# Kornerupine Keep

Full-colour Python 3 neon tower-lite arcade for [ElbowOS](https://x.com/ElbowOS).

Plant crystal pylons on the keep pads. Each pylon lances prism moths falling in its column. Gold moths take two hits. If a moth reaches the gate, the shield cracks — the keep resets the shield so the run can continue.

A / D or arrows pick a column. W / S pick a row. Space plants. R restarts.

## Play

```bash
pip install -r requirements.txt
python3 kornerupine_keep.py --play
```

## Record a 9:16 reel

```bash
python3 kornerupine_keep.py
```

Writes a 15-second 1080x1920 H.264 MP4 (headless dummy video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1rEX5Eo5-1S-0Wt4uMrxF1oqZfmvD4-CH/view?usp=drivesdk

Not a Nintendo ROM or emulator. Original pylons, moths, and rules.
