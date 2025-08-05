import os
import numpy as np
import json
from pypdf import PdfReader
import pymupdf
import pymupdf4llm
from ai_scientist.llm import (
    get_response_from_llm,
    get_batch_responses_from_llm,
    extract_json_between_markers,
)

reviewer_system_prompt_base = (
    "You are an AI researcher who is reviewing a research proposal after author discussion."
    "Be critical and cautious in your decision. Focus on evaluating the proposal's argumentative cohesion, intellectual depth, execution credibility, and scientific rigor."
)

reviewer_system_prompt_neg = (
    reviewer_system_prompt_base
    + "If a proposal is weak or you are unsure, give it low scores and reject it."
)
reviewer_system_prompt_pos = (
    reviewer_system_prompt_base
    + "If a proposal is strong or you are unsure, give it high scores and accept it."
)

template_instructions = """
Respond in the following format:

THOUGHT:
<THOUGHT>

REVIEW JSON:
```json
<JSON>
```

In <THOUGHT>, first briefly discuss your intuitions and reasoning for the evaluation.
Detail your high-level arguments, necessary choices and desired outcomes of the review.
Do not make generic comments here, but be specific to your current proposal.
Treat this as the note-taking phase of your review.

In <JSON>, provide the review in JSON format with the following fields in the order:
- "Summary": A summary of the proposal content and its contributions.
- "Strengths": A list of strengths of the proposal.
- "Weaknesses": A list of weaknesses of the proposal.
- "Argumentative_Cohesion": A rating from 1 to 10 evaluating the logical integrity and persuasiveness of the narrative thread.
- "Intellectual_Depth": A rating from 1 to 10 evaluating the significance and originality of the core insight.
- "Execution_Credibility": A rating from 1 to 10 evaluating the feasibility and groundedness of the proposed execution plan.
- "Scientific_Rigor": A rating from 1 to 10 evaluating the objectivity and integrity of the validation plan.
- "Overall_Quality": A rating from 1 to 10 evaluating the overall quality and potential impact of the research idea.
- "Questions": A set of clarifying questions to be answered by the proposal authors.
- "Limitations": A set of limitations and potential risks of the proposed work.
- "Ethical_Concerns": A boolean value indicating whether there are ethical concerns.
- "Confidence": A rating from 1 to 5 (low, medium, high, very high, absolute).
- "Decision": A decision that has to be one of the following: Accept, Reject.

For the "Decision" field, don't use Weak Accept, Borderline Accept, Borderline Reject, or Strong Reject. Instead, only use Accept or Reject.
This JSON will be automatically parsed, so ensure the format is precise.
"""

