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

**1. Argumentative Cohesion & Persuasiveness (1-10)**
Definition: This metric assesses the seamlessness and logical integrity of the narrative thread connecting the problem statement, core hypothesis, proposed method, and validation plan. It evaluates whether the proposal tells a single, self-consistent, and compelling story that makes the proposed solution feel like a natural and necessary consequence of the initial problem analysis.

Scoring Rubric:
- 10: Exemplary: The argument is as precise as a scalpel, and the narrative is very inspiring. It not only convinces the reader, but also reshapes their cognitive framework of the problem.
- 9: Outstanding: The entire argument is seamless and persuasive, making people feel that this solution is the "inevitable choice" to solve this problem.
- 8: Persuasive: The logical chain is tight and the narrative is smooth, which can actively lead readers to believe the rationality and superiority of its method.
- 7: Cohesive: The path from the problem to the solution is clear and logical, and the connection between each part is natural.
- 6: Clear: The main argument is clear and the reader can understand its basic logic, but the connections between the parts may be a little abrupt.
- 5: Understandable: The core idea of the argument can be understood, but there are obvious logical jumps, and the reader needs to fill in the gaps.
- 4: Disconnected: The problem, method, experiment, etc. feel like they are pieced together independently, lacking a unified narrative thread.
- 3: Confused: There are multiple interfering or contradictory threads in the argument, and the core claims are unclear.
- 2: Contradictory: There are obvious internal contradictions between different parts of the proposal.
- 1: Incoherent: The logic is completely missing and it is impossible to form an understandable argument.

**2. Intellectual Depth & Ambition (1-10)**
Definition: This metric evaluates the significance and originality of the core insight behind the proposal. It assesses whether the work challenges a fundamental assumption, proposes a new paradigm, or offers a solution with the potential for broad impact, as opposed to making a purely incremental or predictable improvement.

Scoring Rubric:
- 10: Field-Defining: Proposes an idea that may open up a new research field or fundamentally change an existing field.
- 9: Paradigm-Shifting: Challenges the core assumptions in the field and proposes a framework that has the potential to become a new mainstream paradigm.
- 8: Highly Original: The core insight is profound and novel, providing a new perspective for solving a recognized problem.
- 7: Significant Novelty: Proposes a completely new method or an important, non-trivial mechanism that significantly outperforms existing technologies.
- 6: Clever: Proposes a clever, non-obvious improvement or combination within the existing framework, which works well.
- 5: Solid Contribution: Makes meaningful, non-trivial improvements to existing methods, which is a solid step in this research direction.
- 4: Incremental: A predictable, logical next step, but lacking in exciting newness.
- 3: Derivative: Mostly a simple combination or minor tweak of existing work, lacking in independent intellectual contribution.
- 2: Trivial: The proposed improvements are very minor and have little practical impact or academic value.
- 1: Not Novel: Completely repeats or imitates existing work.

**3. Credibility & Groundedness of Execution (1-10)**
Definition: This metric assesses the feasibility and practicality of the proposed plan. It evaluates the authors' awareness of potential technical challenges and risks, and the concreteness and credibility of the strategies proposed to overcome them, distinguishing a well-thought-out blueprint from mere wishful thinking.

Scoring Rubric:
- 10: Bulletproof: The plan is extremely detailed, anticipating and solving all major, minor and even potential obstacles, and its execution strategy itself is very inspiring.
- 9: Expert-Level: Not only has the core technical barriers been identified, but also very clever or efficient solutions have been proposed, showing deep domain knowledge.
- 8: Highly Credible: The key challenges are clearly identified and solutions are presented that are specific, detailed, and convincing.
- 7: Credible: The major technical challenges are identified and plausible solutions are proposed.
- 6: Plausible: The overall plan seems feasible, but some technical details or risks are not discussed in depth.
- 5: Feasible but Vague: The plan is feasible at a macro level, but the description of how to solve key technical problems is vague.
- 4: Overly Optimistic: The challenges are acknowledged, but the proposed solutions are overly simple or rely on unproven assumptions.
- 3: Evasive: The difficulties are recognized, but no specific solutions are provided, only that they "will be solved".
- 2: Ignores Fatal Flaws: There are obvious, fatal flaws in the plan, but the author seems unaware of them or deliberately ignores them.
- 1: Pure Fantasy: The proposed method is not physically or computationally feasible and is completely out of touch with reality.

