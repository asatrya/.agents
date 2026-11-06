# Field coverage report format

Use the **reference document** in this project as the pattern for structure and style:

## Sections to include

1. **Title and intro**
   - "Field Coverage" (or similar).
   - Link to original support ticket.
   - Short explanation: how we can (and cannot) fulfill the request using existing dbt models.

2. **Source models used**
   - Bullet list of the dbt models (and optionally sources) that back the extract, with one-line descriptions (grain, key columns).

3. **Per-table field mapping**
   - For each requested table:
     - State **grain** (e.g. one row per order) and any filters (e.g. `placedAt < 2020-04-01`).
     - Markdown table:
       - **Requested field**
       - **Source / expression** (existing models): model name and column or SQL expression.
       - **Status**: e.g. **Supported**, **Derived (supported)**, **Approximate / derived**, **Not modeled**, **Not available (PII)**.
   - **Summary** for that table (one short paragraph).

4. **PII and fallback** (if relevant)
   - Which fields are excluded for PII; what identifiers are provided instead (e.g. customerId, externalCustomerId).
   - Note if email or other PII would require separate model extensions.

5. **Overall**
   - If the request cannot be fully fulfilled, state clearly why (missing critical fields, wrong grain, etc.).

## Status labels (reference)

- **Supported**: Direct or simple rename from an existing column. Use only when you have clear evidence.
- **Derived (supported)**: Aggregation or expression (e.g. sum, max, coalesce) from existing columns.
- **Approximate / derived**: Best-effort proxy (e.g. tax_method as priceMethod). Use only when the mapping is clear; if not sure, use **Not modeled** and note what would need to be verified.
- **Not modeled**: No corresponding column or logic in current models (or uncertain; prefer this when in doubt).
- **Not available (PII)**: Field does not exist in the project (or in any joinable parent) for privacy/design reasons.
- **Available (PII) / Available via join**: Field exists in a model that is already `ref()`’d by the candidate. Not selected in the curated model; can be added in an ad-hoc extract subject to PII governance.

**Rule:** If not sure, do not state **Approximate** or **Supported**. Use a conservative status and describe what would need to be verified.
