# Mobile startup performance investigation (2026-09-13)

The [2026-09-10 audit](../../output/ui-audit-2026-09-10/performance-evidence.json) recorded desktop first contentful paint (FCP) at 1,548 ms and mobile at 10,556 ms, with 104 resources in each run. Its companion DOM evidence shows a Vite development server and failed `/api/auth/refresh`, cart, and hot-product calls. The file does not record viewport width, cache state, throttling, or a request waterfall; desktop `load: 0` also means the captures did not finish at the same lifecycle point. The 104 requests reflect the development module graph, not 104 mobile-only downloads. A production Home build requested 14 resources in the controlled captures below; its lazy 3D chunk was not among them.

Two independent startup dependencies were isolated on the pre-fix production build. A deterministic 10,000 ms response delay **only** on the Google Fonts CSS URL reproduced the old pattern at 390px: DOMContentLoaded 10,058 ms, FCP 10,116 ms, hero visible 10,255 ms. The stylesheet in `index.html` blocked parsing and paint even with `display=swap` in its URL. A 10,000 ms delay **only** on `/api/auth/refresh` gave FCP 112 ms but held the Home hero until 10,219 ms because the public-route guard awaited `hydrateSession()`. The old audit cannot prove which of these delays occurred on September 10; these probes show each mechanism and explain why the matching DCL/FCP timing is especially consistent with a slow stylesheet.

The fix loads Noto Sans SC after the initial page load so the existing system-font fallback paints immediately. Public routes start session restoration without awaiting it. Protected, guest, cart, and checkout routes still await it; the cart fetch waits before choosing a guest session ID or authenticated identity. A restored admin on Home is redirected after hydration. Catalog requests, DIY 3D fallback/retry, pricing, cart mutation logic, checkout calculations, and accessibility controls were left intact.

## Controlled before/after

All timings are milliseconds from navigation start, one cold Chromium context per viewport, production Vite preview on `127.0.0.1:4173`, local API fixtures, no CPU/network throttling, and an intentionally delayed *empty* font stylesheet. These are controlled regression probes, not real-device field metrics. Full request timings and transfer sizes are in [before-font-delay.json](../../output/mobile-startup-2026-09-13/before-font-delay.json) and [after-font-delay.json](../../output/mobile-startup-2026-09-13/after-font-delay.json).

| Viewport | FCP before | FCP after | Home hero before | Home hero after | Resources before/after |
| --- | ---: | ---: | ---: | ---: | ---: |
| Desktop 1280px | 10,120 | 128 | 10,232 | 214 | 14 / 14 |
| Mobile 360px | 10,108 | 84 | 10,228 | 175 | 14 / 14 |
| Mobile 390px | 10,100 | 84 | 10,219 | 174 | 14 / 14 |
| Mobile 430px | 10,084 | 80 | 10,187 | 168 | 14 / 14 |

With only refresh delayed 10,000 ms at 390px, FCP was 112 → 96 ms and the hero was 10,219 → 187 ms; see [before-auth-delay-390.json](../../output/mobile-startup-2026-09-13/before-auth-delay-390.json) and [after-auth-delay-390.json](../../output/mobile-startup-2026-09-13/after-auth-delay-390.json). Three undelayed runs per viewport after the fix had median FCP / hero times of 104 / 198 ms desktop, 84 / 170 ms at 360px, 84 / 174 ms at 390px, and 84 / 173 ms at 430px ([after-normal.json](../../output/mobile-startup-2026-09-13/after-normal.json)). Local preview timings do not predict mobile cellular performance; the reproducible result is that either slow dependency no longer gates the public Home hero.

## Reproduce

From `ecommerce/frontend`, run `npm run build`, then `npm run preview -- --host 127.0.0.1` in a separate terminal. With preview running, use `npm run perf:startup -- --runs=3 --out=../../output/mobile-startup-2026-09-13/after-normal.json` for undelayed captures or add `--font-delay-ms=10000` or `--auth-delay-ms=10000` to isolate either dependency. The [measurement script](../../ecommerce/frontend/scripts/measure-startup.mjs) fixes API responses, locale, color scheme, device scale factor, viewport sizes, and cache isolation and records navigation, paint, resource and hero timing. The dated `before-*` files were captured from the pre-fix build with this same script.

Validation: `npm run check` passed (typecheck, 124 Vitest tests, production build); `npm run test:e2e:diy-mobile` passed 12 cases across 360/390/430px for scrolling, WebGL fallback, retry and reduced motion; `npm run test:e2e:startup` passed 3 cases proving Home renders while refresh is pending and then restores admin routing and authenticated cart identity. The existing Vitest suite also covers catalog filters, pricing provenance, cart, checkout, session handling and navigation accessibility.
