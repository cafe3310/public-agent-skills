import argparse
import sys
import os
from lt_code import LTEncoder

def string_to_nibbles(s):
    b = s.encode('utf-8')
    nibbles = []
    for byte in b:
        nibbles.append(byte >> 4)
        nibbles.append(byte & 0x0F)
    return nibbles

def main():
    parser = argparse.ArgumentParser(description="Encode a robust watermark with sync frames.")
    parser.add_argument("--mark", type=str, required=True, help="The watermark string.")
    parser.add_argument("--count", type=int, default=150, help="Target number of symbols (will be adjusted for frames).")
    parser.add_argument("--seed", type=int, default=42, help="Seed for the fountain code.")
    parser.add_argument("--frame_size", type=int, default=10, help="Symbols per sync frame.")
    
    args = parser.parse_args()
    
    nibbles = string_to_nibbles(args.mark)
    K_val = len(nibbles)
    checksum = 0
    for n in nibbles:
        checksum ^= n
        
    source_nibbles = [K_val >> 4, K_val & 0x0F, checksum >> 4, checksum & 0x0F] + nibbles
    K = len(source_nibbles)
    
    encoder = LTEncoder(source_nibbles, seed=args.seed)
    
    # Sync Marker: [19, 4, 19]
    SYNC_MARKER = [19, 4, 19]
    
    lengths = []
    symbol_idx = 0
    frame_idx = 0
    
    while symbol_idx < args.count:
        # Insert Sync Frame Header
        lengths.extend(SYNC_MARKER)
        # Frame index nibble (0-15 mapped to 4-19)
        lengths.append((frame_idx % 16) + 4)
        
        # Insert Data Symbols
        for _ in range(args.frame_size):
            val, _ = encoder.generate_symbol(symbol_idx)
            lengths.append(val + 4)
            symbol_idx += 1
            if symbol_idx >= args.count:
                break
        frame_idx += 1
    
    print(f"K={K}")
    print(f"Seed={args.seed}")
    print(f"FrameSize={args.frame_size}")
    print("Lengths:", " ".join(map(str, lengths)))

if __name__ == "__main__":
    main()
