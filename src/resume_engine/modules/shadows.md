/* ═══════════════════════════════════════════════════════════════
 * SHADOW SYSTEM — CRITICAL RULES (DO NOT VIOLATE)
 * ═══════════════════════════════════════════════════════════════
 *
 * Rule 1: clip-path elements MUST use filter: drop-shadow()
 *         box-shadow IS CLIPPED by clip-path (CSS spec behavior)
 *
 * Rule 2: Non-clip-path cards use ULTRA-LIGHT box-shadow
 *         Users HATE visible rectangular shadow boxes
 *
 * Rule 3: Page shadow (outer) can be heavier — it's the page, not a card
 * ═══════════════════════════════════════════════════════════════ */

/* .exp-card: has clip-path → filter drop-shadow ONLY, no box-shadow */
/* Located in cards.css — verify after any CSS change */

/* .side-card: no clip-path → ultra-light box-shadow */
/* Located in cards.css — verify: box-shadow: 0 0 0 0.5px, 0 1px 2px */

/* .page: outer page shadow — 3-layer is OK here */
/* Located in base.css */

/* VERIFICATION CHECKLIST:
 * 1. grep 'exp-card.*box-shadow' cards.css → MUST return nothing
 * 2. grep 'exp-card.*filter.*drop-shadow' cards.css → MUST return match
 * 3. grep 'side-card.*box-shadow' cards.css → MUST be ultra-light (0.5px)
 */

