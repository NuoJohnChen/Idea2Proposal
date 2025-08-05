from openai import OpenAI
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
import logging
from ast import literal_eval
import numpy as np


client = OpenAI(base_url="",
                api_key="")

model = "o1-mini"

EXAMPLES_DIRS = [
    'examples_single_o1mini_qwen',
    'examples_single_dsv3_qwen',
    'examples_multi_dsv3_qwen',
]


logging.basicConfig(filename='processing_o1mini.log', level=logging.INFO, format='%(asctime)s - %(message)s')


META_REVIEW_PROMPT_TEMPLATE = """
You are an expert AI scientist acting as a meta-reviewer. You have been given {reviewer_count} independent reviews of a single research proposal.
Your task is to synthesize these reviews into a single, comprehensive, and balanced final review.
Identify the consensus points, acknowledge disagreements, and produce a definitive evaluation in the required JSON format.

Here are the {reviewer_count} reviews:
{reviews_text}

Please provide the final meta-review in the following JSON format. Ensure all fields are included, even if some (like Weaknesses) are empty lists. Do not add any text before or after the JSON object.

{{
  \"Novelty\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Workability\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Relevance\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Specificity\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Integration_Depth\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Strategic_Vision\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Methodological_Rigor\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Argumentative_Cohesion\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Overall_Quality\": {{
    \"score\": <float>
  }},
  \"Weaknesses\": [
    \"<string>\",
    \"<string>\"
  ],
  \"Decision\": \"<string>\"
}}
"""

REFLECTION_PROMPT_TEMPLATE = """
You are an expert AI scientist. You have just produced the following review.
Your task is to critically reflect on it. Are there any weaknesses in your own evaluation? Is the justification strong enough? Is the decision well-supported?
Improve your review based on this self-reflection.

PREVIOUS REVIEW:
```json
{previous_review_json}
```

If you believe your review is already perfect and requires no changes, simply repeat the previous JSON EXACTLY and write \"I am done\" in the justification for the 'Novelty' field.
Otherwise, provide the new, improved review in the following JSON format. Ensure all fields are included, even if some (like Weaknesses) are empty lists.

{{
  \"Novelty\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Workability\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Relevance\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Specificity\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Integration_Depth\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Strategic_Vision\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Methodological_Rigor\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Argumentative_Cohesion\": {{
    \"score\": <float>,
    \"justification\": \"<string>\"
  }},
  \"Overall_Quality\": {{
    \"score\": <float>
  }},
  \"Weaknesses\": [
    \"<string>\",
    \"<string>\"
  ],
  \"Decision\": \"<string>\"
}}
"""

