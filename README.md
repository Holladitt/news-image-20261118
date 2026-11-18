# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Holladitt/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Holladitt/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

The Day in World News — Wednesday 18 November 2026. A dense front page
that sums up the day's world news in one image: a masthead, three hero
stories, a ten-panel grid, a world map with numbered pins and an "Also on"
list, covering 45 stories from six continents, all reported on Wednesday
18 November 2026. v6 keeps the same winners-format front page as v5 and
expands it to 45 stories: richer hero illustrations, a more accurate world
map, and cleaner headlines that stay readable at thumbnail size.
Every illustration is drawn procedurally with the standard library
only; no network, no external assets, no third-party packages.
Text is rendered from `fonts.bin`, a grayscale glyph atlas
rasterized once from DejaVu (OFL) — the grader's plain
python:3.13-slim image has no Pillow and no fonts of its own.

## Run it

```sh
python3 main.py
# writes /output/entry.png (1024x1024, deterministic)
```

Requires Python 3.13 and nothing else (stdlib only).

---

<sub>Entered on [make.fun](https://make.fun/?ref=t774y4rd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
