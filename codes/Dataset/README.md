# DATASET GENERATION

To evaluate our framework autonomously and comprehensively, we developed an extensive suite of synthetically augmented datasets, totaling **2,143 meticulously designed questions**. These datasets were crafted to test every aspect of our pipeline across diverse scenarios and data generation techniques. By ensuring robust and unbiased dataset creation through multiple generation methods, we have set the foundation for a thorough and reliable evaluation of our retrieval strategies and overall framework performance.

---

## INSTALLATION  AND RUNNING THE FILES

### Install the required dependencies

`pip install -r requirements.txt`


## Generalised Dataset

Our journey began with the creation of a **foundational dataset of 323 question-answer pairs**, handpicked from frequently encountered queries in the Mergers and Acquisitions (MnA) sector. Sourced from real-world data, these queries were enhanced using a large language model (LLM) to expand their scope and address edge cases. Each question is paired with its ideal outputs, providing a gold standard for evaluating accuracy and consistency.

##  RAGAS

To simulate real-world complexities, we leveraged the **RAGAS library** to create persona-driven scenarios tailored for financial and legal analysts. This yielded a dataset of **501 questions**, reflecting the breadth of challenges these roles might encounter in case study merger analysis reports. The dataset focuses on query orientation, categorized by complexity described by the knowledge graph:

1. **Single-hop queries**: Requiring precise answers from individual chunks.
2. **Multi-hop specific queries**: Necessitating reasoning across interconnected chunks, pushing the limits of advanced retrieval strategies like re-ranking.

## Comprehensive Chunk Coverage - MLFlow

Using MLFlow's test dataset strategy, we developed a dataset of **306 questions and their ideal chunks**. This approach focused on comprehensive chunk coverage, ensuring that every significant segment of the source documents was represented and tested. This dataset evaluates all aspects of the retrieval strategy of our pathway-enabled RAG tool.

## Legal Compliance Dataset

To verify the legal aspect of our framework, we created a dataset of **301 queries** focusing on merger guidelines that companies must follow during the merger and acquisition period. This holistic compliance dataset helps us assess the framework's performance on legal use cases within the MnA field.The queries range from simple to highly complex legal scenarios, representing the nuanced challenges in this domain.

Legal queries often present unique complexities due to their reliance on:
- Precise language.
- Contextual interpretation.
- Compliance requirements.

This dataset plays a pivotal role in assessing the robustness of our RAG system, testing its ability to extract relevant information, navigate intricate legal language, and provide accurate, context-aware responses.

## Long Form Q&A

To address the need for more complex and nuanced evaluations, we isolated **150 MnA case studies** and generated **1,013 intricate queries**. These queries involve deep reasoning, multi-step problem-solving, and long-form responses, mirroring real-world challenges. By integrating this dataset, we push the boundaries of our framework’s capabilities, particularly in generating detailed reports and managing agentic handoffs.

Each query across all datasets is addressed with precise and well-articulated answers, leveraging the capabilities of large language models (LLMs). These responses reflect the depth and clarity required for practical scenarios. 

The **detailed report-style responses** include:
- Comprehensive explanations.
- Contextual insights.
- Relevant justifications.

These outputs meet the high standards expected in professional settings, establishing a robust benchmark for assessing the system's performance in addressing complex scenarios.

