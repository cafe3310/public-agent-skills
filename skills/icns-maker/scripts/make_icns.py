#!/usr/bin/env python3
"""
make_icns.py
Convert PNG images to standard macOS .icns files following macOS Big Sur+ guidelines.
Subject is automatically scaled to 824x824 inside a 1024x1024 canvas to provide standard
transparent padding (squircle grid margin) unless --full-bleed is specified.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ICONSET_SPECS = [
    ("icon_16x16.png", 16),
    ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32),
    ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128),
    ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256),
    ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512),
    ("icon_512x512@2x.png", 1024),
]


def check_prerequisites():
    for cmd in ["sips", "iconutil"]:
        if not shutil.which(cmd):
            sys.exit(f"Error: Required macOS tool '{cmd}' not found in PATH.")


def get_image_size(path):
    res = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
        capture_output=True,
        text=True,
    )
    w_match = re.search(r"pixelWidth:\s*(\d+)", res.stdout)
    h_match = re.search(r"pixelHeight:\s*(\d+)", res.stdout)
    w = int(w_match.group(1)) if w_match else 0
    h = int(h_match.group(1)) if h_match else 0
    return w, h


def find_masters_in_dir(dir_path):
    """
    Scans directory for PNG files.
    Groups multi-resolution sets (e.g. prefix-1024@1x.png, prefix-512@1x.png)
    and selects the highest resolution master.
    Also collects standalone PNG files.
    """
    entries = [f for f in os.listdir(dir_path) if f.lower().endswith(".png") and not f.startswith(".")]
    if not entries:
        return []

    # Regex to recognize iOS/macOS export resolution suffixes
    pattern = re.compile(r"^(.*?)[-_](\d+(?:\.\d+)?)(?:@\d+x)?\.png$", re.IGNORECASE)
    groups = {}
    standalones = []

    for f in entries:
        full = os.path.join(dir_path, f)
        m = pattern.match(f)
        if m:
            prefix = m.group(1)
            # parse numeric size
            try:
                sz_val = float(m.group(2))
            except ValueError:
                sz_val = 0
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append((sz_val, full))
        else:
            standalones.append(full)

    masters = []
    # Pick highest resolution in each group
    for prefix, file_list in groups.items():
        file_list.sort(key=lambda x: x[0], reverse=True)
        best_file = file_list[0][1]
        out_name = f"{prefix}.icns"
        masters.append((best_file, out_name))

    for f in standalones:
        base = os.path.splitext(os.path.basename(f))[0]
        masters.append((f, f"{base}.icns"))

    masters.sort(key=lambda x: x[1])
    return masters


def build_icns_from_png(src_png, out_icns, subject_size=824, full_bleed=False, backup=False, verbose=False):
    check_prerequisites()

    if backup and os.path.exists(out_icns):
        parent = os.path.dirname(os.path.abspath(out_icns))
        backup_dir = os.path.join(parent, "backup_fullbleed_icns")
        os.makedirs(backup_dir, exist_ok=True)
        backup_target = os.path.join(backup_dir, os.path.basename(out_icns))
        shutil.copy2(out_icns, backup_target)
        if verbose:
            print(f"  [Backup] Saved existing icon to {backup_target}")

    with tempfile.TemporaryDirectory(prefix="icns_maker_") as tmpdir:
        master_1024 = os.path.join(tmpdir, "master_1024.png")

        if full_bleed or subject_size >= 1024:
            # Direct resize to 1024x1024 without extra padding
            subprocess.run(["sips", "-z", "1024", "1024", src_png, "--out", master_1024], check=True, stdout=subprocess.DEVNULL)
        else:
            # Scale subject down and pad canvas with transparent border
            scaled = os.path.join(tmpdir, "scaled.png")
            subprocess.run(["sips", "-z", str(subject_size), str(subject_size), src_png, "--out", scaled], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["sips", "--padToHeightWidth", "1024", "1024", scaled, "--out", master_1024], check=True, stdout=subprocess.DEVNULL)

        # Build .iconset directory
        base_name = os.path.splitext(os.path.basename(out_icns))[0]
        iconset_dir = os.path.join(tmpdir, f"{base_name}.iconset")
        os.makedirs(iconset_dir, exist_ok=True)

        for filename, sz in ICONSET_SPECS:
            dest = os.path.join(iconset_dir, filename)
            if sz == 1024:
                shutil.copyfile(master_1024, dest)
            else:
                subprocess.run(["sips", "-z", str(sz), str(sz), master_1024, "--out", dest], check=True, stdout=subprocess.DEVNULL)

        # Compile with iconutil
        os.makedirs(os.path.dirname(os.path.abspath(out_icns)), exist_ok=True)
        subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", out_icns], check=True)

    file_size = os.path.getsize(out_icns)
    return file_size


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG icons to standard macOS .icns files with proper Big Sur padding (824px inside 1024px)."
    )
    parser.add_argument("inputs", nargs="+", help="Input PNG file(s) or directory containing PNG exports.")
    parser.add_argument("-o", "--output", help="Output .icns file path or destination directory.")
    parser.add_argument(
        "--subject-size",
        type=int,
        default=824,
        help="Target size for icon subject inside 1024x1024 canvas (default: 824).",
    )
    parser.add_argument(
        "--full-bleed",
        action="store_true",
        help="Do not add transparent padding (use full 1024x1024 canvas).",
    )
    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Backup existing .icns files before overwriting.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )

    args = parser.parse_args()

    tasks = []
    for inp in args.inputs:
        if os.path.isdir(inp):
            found = find_masters_in_dir(inp)
            for src, out_name in found:
                if args.output:
                    if os.path.isdir(args.output) or len(args.inputs) > 1 or len(found) > 1:
                        target = os.path.join(args.output, out_name)
                    else:
                        target = args.output if args.output.lower().endswith(".icns") else os.path.join(args.output, out_name)
                else:
                    target = os.path.join(inp, out_name)
                tasks.append((src, target))
        elif os.path.isfile(inp):
            if args.output:
                if os.path.isdir(args.output):
                    base = os.path.splitext(os.path.basename(inp))[0]
                    target = os.path.join(args.output, f"{base}.icns")
                else:
                    target = args.output
            else:
                base = os.path.splitext(os.path.basename(inp))[0]
                # clean resolution suffix if single file
                base = re.sub(r"[-_]\d+(?:\.\d+)?(?:@\d+x)?$", "", base)
                target = os.path.join(os.path.dirname(inp) or ".", f"{base}.icns")
            tasks.append((inp, target))
        else:
            print(f"Warning: Input path '{inp}' does not exist, skipping.", file=sys.stderr)

    if not tasks:
        sys.exit("No PNG files found to process.")

    print(f"Processing {len(tasks)} icon(s) [Subject: {args.subject_size}px, Full-bleed: {args.full_bleed}]...")
    for src, dst in tasks:
        try:
            sz = build_icns_from_png(
                src,
                dst,
                subject_size=args.subject_size,
                full_bleed=args.full_bleed,
                backup=args.backup,
                verbose=args.verbose,
            )
            print(f"  ✓ {os.path.basename(dst)} ({sz:,} bytes) <- {os.path.basename(src)}")
        except Exception as e:
            print(f"  ✗ Failed processing {src}: {e}", file=sys.stderr)

    print("Completed.")


if __name__ == "__main__":
    main()
