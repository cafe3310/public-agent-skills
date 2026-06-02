import argparse
import sys
import re
from lt_code import LTDecoder

def extract_lengths(text):
    segments = re.split(r'[，。！？；：、, . ! ? ; :]', text)
    lengths = []
    for s in segments:
        s = s.strip()
        if s:
            lengths.append(len(s))
    return lengths

def nibbles_to_string(nibbles):
    if len(nibbles) % 2 != 0:
        nibbles = nibbles[:-1]
    bytes_list = []
    for i in range(0, len(nibbles), 2):
        byte = (nibbles[i] << 4) | nibbles[i+1]
        bytes_list.append(byte)
    try:
        return bytes(bytes_list).decode('utf-8')
    except:
        return None

def verify_mark(res):
    if not res: return None
    data_len = (res[0] << 4) | res[1]
    if data_len > len(res) - 4: return None
    checksum_val = (res[2] << 4) | res[3]
    actual_checksum = 0
    for n in res[4:4+data_len]:
        actual_checksum ^= n
    if actual_checksum == checksum_val:
        return nibbles_to_string(res[4:4+data_len])
    return None

def try_decode(K, symbols_with_idx, seed):
    decoder = LTDecoder(K, seed=seed)
    for idx, val in symbols_with_idx:
        if decoder.add_symbol(val, idx):
            break
    res = decoder.get_result()
    return verify_mark(res)

def main():
    parser = argparse.ArgumentParser(description="Decode a robust watermark using sync frames.")
    parser.add_argument("--file", type=str)
    parser.add_argument("--text", type=str)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--K", type=int)
    parser.add_argument("--frame_size", type=int, default=10)
    
    args = parser.parse_args()
    content = ""
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f: content = f.read()
    elif args.text:
        content = args.text
    else:
        content = sys.stdin.read()
    
    if not content:
        sys.exit(1)
        
    lengths = extract_lengths(content)
    SYNC_MARKER = [19, 4, 19]
    
    # Collect symbols and their absolute indices based on frames
    extracted_symbols = []
    i = 0
    while i < len(lengths) - 4:
        if lengths[i:i+3] == SYNC_MARKER:
            frame_id = lengths[i+3] - 4
            # We don't know the full frame index if it wrapped (0-15), 
            # but we can assume sequential frames for now or try multiples of 16.
            # For simplicity, we'll try to guess absolute frame index based on position if needed,
            # but usually the first few cycles will be within 0-15.
            base_symbol_idx = frame_id * args.frame_size
            for j in range(args.frame_size):
                if i + 4 + j < len(lengths):
                    val = lengths[i+4+j] - 4
                    if 0 <= val <= 15:
                        extracted_symbols.append((base_symbol_idx + j, val))
            i += 4 + args.frame_size
        else:
            i += 1
            
    if not extracted_symbols:
        print("Error: No sync frames found.", file=sys.stderr)
        sys.exit(1)

    if args.K:
        mark = try_decode(args.K, extracted_symbols, args.seed)
        if mark: print(f"Decoded Mark: {mark}")
        else: print("Failed.")
    else:
        print("Searching for K...", file=sys.stderr)
        for k_guess in range(5, 260):
            mark = try_decode(k_guess, extracted_symbols, args.seed)
            if mark:
                print(f"K found: {k_guess}")
                print(f"Decoded Mark: {mark}")
                return

if __name__ == "__main__":
    main()