proposal_evaluation_form = (
    """
## Research Proposal Evaluation Form
Below is a description of the evaluation criteria for research proposals and guidelines on what to consider when assessing each dimension.

**Research Proposal Format:**
The proposal should typically include:
- Title
- Problem Statement
- Motivation & Hypothesis
- Proposed Method
- Step-by-Step Experiment Plan

**Four Holistic Evaluation Metrics:**

**1. Novelty (1-10)**
Definition: This metric assesses the degree to which the research proposal introduces an original idea that modifies existing paradigms in the field. It evaluates originality (how rare, ingenious, imaginative, or surprising the core insight is) and paradigm relatedness (whether the idea preserves the current paradigm or modifies it in a radical, transformational way). High novelty indicates a proposal that challenges fundamental assumptions or opens new avenues of research, rather than incremental tweaks.

Scoring Rubric:
- 10: Field-Defining: Proposes a highly original and paradigm-modifying idea that could fundamentally reshape the field or create a new subfield.
- 9: Paradigm-Shifting: The idea is extremely rare and imaginative, challenging core paradigms with transformative potential.
- 8: Highly Original: The core insight is profoundly novel and paradigm-modifying, offering a surprising new perspective on a key problem.
- 7: Significant Novelty: Introduces a rare and ingenious approach that meaningfully modifies existing paradigms.
- 6: Clever: Presents a non-obvious, imaginative idea that partially modifies paradigms within the current framework.
- 5: Solid Originality: Offers meaningful novelty but leans more toward paradigm-preserving improvements.
- 4: Incremental: The idea is somewhat rare but lacks strong imaginative or paradigm-modifying elements.
- 3: Derivative: Mostly paradigm-preserving with minimal originality, resembling common approaches.
- 2: Trivial: Lacks rarity and ingenuity, feeling mundane and non-transformational.
- 1: Not Novel: Completely repeats existing paradigms without any original or modifying elements.

**2. Workability (1-10)**
Definition: This metric evaluates the feasibility of the proposed research plan, assessing whether it can be easily implemented without violating known constraints (e.g., technical, ethical, or resource limitations). It considers acceptability (social, legal, or political feasibility) and implementability (ease of execution, including awareness of risks and mitigation strategies). High workability indicates a practical, grounded blueprint rather than speculative ideas.

Scoring Rubric:
- 10: Bulletproof: Extremely feasible, with all constraints addressed innovatively; acceptability and implementability are exemplary.
- 9: Expert-Level: Highly workable, identifying and resolving constraints with clever, efficient strategies showing deep knowledge.
- 8: Highly Credible: Key constraints are addressed with specific, acceptable, and implementable solutions.
- 7: Credible: Major feasibility issues are identified, with plausible paths to acceptability and implementation.
- 6: Plausible: Overall workable, but some constraints or implementation details are not fully explored.
- 5: Feasible but Vague: Macro-level feasibility is present, but acceptability or implementability lacks detail.
- 4: Overly Optimistic: Acknowledges constraints but proposes simplistic or unproven paths to implementation.
- 3: Evasive: Recognizes workability issues but offers no concrete acceptable or implementable solutions.
- 2: Ignores Fatal Flaws: Obvious constraints are overlooked, making acceptability or implementability doubtful.
- 1: Pure Fantasy: Violates known constraints entirely, with no feasible path to implementation.

**3. Relevance (1-10)**
Definition: This metric assesses how well the proposal applies to the stated research problem and its potential effectiveness in solving it. It evaluates applicability (direct fit to the problem) and effectiveness (likelihood of achieving meaningful results or impact). High relevance ensures the proposal addresses a genuine gap in a compelling, targeted manner, forming a cohesive narrative from problem to solution.

Scoring Rubric:
- 10: Exemplary: Perfectly applicable and highly effective, reshaping understanding of the problem with inevitable impact.
- 9: Outstanding: Seamlessly applicable to the problem, with strong evidence of effectiveness in solving it.
- 8: Highly Relevant: Tightly fits the problem and demonstrates clear, superior effectiveness.
- 7: Relevant: Clearly applies to the problem with logical expectation of effectiveness.
- 6: Applicable: Fits the problem basically, with plausible but not deeply convincing effectiveness.
- 5: Understandable: Core relevance is graspable, but applicability or effectiveness has gaps.
- 4: Disconnected: Feels loosely applicable, with questionable effectiveness in addressing the problem.
- 3: Confused: Applicability is unclear, and effectiveness is undermined by mismatches.
- 2: Contradictory: Internal inconsistencies reduce applicability and effectiveness.
- 1: Irrelevant: Does not apply to the stated problem or offer any effective solution.

**4. Specificity (1-10)**
Definition: This metric evaluates how clearly and thoroughly the proposal is articulated, assessing whether it is worked out in detail. It considers implicational explicitness (clear links between actions and outcomes), completeness (breadth of coverage across who, what, where, when, why, and how), and clarity (grammatical and communicative precision). High specificity distinguishes detailed, rigorous plans from vague or incomplete ones.

Scoring Rubric:
- 10: Gold Standard: Extremely specific, with explicit implications, full completeness, and flawless clarity; sets a benchmark.
- 9: Insightful: Highly detailed, with explicit causal links, comprehensive coverage, and clear communication.
- 8: Critical: Strong specificity, including detailed breakdowns and clear, complete articulation.
- 7: Rigorous: Thoroughly specified, with good explicitness, completeness, and clarity.
- 6: Sufficient: Basically specific, covering key details but with some vagueness in implications or completeness.
- 5: Basic: Core elements are specified, but lacks depth in explicitness, completeness, or clarity.
- 4: Biased or Incomplete: Specificity is uneven, with incomplete coverage or unclear implications.
- 3: Insufficient: Fails to detail key aspects, reducing explicitness and completeness.
- 2: Vague: Relies on ambiguous descriptions, lacking clarity and thoroughness.
- 1: Incoherent: Completely lacks specificity, with no clear details or explicit connections.

**Overall Quality of Idea (1-10)**
Definition: This metric synthesizes the four dimensions (novelty, workability, relevance, and specificity) to evaluate the proposal's overall quality and potential impact. It assesses whether the idea is creative (high novelty), of high quality (strong workability, relevance, and specificity), and capable of making a significant, lasting contribution.

Scoring Rubric:
- 10: Landmark Potential: Exceptional across all dimensions, with visionary novelty, feasible execution, perfect relevance, and detailed specificity.
- 9: Clear Breakthrough: Outstanding synthesis of high novelty, workability, relevance, and specificity for broad impact.
- 8: Strong Contender: Well-balanced with significant strengths in novelty, feasibility, relevance, and detail.
- 7: Solid Contribution: Good overall, representing a meaningful advance via balanced dimensions.
- 6: Competent but Lacks Spark: Sound but may underperform in novelty or specificity.
- 5: Has Potential but Flawed: Core promise exists, but weaknesses in workability or relevance hinder it.
- 4: Weak and Unconvincing: Lacks in multiple dimensions, such as low novelty or poor specificity.
- 3: Fatally Flawed: Critical issues in feasibility or relevance undermine the whole.
- 2: Vague and Insubstantial: Insufficient specificity or relevance makes it hard to evaluate.
- 1: No Merit: Fails across dimensions, showing little novelty, workability, or clarity.

**Confidence Score (1-5):**
- 5: Absolutely certain about your assessment. Very familiar with the related work and checked details carefully.
- 4: Confident in your assessment, but not absolutely certain.
- 3: Fairly confident in your assessment. Possible unfamiliarity with some pieces of related work.
- 2: Willing to defend your assessment, but quite likely unfamiliar with central parts of the submission.
- 1: Assessment is an educated guess. The submission is not in your area or was difficult to understand.
"""
    + template_instructions
)


