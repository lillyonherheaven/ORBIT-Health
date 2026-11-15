# P3-UI verification checklist

All fixture values, sampling schedules, baseline bands, freshness windows and
scripted persistence windows are ILLUSTRATIVE DEMO VALUE.

## Automated verification

From repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest
npm --prefix frontend test
npm --prefix frontend run build
```

Frontend coverage: deterministic fixtures and stable historical observations;
missing/suspect/invalid/stale/cached/unknown-source handling; scenario A delay;
declared-event priority; noise exclusion; missing eye input; crew isolation;
adherence-only streaks; separate tx/delivery/ack; API failure without fallback;
service-worker shell discovery, cached-response marker, and POST isolation.
Python additionally validates frontend observations and alerts against frozen
Pydantic contracts. Existing regression tests are retained.

## Browser checks executed

- Dashboard rendered at the browser's approximately 730px viewport.
- Judge Scenario B displayed RED priority action above the other panels.
- Open Procedure displayed bundled PB-RAD version 1 and illustrative labeling.
- Body hotspot opened the Head & eyes drawer and related observations.
- Selecting Local API removed all simulated readings and displayed GRAY.

## Remaining manual browser checklist

1. Run `npm --prefix frontend run dev`; open the printed localhost URL.
2. Test desktop 1440px, narrow 390px, keyboard-only navigation and reduced motion.
3. Open each of six body regions; use Escape and Tab in drawers/procedures.
4. Judge: A then +24 hours gives scripted ORANGE. Reset; B gives immediate RED.
   Reset; C queues events while link is down and makes A01 eye input GRAY.
5. Restore link: sent/pending/none. Advance +1 hour: sent/delivered/none.
   Acknowledge separately. Check the audit trail and overlapping outbox counts.
6. Disable/corrupt each sensor and inspect the corresponding chart gaps. A noisy
   heart-rate point is suspect and creates only a GRAY quality-review event.
7. Switch each chart among 24-hour, 7-day and 10-day windows; inspect tooltips,
   scenario lines, baseline labels and the accessible data table.
8. Submit a fictional check-in; confirm success and streak. Changing symptoms
   must never change reward. RED hides adherence widgets. Reload preserves demo.
9. `npm --prefix frontend run build`; `npm --prefix frontend run preview`.
   Load once online, reload after worker activation, then use browser offline
   mode and reload. Verify shell, charts, playbooks and simulation remain usable.
10. After future backend routes exist, test cached responses during actual API
    outage and confirm GRAY. Cached API responses never enable acknowledgement.
11. Inspect Network for same-origin assets only; no CDN, remote fonts or API calls.
12. Verify installed PWA behavior on intended judging browsers. Installation and
    actual offline browser reload have not been verified in this session.

## Integration boundaries

Only GET /api/health exists. api.js centralizes future route calls and preserves
X-Role, DailyCheckin and acknowledgement payloads. Status/outbox/gamification
response envelopes are not frozen in executable backend models. The status
adapter currently requires a timezone-bearing `now` simulated-clock field and
boolean `link`; this is an explicitly provisional UI boundary, not a contract
change or an implemented endpoint. Future response mapping must be agreed when
those routes are implemented. No live backend integration is claimed.

Demo data is generated locally by a fixed seeded UI fixture, not the P2 source
or BRSMPT. It is intentionally simpler and uses hourly illustrative snapshots.
Good observations without an evaluated state remain GRAY. Baseline bands are
fixture references, not learned personal baselines. Judge scripts do not validate
persistence rules or perform scientific risk evaluation. Reload restores the
local demonstration state; reset clears only that demo. No API writes are queued
or replayed automatically while offline. The displayed role is a demo identity,
not authentication or access-control enforcement.

Additional executed browser checks: desktop width 1440px and narrow content width
375px both have document scrollWidth equal to clientWidth. A chart-grid overflow
found during the narrow check was fixed and rechecked successfully.

## 3D anatomy revision checklist

- Open the production overview and confirm a WebGL canvas, visible organs,
  skeletal depth, projector and six pins. Confirm the region list and disclaimer
  stay usable even if WebGL fails to initialize.
- Drag the body and observe the pins move with the view. Scroll or pinch to zoom.
  Double-click the view or use Reset view. Wait for idle rotation to resume,
  then toggle Auto-rotate to hold the camera steady.
- Open each pin using both keyboard and pointer. Watch the camera focus, confirm
  the matching drawer opens and check that status includes an icon and text.
- Inject a missing, corrupt or suspect heart-rate reading. Confirm the heart
  remains static, then reset the simulation and confirm the beat resumes.
  Enable reduced motion and confirm the automatic animation stops.
- Use a standard WebGL-capable browser to verify a reheated production cache.
  Build and preview, load once on localhost, confirm service-worker activation
  in the browser, then disconnect or stop the preview server and reload normally.
  Confirm the WebGL scene and six pins still load. The in-app browser stopped-
  server reload was inconclusive for service-worker activation.

## Slate refinement

1. Open the production overview. Check the front-facing anatomy, six pins, and
   hover and keyboard focus tooltips. Verify the mission day and clock stay
   visible on a narrow viewport.
2. Open Heart & chest. Select seven days. Check the chart and its labeled
   illustrative reference. Switch metric tabs and look for gaps after a fault.
3. In the seeded console inject Scenario A and advance 24 hours
   (ILLUSTRATIVE DEMO VALUE). Confirm the leg pin is ORANGE and its drawer
   exposes the matching procedure action. Check that Hands stays GRAY.
4. Switch to Local API mode without the future endpoints. Confirm unavailable
   readings stay GRAY. Use Open seeded simulation to select the mock explicitly.
5. For offline launch, use a browser with active service-worker support. Load
   the production preview, confirm the worker is activated, set the browser
   offline and reload. Verify the shell, chart and six pins. The server-stopped
   in-app check returned a blank page. The automated cache harness passed.

## Automated Chromium offline verification

From the repository root, run the production build and start the preview in a
terminal:

~~~powershell
npm --prefix frontend run build
npm --prefix frontend run preview -- --port 4181 --strictPort
~~~

Use a separate terminal with Node 20 and a locally installed Chromium browser:

~~~powershell
node --experimental-websocket frontend/tests/offline-browser.mjs 'C:\Program Files\Google\Chrome\Application\chrome.exe' http://127.0.0.1:4181/
~~~

Expected: Chromium offline navigation and reload passed: shell, six pins,
charts, drawer and offline banner. The test requires a production preview on
loopback. It uses a clean test profile and leaves the regular browser profile
untouched. It waits for worker activation before disabling HTTP caching and
loading again offline. This supersedes the earlier in-app browser limitation
for standard Chromium, while in-app offline launch and PWA installation remain
unverified.

