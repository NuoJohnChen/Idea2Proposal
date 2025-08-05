import os
import re
from pathlib import Path
from typing import Dict, List

def process_text_files(source_dir: str, output_dir: str) -> None:
    """
    Extract research proposals from text files in the source directory, group them by topic,
    and write formatted versions to new files in the output directory.

    Args:
        source_dir (str): Path to the directory containing the original .txt files.
        output_dir (str): Path to the directory for storing the extracted .txt files.
    """
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    output_path.mkdir(exist_ok=True)
    print(f"Output directory '{output_path}' is ready.")

    if not source_path.is_dir():
        print(f"Error: Source directory '{source_path}' does not exist. Please check the path.")
        return

    topic_groups: Dict[str, List[Path]] = {}
    print(f"Scanning source directory '{source_path}'...")
    
    for file_path in source_path.glob('*.txt'):
        match = re.match(r'single_(.*?)_run\d+.*\.txt', file_path.name)
        if match:
            topic = match.group(1)
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(file_path)

    if not topic_groups:
        print("No files found in the source directory matching the 'single_topic_run...' format.")
        return
        
    print(f"Found {len(topic_groups)} topics: {', '.join(topic_groups.keys())}")

    for topic, files in topic_groups.items():
        proposals = []
        for file_path in sorted(files):
            try:
                content = file_path.read_text(encoding='utf-8')
                
                start_match = re.search(r'(1\.\s*Title:.*)', content, re.DOTALL)
                
                if start_match:
                    proposal_text = start_match.group(1)
                    proposal_text = re.sub(r'References:.*', '', proposal_text, flags=re.DOTALL).strip()
                    proposals.append(f"'''\n{proposal_text}\n'''")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        if proposals:
            paper_txts_content = "paper_txts = [\n    " + ",\n    ".join(proposals) + "\n]"
            output_file = output_path / f"{topic}_proposals.txt"
            
            try:
                output_file.write_text(paper_txts_content, encoding='utf-8')
                print(f"Successfully generated file: {output_file} (containing {len(proposals)} proposals)")
            except Exception as e:
                print(f"Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    SOURCE_DIR = "outputs" 
    OUTPUT_DIR = "extracted_proposals"
    
    process_text_files(SOURCE_DIR, OUTPUT_DIR)