def perform_review(
    text,
    model,
    client,
    num_reflections=5,
    num_fs_examples=1,
    num_reviews_ensemble=5,
    temperature=0.75,
    msg_history=None,
    return_msg_history=False,
    reviewer_system_prompt=reviewer_system_prompt_neg,
    review_instruction_form=proposal_evaluation_form,
):
    if num_fs_examples > 0:
        print("num_fs_examples",num_fs_examples)
        fs_prompt = get_review_fewshot_examples(num_fs_examples)
        base_prompt = review_instruction_form + fs_prompt
    else:
        base_prompt = review_instruction_form

    base_prompt += f"""
Here is the research proposal you are asked to review:
```
{text}
```"""

    if num_reviews_ensemble > 1:
        llm_review, msg_histories = get_batch_responses_from_llm(
            base_prompt,
            model=model,
            client=client,
            system_message=reviewer_system_prompt,
            print_debug=False,
            msg_history=msg_history,
            # Higher temperature to encourage diversity.
            temperature=0.75,
            n_responses=num_reviews_ensemble,
        )
        parsed_reviews = []
        for idx, rev in enumerate(llm_review):
            try:
                parsed_reviews.append(extract_json_between_markers(rev))
            except Exception as e:
                print(f"Ensemble review {idx} failed: {e}")
        parsed_reviews = [r for r in parsed_reviews if r is not None]
        review = get_meta_review(model, client, temperature, parsed_reviews)

        # take first valid in case meta-reviewer fails
        if review is None:
            review = parsed_reviews[0]
        try:
            # Replace numerical scores with the average of the ensemble.
            for score, limits in [
                ("Novelty", (1, 10)),
                ("Workability", (1, 10)),
                ("Relevance", (1, 10)),
                ("Specificity", (1, 10)),
                ("Overall_Quality", (1, 10)),
                ("Confidence", (1, 5)),
            ]:
                scores = []
                for r in parsed_reviews:
                    if score in r and limits[1] >= r[score] >= limits[0]:
                        scores.append(r[score])
                try:
                    review[score] = int(round(np.mean(scores)))
                except Exception as e:
                    review[score] = 6

            
            # print("", type(msg_histories[0]))
            # print("", msg_histories[0].keys())
            
            msg_history = msg_histories[0][:-1]
            msg_history += [
                {
                    "role": "assistant",
                    "content": f"""
    THOUGHT:
    I will start by aggregating the opinions of {num_reviews_ensemble} reviewers that I previously obtained.

    REVIEW JSON:
    ```json
    {json.dumps(review)}
    ```
    """,
                }
            ]
        except Exception as e:
            # Replace numerical scores with the average of the ensemble.
            for score, limits in [
                ("Novelty", (1, 10)),
                ("Workability", (1, 10)),
                ("Relevance", (1, 10)),
                ("Specificity", (1, 10)),
                ("Overall_Quality", (1, 10)),
                ("Confidence", (1, 5)),
            ]:
                scores = []
                for r in parsed_reviews:
                    if score in r and limits[1] >= r[score] >= limits[0]:
                        scores.append(r[score])
                try:
                    review[score] = int(round(np.mean(scores)))
                except Exception as e:
                    review[score] = 6

                
                msg_history_dict = msg_histories[0]

                
                msg_history_items = list(msg_history_dict.items())[:-1]

                
                msg_history = dict(msg_history_items)

                
                msg_history.update({
                    "role": "assistant",
                    "content": f"""
                THOUGHT:
                I will start by aggregating the opinions of {num_reviews_ensemble} reviewers that I previously obtained.

                REVIEW JSON:
                ```json
                {json.dumps(review)}
                ```
                """,
                })
    else:
        llm_review, msg_history = get_response_from_llm(
            base_prompt,
            model=model,
            client=client,
            system_message=reviewer_system_prompt,
            print_debug=False,
            msg_history=msg_history,
            temperature=temperature,
        )
        review = extract_json_between_markers(llm_review)

    if num_reflections > 1:
        for j in range(num_reflections - 1):
            # print(f"Relection: {j + 2}/{num_reflections}")
            text, msg_history = get_response_from_llm(
                reviewer_reflection_prompt,
                client=client,
                model=model,
                system_message=reviewer_system_prompt,
                msg_history=msg_history,
                temperature=temperature,
            )
            print("####text",text)
            review = extract_json_between_markers(text)
            print("####review",review)
            assert review is not None, "Failed to extract JSON from LLM output"

            if "I am done" in text:
                # print(f"Review generation converged after {j + 2} iterations.")
                break

    if return_msg_history:
        return review, msg_history
    else:
        return review


