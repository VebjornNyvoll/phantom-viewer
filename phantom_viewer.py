#!/usr/bin/env python3
"""
Marathon ARG - phantom.cryoarchive.systems ASCII Art Viewer
Connect to the phantom WebSocket and render game room canvases.

Usage: pip install websocket-client Pillow && python phantom_viewer.py

Discovered game rooms:
  QUARANTINE (59x28) - Marathon logo
  mock (216x59) - Cyborg/Runner character  
  AiUplink (59x28) - Nearly blank
  50x100, 55x55, loadtest, first - Blank/test canvases
"""

import websocket
import struct
import time
import sys

GAME_IDS = ['QUARANTINE', 'mock', 'AiUplink', '55x55', '50x100']
PALETTE_DEFAULT = '.,/#MWx='

def connect_and_dump(game_id, timeout=10):
    url = f'wss://phantom.cryoarchive.systems/connect?gameId={game_id}'
    print(f'Connecting to {url}...')
    
    try:
        ws = websocket.create_connection(url, timeout=timeout)
    except Exception as e:
        print(f'  Connection failed: {e}')
        print(f'  (phantom may be temporarily offline)')
        return None
    
    # Read init message (21 bytes)
    data = ws.recv()
    if not isinstance(data, bytes) or len(data) < 21:
        print(f'  Unexpected init: {len(data) if isinstance(data, bytes) else type(data)}')
        ws.close()
        return None
    
    msg_type = data[0]
    tick = struct.unpack('>I', data[1:5])[0]
    players = struct.unpack('>I', data[5:9])[0]
    max_players = struct.unpack('>I', data[9:13])[0]
    palette = data[13:21].decode('ascii', errors='replace')
    
    print(f'  Connected! tick={tick} players={players}/{max_players} palette="{palette}"')
    
    # Request grid state
    ws.send(b'')
    time.sleep(1.5)
    
    try:
        grid_data = ws.recv()
    except:
        print(f'  No grid data received')
        ws.close()
        return None
    
    ws.close()
    
    if not isinstance(grid_data, bytes) or len(grid_data) < 8:
        print(f'  Invalid grid data: {len(grid_data)} bytes')
        return None
    
    # Parse grid: 6-byte header (2 padding + u16 width + u16 height) + packed 3-bit cells
    width = struct.unpack('>H', grid_data[4:6])[0]
    height = struct.unpack('>H', grid_data[6:8])[0]
    print(f'  Grid: {width}x{height}')
    
    # Decode 3-bit packed cells
    cell_data = grid_data[8:]
    cells = []
    for byte in cell_data:
        cells.append((byte >> 5) & 0x7)
        cells.append((byte >> 2) & 0x7)
        cells.append(((byte & 0x3) << 1))  # partial
    
    # Render ASCII art
    lines = []
    non_default = 0
    for y in range(height):
        line = ''
        for x in range(width):
            idx = y * width + x
            bit_offset = idx * 3
            byte_idx = bit_offset // 8
            bit_pos = bit_offset % 8
            
            if byte_idx < len(cell_data):
                if bit_pos <= 5:
                    val = (cell_data[byte_idx] >> (5 - bit_pos)) & 0x7
                else:
                    val = ((cell_data[byte_idx] & ((1 << (8 - bit_pos)) - 1)) << (bit_pos - 5))
                    if byte_idx + 1 < len(cell_data):
                        val |= cell_data[byte_idx + 1] >> (13 - bit_pos)
                    val &= 0x7
            else:
                val = 0
            
            char = palette[val] if val < len(palette) else '?'
            if val != 0:
                non_default += 1
            line += char
        lines.append(line)
    
    total = width * height
    pct = (non_default / total * 100) if total > 0 else 0
    print(f'  Non-default cells: {non_default}/{total} ({pct:.1f}%)')
    print()
    
    # Print ASCII art
    for line in lines:
        print(line)
    
    return lines

if __name__ == '__main__':
    game = sys.argv[1] if len(sys.argv) > 1 else 'QUARANTINE'
    print(f'=== phantom.cryoarchive.systems - Game: {game} ===')
    print()
    result = connect_and_dump(game)
    if result is None:
        print()
        print('Failed to retrieve canvas. phantom may be offline.')
        print('Known game IDs: QUARANTINE, mock, AiUplink, 55x55, 50x100, loadtest, first')
