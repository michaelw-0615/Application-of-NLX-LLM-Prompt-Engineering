# Phase 1: Domain Selection and Task Framework

## Overall Goal
This project is aimed at establishing a concrete, executable evaluation framework for three popular Large Language Models (LLMs): ChatGPT 5 (proprietary advanced), Claude Sonnet 4.0 (proprietary advanced) and Google Gemini 2.5 Free Tier (proprietary standard) in the domain of finance. The models will be tested on two tasks—information synthesis and classification analysis—both of which require high summarizing and logical reasoning capabilities. We define task scopes, input and output formats and quantitative criteria to enable objective, deployable evaluation benchmarking in the next phases.

## Domain and Problem Framing
In this project, we are evaluating LLMs in the field of fundamental analysis on public-equity. The LLMs will take the user persona of an independent equity analyst producing financial briefs and tagging news flows for potential customers. For the information synthesis task, the annual reports and 10-K forms for financial year 2024 for at least 10 major companies in the US will serve as source material for quantitative evaluation. For the classification analysis task, approximately 40 financial news headlines will be provided for LLMs to perform categorization tasks on a self-created set of tags.

## Task Definitions, Schemas and Evaluation Metrics
  ### Task A: Information Synthesis and Corporate Performance Briefing
  For this task, annual reports of 10 major US companies across three distinct industries, together with their 10-K forms, are provided. LLMs are expected to condense these companies’ latest operation results into a one-page analyst brief while capturing key numbers and drivers with source citations. The input will be annual reports (in plain text) as well as their attached 10-K excerpts. The output will be a 250-word briefing structured as Results Snapshot → Key Drivers → Outlook/Risks → Follow-ups, as well as a .json object:

  ```json
  {
      "period": "Q2 FY2025",
      "revenue_yoy_pct": 0.0,
      "op_margin_bps_delta": 0,
      "guidance_change": "raise|maintain|lower|n/a",
      "top_drivers": ["...","..."],
      "top_risks": ["..."],
      "citations": ["press p2 ¶3", "10-K p12 ¶1"]
  }
  ```

  The output will be evaluated on the following criteria:

  **Schema Validity Rate:** The proportion of parsable .json files, categorized into 4-point scales (>98%--4; 95-98%--3; 90-95%--2; <90%--1)

  **Fact Accuracy:** The proportion of exact-matches for revenue_yoy_pct and op_margin_bps_delta indices categorized into 4-point scales (>95%--4; 90-95%--3; 75-90%--2; <75%--1)

  **Citation Coverage:** Percentage of numerical claims with at least one correct citation span, categorized into 4-point scales (>95%--4; 90-95%--3; 80-90%--2; <80%--1)

  **Coverage and Overall Readability:** Percentage of briefings including all four narrative sections, categorized into 4-point scales (>95%--4; 90-95%--3; 80-90%--2; <80%--1)

  ### Task B: Classification Analysis on Financial Headlines
  For this task, LLMs are given tag headlines with event type, sentiment, and focal ticker, and are expected to return a short evidence snippet. The output should be a .json object structured as:

  ```json
  {
      "event_type": "earnings|M&A|guidance|regulatory|macro|other",
      "sentiment": "pos|neu|neg",
      "ticker": "AAPL",
      "evidence": "trigger phrase or cue"
  }
  ```
    
  The output will be evaluated on the following criteria:

  **Event-Type Macro-F1:** The F1-score for all event-type tags, categorized into 4-point scales (>90%--4; 80-90%--3; 70-80%--2; <70%--1)

  **Sentiment Macro-F1:** The F1-score for all sentiment tags, categorized into 4-point scales (>95%--4; 90-95%--3; 75-90%--2; <75%--1)

  **Ticker Macro-F1:** The F1-score for all ticker tags, categorized into 4-point scales (>95%--4; 90-95%--3; 75-90%--2; <75%--1)