# 基础评审提示词 (从您的代码中提取并模块化)
BASE_REVIEW_PROMPT = """
You are an expert AI scientist reviewing a research proposal. Your task is to provide a structured, quantitative review based on a specific framework.

**IMPORTANT CONTEXT ON PROPOSAL ORIGIN**: The proposal you are about to review is the outcome of a collaborative process and may have been guided by a **Leader**, a **Multi-Person** group, or a **Single-Person**. A proposal guided by a **Leader** represents a highly curated and directed vision and is theoretically expected to be of the highest quality, especially in dimensions like Strategic Vision and Integration Depth. A **Multi-Person** proposal reflects a broad consensus, while a **Single-Person** proposal reflects an individual's perspective. Please factor this context into your evaluation.

Analyze the provided proposal text below and evaluate it on the following eight core dimensions, providing a score from 1.0 to 10.0 for each, along with a brief justification.

--- CORE DIMENSIONS ---

1. Novelty (1-10)
Definition: This metric assesses the degree to which the research proposal introduces an original idea that modifies existing paradigms in the field. It evaluates originality (how rare, ingenious, imaginative, or surprising the core insight is) and paradigm relatedness (whether the idea preserves the current paradigm or modifies it in a radical, transformational way). High novelty indicates a proposal that challenges fundamental assumptions or opens new avenues of research, rather than incremental tweaks.
Guiding Question: How original and paradigm-modifying is the core idea? Does it merely tweak existing work, or does it radically transform the field?
1-3: Low Novelty. Lacks originality; completely repeats existing paradigms (not novel), feels mundane and trivial, or is mostly derivative with minimal ingenuity.
4-7: Moderate Novelty. Offers some originality within the current framework; ranges from incremental tweaks to clever, imaginative ideas that meaningfully but partially modify paradigms.
8-10: High Novelty. Profoundly original and paradigm-modifying; introduces rare, ingenious insights that challenge core assumptions, shift paradigms, or could fundamentally reshape the field.

2. Workability (1-10)
Definition: This metric evaluates the feasibility of the proposed research plan, assessing whether it can be easily implemented without violating known constraints (e.g., technical, ethical, or resource limitations). It considers acceptability (social, legal, or political feasibility) and implementability (ease of execution, including awareness of risks and mitigation strategies). High workability indicates a practical, grounded blueprint rather than speculative ideas.
Guiding Question: How feasible and implementable is the plan? Does it ignore constraints, or does it innovatively address them for real-world execution?
1-3: Low Workability. Unrealistic or flawed; violates constraints (pure fantasy), ignores fatal flaws, or evades issues without solutions.
4-7: Moderate Workability. Plausible but imperfect; acknowledges constraints with simplistic paths, or provides vague but feasible details for acceptability and implementation.
8-10: High Workability. Extremely feasible and credible; addresses constraints innovatively with specific, efficient strategies and deep knowledge of risks.

3. Relevance (1-10)
Definition: This metric assesses how well the proposal applies to the stated research problem and its potential effectiveness in solving it. It evaluates applicability (direct fit to the problem) and effectiveness (likelihood of achieving meaningful results or impact). High relevance ensures the proposal addresses a genuine gap in a compelling, targeted manner, forming a cohesive narrative from problem to solution.
Guiding Question: How well does the proposal fit and solve the problem? Is it disconnected, or does it offer transformative impact?
1-3: Low Relevance. Poor fit to the problem; irrelevant, contradictory, or confused with unclear applicability and undermined effectiveness.
4-7: Moderate Relevance. Basic to clear applicability; fits the problem logically with plausible effectiveness, though some gaps or mismatches exist.
8-10: High Relevance. Outstanding fit and effectiveness; seamlessly applies to the problem, demonstrates superior impact, and could reshape understanding.

4. Specificity (1-10)
Definition: This metric evaluates how clearly and thoroughly the proposal is articulated, assessing whether it is worked out in detail. It considers implicational explicitness (clear links between actions and outcomes), completeness (breadth of coverage across who, what, where, when, why, and how), and clarity (grammatical and communicative precision). High specificity distinguishes detailed, rigorous plans from vague or incomplete ones.
Guiding Question: How detailed and clear is the articulation? Is it incoherent, or does it provide a benchmark-level blueprint?
1-3: Low Specificity. Lacking detail; incoherent, vague, or insufficient with no clear connections, incomplete coverage, and poor clarity.
4-7: Moderate Specificity. Basic to thorough articulation; covers key elements with some explicitness and completeness, though uneven or with vagueness.
8-10: High Specificity. Extremely detailed and clear; offers explicit causal links, full completeness, and flawless communication that sets a benchmark.

5. Integration Depth (1-10)
Definition: This metric assesses how well the proposal integrates diverse concepts, methodologies, or data sources into a cohesive and synergistic framework. It evaluates the ability to connect disparate elements, creating a whole that is greater than the sum of its parts. High integration depth indicates a sophisticated, interdisciplinary approach, rather than a siloed or fragmented one.
Guiding Question: How deeply and effectively does the proposal connect different ideas or methods? Is it a collection of separate parts, or a truly integrated system?
1-3: Low. Siloed approach; elements are disconnected or poorly combined.
4-7: Moderate. Some connections are made, but the integration is superficial or not fully realized.
8-10: High. Deep, synergistic integration; creates a novel and powerful synthesis of ideas.

6. Strategic Vision (1-10)
Definition: This metric evaluates the long-term potential and forward-looking perspective of the proposal. It assesses whether the research addresses not just an immediate gap but also anticipates future trends, sets the stage for subsequent work, and has a clear vision for its broader impact on the field or society. High strategic vision indicates a proposal that is not just a single project, but a foundational step in a larger, ambitious research agenda.
Guiding Question: What is the long-term ambition of this proposal? Does it have a clear and compelling vision for the future?
1-3: Low. Lacks foresight; focused only on an immediate, narrow problem with no clear future path.
4-7: Moderate. Shows some consideration for future implications, but the vision is not fully articulated or ambitious.
8-10: High. Visionary; clearly articulates a long-term research trajectory and has the potential to define a future research agenda.

7. Methodological Rigor (1-10)
Definition: This metric assesses the soundness and appropriateness of the proposed research methods. It evaluates the quality of the experimental design, data collection procedures, analytical techniques, and validation strategies. High methodological rigor ensures that the research outcomes will be reliable, valid, and reproducible.
Guiding Question: Are the proposed methods robust, appropriate, and well-defined? Can the results be trusted?
1-3: Low. Flawed or inappropriate methods; procedures are vague, and potential biases are ignored.
4-7: Moderate. Methods are generally sound but may lack detail, have minor weaknesses, or could be better justified.
8-10: High. Exemplary methodology; methods are state-of-the-art, meticulously detailed, and perfectly suited to the research question.

8. Argumentative Cohesion (1-10)
Definition: This metric assesses the logical flow and coherence of the argument presented in the proposal. It evaluates how well different sections connect to form a unified narrative, the consistency of reasoning throughout, and the strength of the logical connections between claims and evidence. High argumentative cohesion indicates a proposal where all parts work together to build a compelling, logically sound case.
Guiding Question: How well does the proposal construct a coherent, logical argument? Are the connections between ideas clear and compelling?
1-3: Low. Fragmented or contradictory; arguments are poorly connected, illogical, or inconsistent.
4-7: Moderate. Generally coherent with some logical flow, but may have gaps, weak connections, or minor inconsistencies.
8-10: High. Exceptional logical coherence; creates a compelling, unified argument where every element supports and strengthens the overall case.

--- OVERALL EVALUATION ---

Overall Quality of Idea (1-10)
Definition: This metric synthesizes all eight dimensions to evaluate the proposal's overall quality and potential impact.
Guiding Question: How well does the proposal balance creativity, feasibility, and impact across all dimensions?

--- OUTPUT FORMAT ---

Your final output MUST be a JSON object with the following exact structure. Do not add any text before or after the JSON object.

{{
  "Novelty": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Workability": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Relevance": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Specificity": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Integration_Depth": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Strategic_Vision": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Methodological_Rigor": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Argumentative_Cohesion": {{
    "score": <float>,
    "justification": "<string>"
  }},
  "Overall_Quality": {{
    "score": <float>
  }},
  "Weaknesses": [
    "<string>",
    "<string>"
  ],
  "Decision": "<string>"
}}
"""

