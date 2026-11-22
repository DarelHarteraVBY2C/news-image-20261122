# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/DarelHarteraVBY2C/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/DarelHarteraVBY2C/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-page newspaper front page summing up world news for Sunday, 22 November 2026. Built for the [make.fun news-image-20261122 bounty](https://make.fun/bounty/news-image-20261122) ("Sum up 22 November's world news in one image", $100 in USDC).

## The front page

The lead story is Iran's strikes on US bases in Bahrain. The other stories on the page:

- **COP31 close to a final deal**, with an approval session at 06:00 GMT.
- **Eisenkot invites Likud to marathon coalition talks** in Israel.
- **The AI rout spreads to Asia**: Nikkei -5.1%, Kospi -5.5%, SoftBank -14.5%.
- **Hong Kong's Election Committee votes** (text brief): 856 candidates for 723 seats.

A strip along the bottom covers three tankers hit near Hormuz, the COP31 objections deadline, and the Change Bloc's 48 of 120 seats.

## How it works

`compose.py` lays out the four generated photo panels, the Hong Kong text brief, and the day's headlines into `entry.jpg` (1024×1024, under 1 MiB). `main.ts` validates that image and copies it to the output directory as `entry.png`.

```sh
python3 compose.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Running `main.ts` twice writes byte-identical output.

## License

MIT. See `LICENSE`.
