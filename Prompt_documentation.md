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