**4. Scientific Rigor & Critical Thinking (1-10)**
Definition: This metric evaluates the objectivity and integrity of the proposed validation plan. It assesses whether the experiments are designed to rigorously test the core hypotheses, employ fair and strong baselines, include critical analyses like ablation studies, and are aimed at discovering the truth rather than merely confirming the proposal's claims.

Scoring Rubric:
- 10: Gold Standard: The experimental design is extremely sophisticated, not only can it perfectly verify the hypothesis, but its methods and depth can even set a new evaluation benchmark for the field.
- 9: Insightful: The verification plan is very comprehensive, including in-depth analysis and stress tests aimed at exploring boundaries and failure modes.
- 8: Critical: In addition to standard performance comparisons, detailed ablation experiments and analysis are designed to explore "why" it works, reflecting strong critical thinking.
- 7: Rigorous: The experimental plan is thorough, including comparisons with strong and fair baselines, and the evaluation indicators are comprehensive.
- 6: Sufficient: The experimental plan is sufficient to verify its main arguments, and the baseline and indicator selection are reasonable.
- 5: Basic: Basic validation schemes are proposed, but lack depth, e.g. no ablation studies or deeper analysis.
- 4: Biased: The experimental setup (e.g. baseline selection, dataset) is biased in favor of one's own method and is not fair.
- 3: Insufficient: The experimental plan fails to fully validate its core claims.
- 2: Cherry-Picking: The evaluation plan relies on carefully selected examples or metrics, which is misleading.
- 1: Invalid: The experimental plan is completely invalid or missing, or is based only on anecdotal evidence.

**Overall Quality of Idea (1-10)**
Definition: This metric evaluates the overall quality and potential impact of a research idea as presented in a proposal. It synthesizes the four key dimensions above and assesses the proposal's potential to make a significant and lasting contribution to the field.

Scoring Rubric:
- 10: Landmark Potential: A truly exceptional idea that is visionary, fundamentally sound, and meticulously planned. Clear potential to define a new research paradigm.
- 9: Clear Breakthrough: An outstanding idea that is highly ambitious, deeply insightful, and backed by a highly credible and rigorous plan.
- 8: Strong Contender: A very strong and well-crafted idea with significant novelty, persuasive narrative, credible execution plan, and rigorous validation strategy.
- 7: Solid Contribution: A solid, well-rounded research proposal that represents a clear contribution to the field.
- 6: Competent but Lacks Spark: A competent proposal that is technically sound but may lack significant ambition or novelty.
- 5: Has Potential but Flawed: Contains a kernel of a good idea but is undermined by significant flaws in key areas.
- 4: Weak and Unconvincing: The idea is either unoriginal, poorly motivated, or its proposed execution is not credible.
- 3: Fatally Flawed: The proposal suffers from critical flaws such as naive problem understanding or technically infeasible plans.
- 2: Vague and Insubstantial: Too vague to be properly evaluated, lacks clear research question or concrete method.
- 1: No Merit: Incoherent, unoriginal, and demonstrates complete lack of understanding of the research process.

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
                ("Argumentative_Cohesion", (1, 10)),
                ("Intellectual_Depth", (1, 10)),
                ("Execution_Credibility", (1, 10)),
                ("Scientific_Rigor", (1, 10)),
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
                ("Argumentative_Cohesion", (1, 10)),
                ("Intellectual_Depth", (1, 10)),
                ("Execution_Credibility", (1, 10)),
                ("Scientific_Rigor", (1, 10)),
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
