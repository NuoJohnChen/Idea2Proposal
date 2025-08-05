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
# "gpt-4o"#


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
Title:
Lightweight Image Classification Network Based on Feature Extraction Network SimpleResUNet and Attention

Problem Statement:
Traditional CNN-based models for image classification face limitations in capturing global contextual information due to their local receptive fields, hindering performance in tasks requiring long-range dependencies. Lightweight networks (e.g., MobileNet, ShuffleNet) reduce computational costs but often sacrifice accuracy, especially in small-sample scenarios. Existing hybrid architectures (e.g., Res-UNet, TransUNet) improve feature extraction but introduce excessive complexity, making them impractical for resource-constrained environments. There is a critical need for a lightweight yet robust model that balances efficiency with high accuracy, particularly for small datasets.

Motivation & Hypothesis:
We hypothesize that integrating the multi-scale feature fusion of U-Net with the gradient stability of ResNet can enhance feature richness while maintaining computational efficiency. Additionally, replacing traditional normalization and classification layers with adaptive mechanisms (e.g., GroupNorm, Attention) can improve robustness in small-sample settings. Our core idea is that a simplified Residual U-Net (SimpleResUNet) with attention-driven feature selection will outperform existing lightweight models by dynamically emphasizing discriminative features and suppressing noise, even with limited training data.

Proposed Method:
(1) SimpleResUNet Architecture:

ResNet-U-Net Fusion: Design a U-Net-inspired encoder-decoder with residual blocks, enabling skip connections to fuse low-level details and high-level semantics.
Lightweight Adaptation: Replace standard convolutions with depthwise separable convolutions and reduce channel dimensions while preserving multi-scale feature hierarchies.
(2) Feature Scale Normalization:

Adaptive Pooling: Introduce an adaptive average pooling layer to unify feature dimensions across varying input sizes, enabling multi-scale compatibility.
GroupNorm Integration: Replace BatchNorm with GroupNorm in the Attention classifier to stabilize training with small batch sizes.
(3) Attention-Based Classification:

Feature-Sequence Attention: Redesign the self-attention mechanism to operate on the feature sequence output by SimpleResUNet, dynamically weighting features based on their discriminative power.
Gradient Propagation Analysis: Derive gradient formulas for SimpleResUNet to validate its stability and efficiency during backpropagation.
Step-by-Step Experiment Plan:

Validate Feature Extraction Efficacy:

Synthetic Tasks: Test SimpleResUNet on tasks requiring global-local feature fusion (e.g., reconstructing occluded images, detecting multi-scale patterns).
Ablation Study: Compare variants (e.g., without residual connections, with standard U-Net) on CIFAR-10 to isolate the impact of architectural choices.
Benchmark Lightweight Performance:

Efficiency Metrics: Measure FLOPs, parameters, and inference speed against MobileNet, ShuffleNet, and ResNet variants.
Small-Sample Accuracy: Evaluate on MalImg and MalVis datasets with limited training samples (e.g., 10–100 samples per class).
Assess Multi-Scale Adaptability:

Variable Input Sizes: Train and test on datasets with diverse resolutions (e.g., 32×32 to 256×256) to verify robustness of adaptive pooling.
Cross-Dataset Generalization: Pre-train on CIFAR-10 and fine-tune on medical imaging datasets (e.g., ISIC 2018) to test transferability.
Attention Mechanism Analysis:

Feature Activation Maps: Visualize attention weights to identify which features drive classification decisions.
Compare Normalization Strategies: Test GroupNorm vs. BatchNorm/LayerNorm in the classifier under varying batch sizes.
Interpretability and Scalability:

Gradient Propagation Proof: Mathematically demonstrate that SimpleResUNet inherits ResNet’s gradient stability.
Feature Dimension Study: Sweep feature dimensions (3 to 256) to correlate model performance with theoretical sampling principles (Nyquist-Shannon-inspired analysis).
Real-World Deployment:

Edge Device Testing: Deploy the model on resource-constrained hardware (e.g., NVIDIA Jetson Nano) to measure real-time inference throughput.
Robustness Checks: Evaluate performance under noise, adversarial attacks, and dataset shifts to validate practical usability.
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
    num_fs_examples=0,
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
print("####review",review)
print("Overall Quality:", review["Overall_Quality"])    # Overall score (1-10)
novelty = review["Novelty"]
workability = review["Workability"]
relevance = review["Relevance"]
specificity = review["Specificity"]
print("Novelty:", novelty)
print("Workability:", workability)
print("Relevance:", relevance)
print("Specificity:", specificity)
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