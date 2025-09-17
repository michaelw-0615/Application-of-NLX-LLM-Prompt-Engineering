# Phase 2: Prompt Documentation

Below are design notes for six prompts (three per task). For each, we summarize: **Design rationale**, **Expected output characteristics**, and **Potential failure modes with mitigations**. This documentation is aimed at creating reproducible benchmarking in Phase 3, or the testing and evaluation phase.

## Task A: Information Synthesis
### CLEAR Prompt
**Prompt content**. 

You’re an equity research analyst. You will process a batch of 10-K excerpts for your customer and return, for EACH document, exactly:
1) a ≤250-word analyst brief with four sections (Results Snapshot → Key Drivers → Outlook & Risks → Follow-ups), and
2) one JSON object matching the schema at the end of this message.

Rules:
- Use ONLY the provided text. If evidence for a field is missing, write “unavailable in provided 10-K excerpt” in the brief and set that JSON field to null.
- Normalize units: YoY/QoQ in percentage points (one decimal), operating margin delta in bps (integer), currency in USD millions if mentioned.
- Every numeric claim in the brief must be backed by a citation present in the JSON `citations` array.
- For each input block, output the brief first, then the JSON. Keep the same order as inputs.
BATCH INPUT: Attached to chatbox in the format of PDF
JSON SCHEMA (for each company)

```json
{
  "company": "string",
  "period": "e.g., FY2024",
  "revenue_yoy_pct": 0.0,
  "op_margin_bps_delta": 0,
  "guidance_change": "raise|maintain|lower|n/a",
  "top_drivers": ["string", "string"],
  "top_risks": ["string", "string"],
  "citations": ["doc:{DOC_ID} p.X ¶Y", "doc:{DOC_ID} p.Z table:RowLabel"]
}
```

**Design rationale.** The CLEAR prompting structure (Context, Length, Examples, Audience, Role) makes constraints explicit for a high-precision, evidence-bound summarization task. It front-loads the schema, unit normalization (pp/bps/USD mm), and citation policy so the model writes to designated specifications rather than free-forming.

**Expected output characteristics.**

- One ≤250-word brief with four sections: Results Snapshot → Key Drivers → Outlook & Risks → Follow-ups.
- One strict JSON object conforming to the shared schema; values normalized (YoY to 1 decimal pp; margin deltas in bps).
- Citations for every numeric claim, pointing to page/paragraph/table anchors.

**Potential failure modes & mitigations.**

- Hallucinated facts or missing citations. Mitigate by: “sources only” rule; require citation coverage and invalidate uncited numerics.
- Schema drift/invalid JSON. Mitigate by explicit “JSON-only” gate and example skeleton; add a final “validate JSON parsability” instruction.
- Accounting ambiguity (GAAP vs CC/Non-GAAP). Mitigate by defaulting to GAAP unless the text explicitly states otherwise; instruct to disclose basis in the brief.
- Excess length. Mitigate with explicit ≤250-word cap and section headers.

### Few-Shot Prompt
**Prompt content.**

[Example 1 Input]

Company: American Express Company (AMEX) | Period: FY2015 | Doc ID: AMEX-10K-2015

https://s26.q4cdn.com/747928648/files/doc_financials/2024/q4/65345cb2-3baf-42fd-ad88-968e29a7264a.pdf

[Example 1 Output]

- Results Snapshot. AMEX’s total revenues net of interest expense fell 4% YoY to $32.8bn (doc:AMEX-10K-2015 p.64 table). Operating margin is not presented on a GAAP basis in the filing for this business model; therefore margin delta is unavailable.
- Key Drivers. Billed-business growth was offset by a lower average discount rate and higher contra-discount rewards(cash rebates) (doc:AMEX-10K-2015 p.65 ¶TOTAL REVENUES NET OF INTEREST EXPENSE).
- Outlook & Risks. FX exposure from international operations and continued discount-rate pressure are highlighted (doc:AMEX-10K-2015 p.64–65).
- Follow-ups. Clarify 2016 margin framework and the sensitivity to discount-rate moves; quantify FX headwinds in basis points.

    ```json
    {
        "company": "American Express Company",
        "period": "FY2015",
        "revenue_yoy_pct": -4.0,
        "op_margin_bps_delta": null,
        "guidance_change": "n/a",
        "top_drivers": ["billed business growth", "lower average discount rate", "higher cash-rebate rewards"],
        "top_risks": ["foreign exchange exposure", "discount-rate pressure"],
        "citations": [
            "doc:AMEX-10K-2015 p.64 table:Summary of Financial Performance",
            "doc:AMEX-10K-2015 p.65 ¶TOTAL REVENUES NET OF INTEREST EXPENSE"
        ]
    }
    ```


[Example 2 Input]

Company: 3M | Period: FY2024 | Doc ID: MMM-10K-2024

https://www.sec.gov/Archives/edgar/data/66740/000089710104000425/mmm041053s1_10k.htm 

