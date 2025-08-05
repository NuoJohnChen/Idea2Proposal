from openai import OpenAI
from ai_scientist.perform_review import load_paper, perform_review

# client = OpenAI(base_url="",
#                 api_key="")


# client = OpenAI(base_url="",
#                 api_key="")

#chatfire
client = OpenAI(base_url="",
                api_key="")
# client = OpenAI(base_url="",
#                 api_key="")

 

model = "deepseek-v3"#"deepseek-chat-64k"#"deepseek-chat-64k"#"deepseek-v3-128k"#"deepseek-chat-64k"#"deepseek-chat"#"deepseek-v3"


# import openai 
# https://api.deepseek.com/v1
# sk-1be4ed2a3d2d4d128c3bc1f43cfe7007
# deepseek-chat
# client = openai.OpenAI(api_key="")
# client = OpenAI(base_url="https://api.deepseek.com/v1",
#                 api_key="")


# model = "gpt-4-1106-preview"
# model = "deepseek-chat:function"
# model = "deepseek-chat"
# model="deepseek-reasoner"

# model = "gpt-4o-2024-08-06"

# Load paper from PDF file (raw text)
# paper_txt = load_paper("")
# paper_txt = load_paper("/AI-Scientist/iclr10101010.pdf")
# paper_txt = load_paper("/AI-Scientist/iclr11133.pdf")
# paper_txt = load_paper("/AI-Scientist/reviewiclr2025workshop/105_Chain_of_Thought_Reasoning.pdf")
# paper_txt = load_paper("/AI-Scientist/reviewiclr2025workshop/155_Training_Large_Language_Mo.pdf")
# paper_txt = load_paper("/AI-Scientist/reviewiclr2025workshop/177_Strategic_LLM_Decoding_thr.pdf")
# paper_txt = load_paper("/AI-Scientist/reviewiclr2025workshop/Freshbench (5).pdf")
# paper_txt = load_paper("/AI-Scientist/mpaw_workshop.pdf")
paper_txt='''
### **Research Proposal: Exploring Selective State Spaces for Efficient Sequence Modeling**

**1. Working Title:**
Mamba: Linear-Time Sequence Modeling with Selective State Spaces

**2. Problem Statement & Motivation:**
The field of sequence modeling is dominated by the Transformer architecture, but its core attention mechanism scales quadratically with sequence length. This computational bottleneck makes it fundamentally impractical for the ever-growing need to process very long sequences in domains like high-resolution audio, genomics, and long-form text.

While more efficient, sub-quadratic architectures (e.g., linear attention, previous state space models) exist, they have consistently failed to match the performance of Transformers on complex, information-dense tasks like language modeling. This suggests a critical trade-off currently exists: we can have either high performance (Transformers) or computational efficiency (prior SSMs), but not both.

**3. Central Hypothesis:**
Our central hypothesis is that the performance gap of existing efficient models stems from their inability to perform **content-based reasoning**. Models like the S4 are linear and time-invariant (LTI), meaning their dynamics are fixed and do not adapt based on the input sequence. Transformers, in contrast, excel because attention is inherently dynamic and content-aware—it can *selectively* choose what information to focus on at each step.

**Our core idea is to bridge this gap by introducing a selection mechanism into a state space model.** We hypothesize that by making an SSM's state transitions **input-dependent**, we can empower it with the selective capabilities of attention while retaining the linear-time scaling and recurrent structure of an SSM.

**4. Proposed Technical Investigation:**

Our research will proceed along three main technical thrusts:

1.  **Developing a Selective State Space (S6) Model:**
    *   **Objective:** Modify the standard SSM formulation to make it input-dependent.
    *   **Plan:** We will start by making the core SSM parameters (`Δ`, `B`, `C`) functions of the input token `x_t`. The key parameter to investigate is `Δ`, the discretization timestep, as we believe controlling it will allow the model to learn to selectively propagate or ignore information. For example, a large `Δ` would reset the state and forget past information, while a small `Δ` would focus finely on the recent context. This creates a time-varying system that can, in theory, mimic content-based selection.

2.  **Addressing the Computational Challenge:**
    *   **Objective:** An input-dependent SSM breaks the time-invariance that allows for fast convolutional parallelization. A naive recurrent implementation would be too slow for training on modern hardware. We must design a new, efficient algorithm for this dynamic model.
    *   **Plan:** We will investigate a hardware-aware parallel scan algorithm. The core strategy is to avoid the massive I/O bottleneck of materializing the full state for every sequence element. We plan to leverage GPU kernel fusion to perform the recurrent state updates and multiplications within fast on-chip SRAM, only writing the final output back to the much slower HBM. This is a significant engineering challenge, but it is critical for making the model trainable at scale.

3.  **Designing a Minimalist Architecture:**
    *   **Objective:** Integrate our new "S6" layer into a simple, effective, and scalable neural network architecture.
    *   **Plan:** Instead of inserting our S6 layer into a Transformer block, we will explore a more radical simplification. We will design a "Mamba" block that combines the S6 layer with a gating mechanism and MLP-like expansion into a single, unified unit. We hypothesize that a simple stack of these homogeneous blocks can form a powerful architecture that dispenses with attention and separate FFN layers entirely.

**5. Experimental Plan & Validation Strategy:**

We will structure our experiments to progressively validate our hypotheses.

1.  **Phase 1: Proof-of-Concept on Synthetic Tasks.**
    *   **Question:** Can our selective SSM even perform basic content-based reasoning?
    *   **Experiments:** We'll test the S6 model on tasks known to be impossible for LTI models, such as the Selective Copying and Induction Heads tasks.
    *   **Success Metric:** The model should not only solve these tasks but also show evidence of generalizing to sequence lengths far beyond what it was trained on. This would be the first strong signal that our selection mechanism works as intended.

2.  **Phase 2: Viability on a Core Benchmark (Language Modeling).**
    *   **Question:** Is this architecture competitive with Transformers in a real-world, high-performance domain?
    *   **Experiments:** We will train models of various sizes (from 125M to ~3B parameters) on The Pile dataset. We will rigorously chart their perplexity scaling curves against well-optimized Transformer baselines (like Transformer++).
    *   **Success Metric:** Achieving perplexity scores that are on par with, or better than, Transformer baselines of a similar parameter count. This would establish the architecture as a serious contender.

3.  **Phase 3: Stress-Testing Long-Context Capabilities.**
    *   **Question:** Does the linear-time scaling of our model translate into practical advantages on ultra-long sequences?
    *   **Experiments:** We will apply the model to genomics (modeling the human genome) and audio (raw waveform modeling), pushing context lengths towards one million tokens.
    *   **Success Metric:** Demonstrating continued performance improvement as context length increases, a regime where Transformers are computationally infeasible. We will also need to empirically verify that our custom kernel provides a significant speedup in these settings.

4.  **Phase 4: Ablation and Analysis.**
    *   **Question:** What parts of our design are most critical to its success?
    *   **Experiments:** We will systematically ablate the selection mechanism (e.g., making only `Δ` selective vs. `B` and `C`), analyze the hardware performance of our parallel scan, and compare our unified Mamba block against more traditional hybrid architectures.
    *   **Success Metric:** A clear understanding of the key contributors to performance, which will guide future work and confirm our initial hypotheses about the importance of input-dependent dynamics.
'''

