import json
from openai import OpenAI
from ai_scientist.perform_review import load_paper, perform_review
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import os
import tiktoken


model = "deepseek-chat-64k"#"deepseek-chat-64k"#"deepseek-v3-128k"#"deepseek-v3"#"deepseek-chat:function"#"deepseek-v3"#"deepseek-chat:function"

def load_cached_lines(cache_file):
    cached_lines = set()
    if os.path.exists(cache_file):
        for file in os.listdir(cache_file):
            if file.endswith('.jsonl'):
                cached_lines.add(file.replace('.jsonl', ''))
    return cached_lines

def truncate_to_30000_tokens(text, encoder):
    # encoded_tokens = encoder.encode(text)
    # if len(encoded_tokens) > 30000:
    #     encoded_tokens = encoded_tokens[:30000]
    # return encoder.decode(encoded_tokens)
    return text

def process_line(line, cached_lines, cache_file, model, encoder, not_none_count):
    
    client = OpenAI(base_url="",
                    api_key="")

    entry = json.loads(line)
    paper_id = entry.get('article', f"paper_{not_none_count}")

    if paper_id in cached_lines:
        print(f"Cache exists for {paper_id}, skipping processing.")
        return None

    decision = entry.get('decision', None)
    
    if decision is not None:
        paper_content = entry['paper_content']
        # Truncate paper content to 30000 tokens
        paper_content = truncate_to_30000_tokens(paper_content, encoder)
        
        try:
            print("perform_review", not_none_count)
            review = perform_review(
                paper_content,
                model,
                client,
                num_reflections=1,
                num_fs_examples=1,
                num_reviews_ensemble=1,
                temperature=0,
            )
            entry.update({
                'predict_soundness': review["Soundness"],
                'predict_presentation': review["Presentation"],
                'predict_contribution': review["Contribution"],
                'predict_rating': review["Overall"],
                'predict_decision': review["Decision"],
                'predict_weaknesses': review["Weaknesses"]
            })  
        except:
            print("no_response_paper_id:",paper_id)

        paper_cache_file = os.path.join(cache_file, f"{paper_id}.jsonl")
        with open(paper_cache_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        cached_lines.add(paper_id)
        return json.dumps(entry, ensure_ascii=False) + '\n'
    else:
        return None

def submit_tasks(lines, cached_lines, cache_file, model, encoder):
    filtered_lines = []
    not_none_count = 0
    with ProcessPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(process_line, line, cached_lines, cache_file, model, encoder, not_none_count): line for line in lines}
        for future in tqdm(futures, total=len(lines)//32):
            result = future.result()
            if result is not None:
                filtered_lines.append(result)
                not_none_count += 1
    return filtered_lines

def main():
    
    input_file = ""
    output_file = ""
    cache_file = "/AI-Scientist/cache_deepseek_newxtra7b"

    
    encoder = tiktoken.get_encoding('cl100k_base')

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cached_lines = load_cached_lines(cache_file)
    
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for paper_id in cached_lines:
            paper_cache_file = os.path.join(cache_file, f"{paper_id}.jsonl")
            with open(paper_cache_file, 'r', encoding='utf-8') as cache_f:
                f.write(cache_f.read())

    filtered_lines = submit_tasks(lines, cached_lines, cache_file, model, encoder)

    with open(output_file, 'a', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    print(f"")

if __name__ == "__main__":
    main()