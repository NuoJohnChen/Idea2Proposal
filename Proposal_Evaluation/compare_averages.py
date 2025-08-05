import os
import re

# Directories
multi_dir = 'processed_resultsmrec2'
single_dir = 'processed_resultssrec2'
comparison_dir = 'comparison_results_mrec2'
os.makedirs(comparison_dir, exist_ok=True)

# Score categories
score_categories = [
    'Overall Quality',
    'Argumentative Cohesion',
    'Intellectual Depth',
    'Execution Credibility',
    'Scientific Rigor'
]

# Function to parse averages from a file
def parse_averages(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # Find the Averages section
    match = re.search(r'Averages:\n(.*)', content, re.DOTALL)
    if not match:
        return None
    avg_lines = match.group(1).strip().split('\n')
    averages = {}
    for line in avg_lines:
        if ':' in line:
            cat, value = line.split(':', 1)
            cat = cat.strip()
            try:
                averages[cat] = float(value.strip())
            except ValueError:
                pass
    return averages

# Get list of topic files from multi_dir (assuming same in single_dir)
topic_files = [f for f in os.listdir(multi_dir) if f.endswith('.txt')]

# Initialize overall sums
overall_diffs = {cat: 0.0 for cat in score_categories}

for topic_file in topic_files:
    multi_path = os.path.join(multi_dir, topic_file)
    single_path = os.path.join(single_dir, topic_file)
    
    if not os.path.exists(single_path):
        print(f'Skipping {topic_file}: missing in single_dir')
        continue
    
    multi_avgs = parse_averages(multi_path)
    single_avgs = parse_averages(single_path)
    
    if not multi_avgs or not single_avgs:
        print(f'Skipping {topic_file}: unable to parse averages')
        continue
    
    differences = {}
    for cat in score_categories:
        if cat in multi_avgs and cat in single_avgs:
            differences[cat] = round(multi_avgs[cat] - single_avgs[cat], 2)
        else:
            differences[cat] = 0.0
    
    # Write differences to file
    output_path = os.path.join(comparison_dir, topic_file.replace('.txt', '_diff.txt'))
    with open(output_path, 'w') as out_f:
        out_f.write('Differences (multi - single):\n')
        for cat, diff in differences.items():
            out_f.write(f'{cat}: {diff}\n')
            overall_diffs[cat] += diff
    print(f'Processed differences for {topic_file} into {output_path}')

# Write overall differences
overall_path = os.path.join(comparison_dir, 'overall_diff.txt')
with open(overall_path, 'w') as out_f:
    out_f.write('Overall Differences (multi - single) across all topics:\n')
    for cat, total_diff in overall_diffs.items():
        out_f.write(f'{cat}: {round(total_diff, 2)}\n')
print(f'Processed overall differences into {overall_path}')

print('Comparison complete.')