# print(paper_txt[:2000])
print(len(paper_txt))
# paper_txt = load_paper("/AI-Scientist/iclr11133.pdf")


# with open("", "r") as f:
#     paper_txt = f.read()

# Get the review dictionary
review = perform_review(
    paper_txt,
    model,
    client,
    num_reflections=5,
    num_fs_examples=1,
    num_reviews_ensemble=5,
    temperature=0.1,
)
# review = perform_review(
#     paper_txt,
#     model,
#     client,
#     num_reflections=1,
#     num_fs_examples=1,
#     num_reviews_ensemble=1,
#     temperature=0.1,
# )
# print(review)
# Inspect review results
# 'Soundness': 4, 'Presentation': 4, 'Contribution': 4
print("####review",review)
print("Rating:", review["Overall"])    # Overall score (1-10)
soundness = review["Soundness"]
presentation = review["Presentation"]
contribution = review["Contribution"]
print("Soundness:", soundness)
print("Presentation:", presentation)
print("Contribution:", contribution)
print("Decision:", review["Decision"])   # 'Accept' or 'Reject'
print("Weaknesses:", review["Weaknesses"]) # List of weaknesses (strings)


# from openai import OpenAI

# 
# client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="")

# 
# model = "deepseek-chat"
# system_message = ""
# user_message = ""

# 
# msg_history = [{"role": "user", "content": user_message}]

# 
# try:
#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": system_message},
#             *msg_history,
#         ],
#         temperature=0.7,
#         max_tokens=4096,
#         n=1,
#         stop=None,
#     )
    
#     
#     content = response.choices[0].message.content
#     print("", content)
# except Exception as e:
#     print("", str(e))