def _get_single_review_json(prompt, model, client, temperature):
    """Helper function to get a single JSON review from the LLM."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        content = response.choices[0].message.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            logging.warning("No JSON object found in the model's response.")
            return None
        return json.loads(match.group(0))
    except Exception as e:
        logging.error(f"Error in _get_single_review_json: {e}")
        return None

def perform_structured_review(paper_txt, model, client, temperature=0.1, num_reviews_ensemble=3, num_reflections=3):


    print(f"--- Starting Ensemble Phase ({num_reviews_ensemble} reviews) ---")
    initial_prompt = f"{BASE_REVIEW_PROMPT}\n---PROPOSAL TEXT TO REVIEW:---\n{paper_txt}"
    
    ensemble_reviews = []

    with ThreadPoolExecutor(max_workers=num_reviews_ensemble) as executor:
        futures = [executor.submit(_get_single_review_json, initial_prompt, model, client, 0.5) for _ in range(num_reviews_ensemble)]
        for future in as_completed(futures):
            review = future.result()
            if review:
                ensemble_reviews.append(review)

    if not ensemble_reviews:
        print("Failed to get any reviews in the ensemble phase.")
        return None

    print(f"--- Ensemble Phase Complete: Got {len(ensemble_reviews)} reviews. ---")


    print("--- Starting Meta-Review Phase ---")
    reviews_text = ""
    for i, r in enumerate(ensemble_reviews):
        reviews_text += f"\n--- Review {i+1} ---\n{json.dumps(r, indent=2)}"

    meta_prompt = META_REVIEW_PROMPT_TEMPLATE.format(
        reviewer_count=len(ensemble_reviews),
        reviews_text=reviews_text
    )
    

    current_review = _get_single_review_json(meta_prompt, model, client, temperature)

    if not current_review:
        print("Meta-review failed. Using the first ensemble review as a fallback.")
        current_review = ensemble_reviews[0]
    
    print("--- Meta-Review Phase Complete ---")


    print(f"--- Starting Reflection Phase ({num_reflections} iterations) ---")
    for i in range(num_reflections):
        print(f"Reflection iteration {i + 1}/{num_reflections}...")
        reflection_prompt = REFLECTION_PROMPT_TEMPLATE.format(
            previous_review_json=json.dumps(current_review, indent=2)
        )
        
        next_review = _get_single_review_json(reflection_prompt, model, client, temperature)

        if not next_review:
            print("Reflection step failed. Continuing with the previous review.")
            break
        

        if next_review.get('Novelty', {}).get('justification') == "I am done":
            print("Reflection converged. Stopping early.")
            break
        
        current_review = next_review

    print("--- Reflection Phase Complete ---")


    final_scores = {}
    score_keys = ["Novelty", "Workability", "Relevance", "Specificity", "Integration_Depth", "Strategic_Vision", "Methodological_Rigor", "Argumentative_Cohesion"]
    for key in score_keys:
        scores = [float(r.get(key, {}).get('score', 0.0)) for r in ensemble_reviews if r.get(key, {}).get('score') is not None]
        final_scores[key] = np.mean(scores) if scores else 0.0


    weights = {
        'Novelty': 1/8, 'Workability': 1/8, 'Relevance': 1/8, 'Specificity': 1/8,
        'Integration_Depth': 1/8, 'Strategic_Vision': 1/8, 'Methodological_Rigor': 1/8, 'Argumentative_Cohesion': 1/8
    }

    overall_score = sum(final_scores[key] * weights[key] for key in score_keys)


    final_review = {
        "Novelty": f"{final_scores['Novelty']:.1f}/10",
        "Workability": f"{final_scores['Workability']:.1f}/10",
        "Relevance": f"{final_scores['Relevance']:.1f}/10",
        "Specificity": f"{final_scores['Specificity']:.1f}/10",
        "Integration_Depth": f"{final_scores['Integration_Depth']:.1f}/10",
        "Strategic_Vision": f"{final_scores['Strategic_Vision']:.1f}/10",
        "Methodological_Rigor": f"{final_scores['Methodological_Rigor']:.1f}/10",
        "Argumentative_Cohesion": f"{final_scores['Argumentative_Cohesion']:.1f}/10",
        "Overall_Quality": f"{overall_score:.1f}/10",
        "Decision": current_review.get('Decision', 'N/A'),
        "Weaknesses": current_review.get('Weaknesses', []) or ['No major weaknesses identified.'],
        "Justifications": {key: current_review.get(key, {}).get('justification', 'N/A') for key in score_keys}
    }
    return final_review


def extract_paper_blocks_from_file(file_content):

    try:
        match = re.search(r'paper_txts\s*=\s*(\[.*?\])', file_content, re.DOTALL)
        if match:
            list_string = match.group(1)
            paper_blocks = literal_eval(list_string)
            if isinstance(paper_blocks, list):
                return paper_blocks
    except (ValueError, SyntaxError) as e:
        logging.error(f"Could not parse Python list from file: {e}")
        print(f"Could not parse Python list from file: {e}")
    
    paper_blocks = re.findall(r"'''(.*?)'''", file_content, re.DOTALL)
    if paper_blocks:
        return paper_blocks

    return [file_content]


def process_file(txt_path, results_dir):

    with open(txt_path, 'r', encoding='utf-8') as f:
        file_content = f.read().strip()
    if not file_content:
        logging.info(f"{txt_path} is empty, skipping.")
        print(f"{txt_path} is empty, skipping.")
        return None
    
    logging.info(f"Processing {txt_path} ...")
    print(f"Processing {txt_path} ...")
    
    paper_blocks = extract_paper_blocks_from_file(file_content)
    
    os.makedirs(results_dir, exist_ok=True)
    base_name = os.path.basename(txt_path).replace('.txt', '')
    
    all_reviews = []

    if not paper_blocks:
        logging.warning(f"No processable content found in {txt_path}. Skipping.")
        print(f"No processable content found in {txt_path}. Skipping.")
        return None

    for idx, paper_txt in enumerate(paper_blocks, 1):
        paper_txt = paper_txt.strip()
        if not paper_txt:
            continue
        
        logging.info(f"Processing entry {idx} in {txt_path} ...")
        print(f"Processing entry {idx} in {txt_path} ...")
        
        review = perform_structured_review(
            paper_txt,
            model,
            client,
            temperature=0.1,
            num_reviews_ensemble=3, # 3次独立评审
            num_reflections=3      # 3轮自我反思
        )

        if review is None:
            continue

        logging.info(f"####review for entry {idx} in {txt_path}: {review}")
        print(f"####review for entry {idx} in {txt_path}", review)
        
        json_path = os.path.join(results_dir, f'{base_name}_entry{idx}_review.json')
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(review, jf, indent=4, ensure_ascii=False)
        logging.info(f"Saved full review to {json_path}")
        
        summary_lines = [
            f"--- Review for {base_name}_entry{idx} ---",
            f"Overall Quality: {review['Overall_Quality']}",
            f"Novelty: {review['Novelty']}",
            f"Workability: {review['Workability']}",
            f"Relevance: {review['Relevance']}",
            f"Specificity: {review['Specificity']}",
            f"Integration Depth: {review['Integration_Depth']}",
            f"Strategic Vision: {review['Strategic_Vision']}",
            f"Methodological Rigor: {review['Methodological_Rigor']}",
            f"Argumentative Cohesion: {review['Argumentative_Cohesion']}",
            f"Decision: {review['Decision']}",
            f"Weaknesses: {', '.join(review['Weaknesses'])}"
        ]
        summary_text = '\n'.join(summary_lines)
        print(summary_text)
        
        summary_path = os.path.join(results_dir, f'{base_name}_entry{idx}_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as sf:
            sf.write(summary_text)
        logging.info(f"Saved summary to {summary_path}")
        
        all_reviews.append(review)
    
    return all_reviews

def process_examples_directory(examples_dir):
    if not os.path.exists(examples_dir):
        print(f"Directory {examples_dir} does not exist. Creating it...")
        os.makedirs(examples_dir)
        print(f"Created directory: {examples_dir}. Please add your .txt files there.")
        return

    results_dir = examples_dir.replace('examples_', 'results_')
    
    txt_files = [os.path.join(examples_dir, f) for f in os.listdir(examples_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"No .txt files found in the '{examples_dir}' directory.")
        return
    
    print(f"Processing directory: {examples_dir} -> {results_dir}")
    print(f"Found {len(txt_files)} .txt files to process")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_file, txt_path, results_dir): txt_path for txt_path in txt_files}
        for future in as_completed(futures):
            txt_path = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing {txt_path}: {e}")
                print(f"Error processing {txt_path}: {e}")

if __name__ == '__main__':
    for examples_dir in EXAMPLES_DIRS:
        print(f"\n{'='*60}")
        print(f"Processing examples directory: {examples_dir}")
        print(f"{'='*60}")
        process_examples_directory(examples_dir)
    
    print(f"\n{'='*60}")
    print("All directories processed!")
    print(f"{'='*60}")
