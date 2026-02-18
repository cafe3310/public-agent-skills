import json
import os
import argparse
import sys

def read_file_content(path):
    """Safely read file content."""
    try:
        if not os.path.exists(path):
            return f"> Error: File not found at {path}"
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().strip()
    except Exception as e:
        return f"> Error reading file: {str(e)}"

def merge_docs(config_path):
    """
    Merges documents based on the provided JSON configuration.
    
    Config Schema:
    {
        "output_dir": "path/to/output",
        "tasks": [
            {
                "filename": "output_file.md",
                "title": "Main Document Title",
                "sections": [
                    {
                        "title": "Section Title", 
                        "path": "path/to/source_file.txt",
                        "syntax": "text"  // optional, default to markdown/text
                    }
                ]
            }
        ]
    }
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Failed to load config file: {e}")
        sys.exit(1)

    output_dir = config.get("output_dir", ".")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    for task in config.get("tasks", []):
        output_filename = task.get("filename")
        if not output_filename:
            continue

        output_path = os.path.join(output_dir, output_filename)
        doc_title = task.get("title", "Untitled Document")
        
        content_blocks = [f"# {doc_title}\n"]

        for section in task.get("sections", []):
            sec_title = section.get("title", "Untitled Section")
            src_path = section.get("path")
            syntax = section.get("syntax", "text")
            
            # Read content
            file_content = read_file_content(src_path)
            
            # Format as markdown section
            block = f"## {sec_title}\n\n```{syntax}\n{file_content}\n```\n"
            content_blocks.append(block)

        # Write final document
        try:
            with open(output_path, 'w', encoding='utf-8') as f_out:
                f_out.write("\n".join(content_blocks))
            print(f"✅ Generated: {output_path}")
        except Exception as e:
            print(f"❌ Failed to write {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge text files into structured Markdown documents based on a JSON plan.")
    parser.add_argument("config_file", help="Path to the JSON configuration file")
    args = parser.parse_args()

    merge_docs(args.config_file)