reviewer_reflection_prompt = """Round {current_round}/{num_reflections}.
In your thoughts, first carefully consider the accuracy and soundness of the review you just created.
Include any other factors that you think are important in evaluating the proposal.
Ensure the review is clear and concise, and the JSON is in the correct format.
Do not make things overly complicated.
In the next attempt, try and refine and improve your review.
Stick to the spirit of the original review unless there are glaring issues.

Respond in the same format as before:
THOUGHT:
<THOUGHT>

REVIEW JSON:
```json
<JSON>
```

If there is nothing to improve, simply repeat the previous JSON EXACTLY after the thought and include "I am done" at the end of the thoughts but before the JSON.
ONLY INCLUDE "I am done" IF YOU ARE MAKING NO MORE CHANGES."""


def load_paper(pdf_path, num_pages=None, min_size=100):
    try:
        if num_pages is None:
            text = pymupdf4llm.to_markdown(pdf_path)
        else:
            reader = PdfReader(pdf_path)
            min_pages = min(len(reader.pages), num_pages)
            text = pymupdf4llm.to_markdown(pdf_path, pages=list(range(min_pages)))
        if len(text) < min_size:
            raise Exception("Text too short")
    except Exception as e:
        print(f"Error with pymupdf4llm, falling back to pymupdf: {e}")
        try:
            doc = pymupdf.open(pdf_path)  # open a document
            if num_pages:
                doc = doc[:num_pages]
            text = ""
            for page in doc:  # iterate the document pages
                text = text + page.get_text()  # get plain text encoded as UTF-8
            if len(text) < min_size:
                raise Exception("Text too short")
        except Exception as e:
            print(f"Error with pymupdf, falling back to pypdf: {e}")
            reader = PdfReader(pdf_path)
            if num_pages is None:
                text = "".join(page.extract_text() for page in reader.pages)
            else:
                text = "".join(page.extract_text() for page in reader.pages[:num_pages])
            if len(text) < min_size:
                raise Exception("Text too short")

    return text


