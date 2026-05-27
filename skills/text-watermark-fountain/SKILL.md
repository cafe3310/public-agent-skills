---
name: text-watermark-fountain
description: A specialized skill for embedding and extracting resilient watermarks in text by manipulating sentence lengths and using Fountain Codes. Use this when the user wants to add a hidden, robust watermark to text or verify an existing one.
license: MIT
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - python3
---

# Text Watermark Fountain (Robust Sync-Frame Version)

This skill enables the Agent to embed a string watermark into a text such that it can be recovered even if the text is partially modified, segments are deleted, or new sentences are inserted. It uses a custom Luby Transform (LT) Fountain Code combined with **Sync Frames** to map the watermark into a sequence of target lengths.

## How it works (Robustness Mechanism)

1.  **Sync Markers**: The encoding script periodically inserts a unique length pattern `[19, 4, 19]` (Sync Marker) followed by a **Frame ID**.
2.  **Self-Synchronization**: The decoder searches the entire text for these markers using a sliding window. Even if middle segments are removed, the decoder can resynchronize using the next Sync Marker and know exactly which symbols it is looking at.
3.  **Redundancy**: By repeating these frames throughout a long text, the watermark becomes extremely difficult to destroy.

## Workflow: Embedding a Watermark

When a user asks to embed a watermark (e.g., "name_1") into a text:

1.  **Generate Length Sequence**:
    - Run the encoding script:
      ```bash
      python3 scripts/encode.py --mark "name_1" --count [TOTAL_DATA_SYMBOLS]
      ```
    - Note the `Lengths` output. It will contain periodic `19 4 19 [ID]` headers.

2.  **Precise Text Fine-tuning (Batch Processing)**:
    To ensure 100% accuracy, you MUST use a multi-stage approach:
    - **Step 2.1: Redundancy & Looping**: If the original text is significantly longer than the required length sequence, the script handles the symbol indexing. Just ensure you cover all target lengths.
    - **Step 2.2: Segmentation**: Split the source text into segments using allowed punctuation (`，。！？；：、, . ! ? ; :`).
    - **Step 2.3: Batch Delegation**: Use a **subagent** to rewrite segments in batches of 5-10.
      *   **Prompt for Subagent**: "Rewrite these segments to match EXACT character lengths: [L1, L2, ...]. Maintain meaning. NO internal punctuation allowed within a segment. Count every character (Chinese, English, digits) as 1."
    - **Step 2.4: Verification**: After each batch, run a Python one-liner to verify:
      ```bash
      python3 -c "print([len(s.strip()) for s in [SEG1, SEG2, ...]])"
      ```

3.  **Final Polishing & Formatting**:
    - **Step 3.1: Style Alignment**: Compare the verified segments with the original text. Refine phrasing to match the original's tone, but **STRICTLY** maintain the verified character count.
    - **Step 3.2: Paragraph Reconstruction**: Re-insert original line breaks. Paragraph breaks (\n) do not affect length measurement.

4.  **Output**:
   - Provide the final watermarked text to the user.

## Workflow: Extracting a Watermark

1. **Run Decoder**:
   - Pass the text to the decoding script:
     ```bash
     python3 scripts/decode.py --text "THE_TEXT_CONTENT"
     ```
   - The script will search for sync frames and use the LT decoder to recover the mark.

## Guidelines for the Agent

- **Precision is Absolute**: A single character error in a segment breaks that data symbol.
- **Punctuation is a Splitter**: Do NOT use punctuation inside a segment unless you intend to split it.
- **Sync Frames are Sacred**: The `19 4 19 [ID]` sequence must be embedded exactly as specified in the output of `encode.py`.
