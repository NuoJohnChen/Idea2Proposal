import os
import re

# Directory containing the summary files
results_dir = 'results'

# New directory for processed results
processed_dir = 'processed_results'
os.makedirs(processed_dir, exist_ok=True)

# Dictionary to hold topic -> list of (entry_num, content)
topic_data = {}

# Regex to parse filename: topic_entryX_summary.txt
filename_pattern = re.compile(r'^(?P<topic>.*?)_entry(?P<entry>\d+)_summary\.txt$')

# Iterate over all files in results_dir
for filename in os.listdir(results_dir):
    if filename.endswith('_summary.txt'):
        match = filename_pattern.match(filename)
        if match:
            topic = match.group('topic')
            entry_num = int(match.group('entry'))
            file_path = os.path.join(results_dir, filename)
            with open(file_path, 'r') as f:
                content = f.read().strip()
            if topic not in topic_data:
                topic_data[topic] = []
            topic_data[topic].append((entry_num, content))

# For each topic, sort by entry_num and write to file
for topic, entries in topic_data.items():
    # Sort by entry number
    entries.sort(key=lambda x: x[0])
    # Sanitize topic name for filename (replace commas, ampersands, etc. with underscores)
    safe_topic = re.sub(r'[,\s&()]+', '_', topic).strip('_')
    safe_topic = re.sub(r'_+', '_', safe_topic)  # Replace multiple underscores with single
    output_path = os.path.join(processed_dir, f'{safe_topic}.txt')
    with open(output_path, 'w') as out_f:
        for entry_num, content in entries:
            out_f.write(f'Entry {entry_num}:\n{content}\n\n')

    # Now compute averages
    score_categories = [
        'Overall Quality',
        'Argumentative Cohesion',
        'Intellectual Depth',
        'Execution Credibility',
        'Scientific Rigor'
    ]
    scores = {cat: [] for cat in score_categories}

    with open(output_path, 'r') as in_f:
        content = in_f.read()
        entry_blocks = re.split(r'Entry \d+:\n', content)
        for block in entry_blocks[1:]:  # Skip first empty
            lines = block.strip().split('\n')
            for line in lines:
                for cat in score_categories:
                    if line.startswith(cat + ':'):
                        try:
                            value = float(line.split(':')[1].strip())
                            scores[cat].append(value)
                        except ValueError:
                            pass

    # Compute averages
    averages = {}
    for cat in score_categories:
        if scores[cat]:
            avg = sum(scores[cat]) / len(scores[cat])
            averages[cat] = round(avg, 2)
        else:
            averages[cat] = 0.0

    # Append averages to the file
    with open(output_path, 'a') as out_f:
        out_f.write('\nAverages:\n')
        for cat, avg in averages.items():
            out_f.write(f'{cat}: {avg}\n')

    print(f'Processed topic "{topic}" into {output_path} with averages')

print('Processing complete.')