def load_review(path):
    with open(path, "r") as json_file:
        loaded = json.load(json_file)
    return loaded["review"]


# get directory of this file
dir_path = os.path.dirname(os.path.realpath(__file__))

# fewshot_papers = [
#     os.path.join(dir_path, "fewshot_examples/132_automated_relational.pdf"),
#     os.path.join(dir_path, "fewshot_examples/attention.pdf"),
#     os.path.join(dir_path, "fewshot_examples/2_carpe_diem.pdf"),
# ]

# fewshot_reviews = [
#     os.path.join(dir_path, "fewshot_examples/132_automated_relational.json"),
#     os.path.join(dir_path, "fewshot_examples/attention.json"),
#     os.path.join(dir_path, "fewshot_examples/2_carpe_diem.json"),
# ]
fewshot_papers = [
    os.path.join(dir_path, "fewshot_examples/mamba.pdf"),
]

fewshot_reviews = [
    os.path.join(dir_path, "fewshot_examples/mamba.json"),
]

def get_review_fewshot_examples(num_fs_examples=1):
    fewshot_prompt = """
Below are some sample reviews of research proposals, copied from previous machine learning conferences.
Note that while each review is formatted differently according to each reviewer's style, the reviews are well-structured and therefore easy to navigate.
"""
    for paper, review in zip(
        fewshot_papers[:num_fs_examples], fewshot_reviews[:num_fs_examples]
    ):
        txt_path = paper.replace(".pdf", ".txt")
        if os.path.exists(txt_path):
            with open(txt_path, "r") as f:
                paper_text = f.read()
        else:
            paper_text = load_paper(paper)
        review_text = load_review(review)
        fewshot_prompt += f"""
Proposal:

```
{paper_text}
```

Review:

```
{review_text}
```
"""

    return fewshot_prompt


meta_reviewer_system_prompt = """You are an expert in AI domain.
You are in charge of meta-reviewing a research proposal that was reviewed by {reviewer_count} reviewers.
Your job is to aggregate the reviews into a single meta-review in the same format.
Be critical and cautious in your decision, find consensus, and respect the opinion of all the reviewers."""


def get_meta_review(model, client, temperature, reviews):
    # Write a meta-review from a set of individual reviews
    review_text = ""
    for i, r in enumerate(reviews):
        review_text += f"""
Review {i + 1}/{len(reviews)}:
```
{json.dumps(r)}
```
"""
    base_prompt = proposal_evaluation_form + review_text

    llm_review, msg_history = get_response_from_llm(
        base_prompt,
        model=model,
        client=client,
        system_message=meta_reviewer_system_prompt.format(reviewer_count=len(reviews)),
        print_debug=False,
        msg_history=None,
        temperature=temperature,
    )
    meta_review = extract_json_between_markers(llm_review)
    return meta_review


def perform_improvement(review, coder):
    improvement_prompt = '''The following review has been created for your research proposal:
"""
{review}
"""

Improve the text using the review.'''.format(
        review=json.dumps(review)
    )
    coder_out = coder.run(improvement_prompt)
