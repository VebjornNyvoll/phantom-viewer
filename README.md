# phantom-viewer

Connects to `phantom.cryoarchive.systems` via WebSocket and decodes the collaborative ASCII art canvases from the Marathon ARG.

## What's on the canvases?

### QUARANTINE (59x28) — Marathon Logo

![QUARANTINE canvas](quarantine_render.png)

### mock (216x59) — Cyborg / Runner Character

![mock canvas](mock_render.png)

## How it works

phantom.cryoarchive.systems hosts collaborative pixel-art game rooms over binary WebSocket. Each cell is 3 bits packed into bytes, mapping to an 8-character ASCII palette (e.g. `.,/#MWx=`).

**Protocol:**
1. Connect to `wss://phantom.cryoarchive.systems/connect?gameId=<id>`
2. Receive 21-byte init message: type(1) + tick(u32) + players(u32) + max(u32) + palette(8 ASCII chars)
3. Send `\x01` to request grid state
4. Receive grid: 4 bytes padding + u16 width + u16 height + packed 3-bit cells

## Usage

```bash
pip install websocket-client
python phantom_viewer.py QUARANTINE
python phantom_viewer.py mock
```

## Known game rooms

| Game ID | Size | Content |
|---------|------|---------|
| QUARANTINE | 59x28 | Marathon logo (completed) |
| mock | 216x59 | Cyborg/Runner character |
| AiUplink | 59x28 | Nearly blank |
| 55x55 | 55x55 | Blank |
| 50x100 | 100x50 | Blank |
| loadtest | 300x100 | Blank |
| first | ? | No grid received |

> **Note:** phantom.cryoarchive.systems may be intermittently offline. If connections time out, try again later.