[Example 2 Output]

- Results Snapshot. Net sales −0.1% YoY to $24.6bn (GAAP); operating margin rebounded to 19.6% from (43.4)% in 2023 (+6,300 bps), reflecting the lapping of prior-year litigation charges and restructuring effects (doc:MMM-10K-2024 Item 7 table).
- Key Drivers. Spending discipline, sourcing actions, restructuring, higher selling prices, and productivity supported earnings (doc:MMM-10K-2024 Item 7 narrative).
- Outlook & Risks. Ongoing sensitivity to volumes, manufacturing/supply-chain, inflation, and regional demand(China/Europe) is noted (doc:MMM-10K-2024 Item 7 narrative).
- Follow-ups. Break out non-recurring items vs. structural margin lift; quantify 2025 mix/pricing assumptions.

    ```json
    {
        "company": "3M Company",
        "period": "FY2024",
        "revenue_yoy_pct": -0.1,
        "op_margin_bps_delta": 6300,
        "guidance_change": "n/a",
        "top_drivers": ["spending discipline & sourcing actions", "restructuring", "higher selling prices & productivity"],
        "top_risks": ["lower volumes", "manufacturing/supply-chain headwinds", "inflation and China/Europe demand"],
        "citations": [
            "doc:MMM-10K-2024 Item 7 table:Additional financial information (GAAP)",
            "doc:MMM-10K-2024 Item 7 ¶drivers/headwinds"
        ]
    }
    ```

NOW PROCESS THIS BATCH (keep outputs in the same order): Attached as PDF files.

STRICT OUTPUT: For each block, print the brief (≤250 words) followed by exactly one JSON object matching this schema:

```json
{
  "company": "string",
  "period": "e.g., FY2024",
  "revenue_yoy_pct": 0.0,
  "op_margin_bps_delta": 0,
  "guidance_change": "raise|maintain|lower|n/a",
  "top_drivers": ["string", "string"],
  "top_risks": ["string", "string"],
  "citations": ["doc:{DOC_ID} p.X ¶Y", "doc:{DOC_ID} p.Z table:RowLabel"]
}
```

**Design rationale.** Two in-distribution examples (e.g., “SEC approves bitcoin ETFs” → crypto_etf, “Nvidia … most valuable” → valuation_milestone) anchor label semantics and evidence granularity (minimal span), reducing ambiguity and boosting early F1.

**Expected output characteristics.**

- JSON array; each object mirrors the examples’ compact style.
- Consistent evidence spans (short, decisive trigger phrases).
- Stable sentiment mapping from headline framing.

**Potential failure modes & mitigations.**

- Over-generalization from narrow examples. Mitigate by adding one neutral and one negative exemplar later (pilot feedback).
- Ticker leakage to non-equities (e.g., BTC). Mitigate with explicit “non-equity → null.”
- Event boundary errors (valuation vs macro_market). Mitigate with a cue list inside the prompt and post-run error sampling to tune wording.

### Chain-of-Thought Prompt

**Prompt content.** 

You will silently plan the steps (locate numbers → normalize units → verify evidence → compose brief → validate JSON), but DO NOT reveal your chain-of-thought. Use only the provided text.

INPUT (JSON array of documents):

```json
{
  "docs": [
    {
      "company": "{COMPANY_1}",
      "period": "{FISCAL_YEAR_1}",
      "doc_id": "{DOC_ID_1}",
      "doc_text": "{DOC_TEXT_1}",
      "table_text": "{TABLE_TEXT_1}"
    },
    {
      "company": "{COMPANY_2}",
      "period": "{FISCAL_YEAR_2}",
      "doc_id": "{DOC_ID_2}",
      "doc_text": "{DOC_TEXT_2}",
      "table_text": "{TABLE_TEXT_2}"
    }
    // ... repeat for all companies
  ]
}
```

CONSTRAINTS
- Normalize: YoY in pp (1 decimal), operating-margin delta in bps (integer), currency in USD millions if mentioned.
- If evidence is missing for any field, set it to null and state “unavailable in provided 10-K excerpt” in the brief.
- Every numeric claim must have a corresponding citation anchor in `data.citations`.

INPUT: Attached as PDF files.

OUTPUT (JSON only; no extra prose):

```json
{
  "results": [
    {
      "company": "{COMPANY_1}",
      "period": "{FISCAL_YEAR_1}",
      "narrative": "≤250-word brief here ... (doc:{DOC_ID_1} p.X ¶Y) ...",
      "data": {
        "revenue_yoy_pct": 0.0,
        "op_margin_bps_delta": 0,
        "guidance_change": "raise|maintain|lower|n/a",
        "top_drivers": ["...", "..."],
        "top_risks": ["...", "..."],
        "citations": ["doc:{DOC_ID_1} p.X ¶Y", "doc:{DOC_ID_1} p.Z table:RowLabel"]
      }
    }
    // ... one object per input, same order
  ]
}
```

