---
name: writing-style-persuasive
description: Compose persuasive educational, ethical, reflective, or faith-oriented writing with question-led reasoning, concrete examples, repetition, contrast, and a warm conversational cadence. Use when the user wants audience-engaging persuasion without imitating a named writer. After drafting, apply a Humanizer-style editorial pass to remove generic AI patterns while preserving the writer's meaning, evidence, sources, and voice.
---

# Writing Style Persuasive

Create writing that helps an audience arrive at an insight, rather than merely receiving a conclusion. This skill captures high-level rhetorical techniques from conversational teaching: direct address, Socratic questioning, concrete demonstrations, progressive explanation, oral rhythm, and reflective application. It does not reproduce any living writer's exact voice, signature wording, or identifiable mannerisms.

## Inputs

Use the user's topic, intended audience, purpose, format, desired length, and source material. If one is missing, infer a reasonable default unless it would change the argument materially.

For source-sensitive subjects, treat the user's supplied facts, quotations, scripture references, and citations as the source of truth. Do not invent quotations, references, stories, or factual claims. If a needed claim is uncertain, flag it for verification or ask for a source.

## Composition pattern

Shape the draft around this progression when it fits the subject:

`familiar behavior or assumption → interruption → question → concrete example → audience participation → principle → consequence → reflective action`

Adapt the pattern rather than forcing every stage into every piece.

1. Identify the audience's likely assumption, habit, fear, or point of confusion. Begin with a recognizable situation, a vivid question, a small contrast, or a concrete scene.
2. Make the audience think. Ask questions that require reasons, not just yes/no agreement. After each important question, supply the reasoning or invite the reader to test it against the example.
3. Explain in small, cumulative chunks. Use a recurring loop of example, question, answer or reframe, and brief recap. Let each chunk prepare the next one.
4. Prefer one strong analogy, demonstration, dialogue, or thought experiment over a pile of weak examples. Explain what the analogy reveals and where it stops applying.
5. Move from the concrete to the principle. Name the deeper issue only after the audience has seen it operate in an ordinary case.
6. Use direct, inclusive address (`you`, `we`, `let us`) where appropriate. Favor clear spoken sentences, varied sentence length, intentional repetition, useful asides, and transitions that sound natural when read aloud.
7. Use contrast when it clarifies the choice: comfort versus truth, imitation versus understanding, command versus conviction, surface symptom versus root cause, or majority opinion versus independent thought. Keep the contrast accurate and avoid false binaries.
8. Connect the principle to a human consequence. Show what changes in judgment, character, relationship, or action; do not leave the insight floating as an abstraction.
9. Close with a memorable restatement, a practical next step, or a reflective question. End by inviting agency rather than demanding performative agreement.

## Human voice pass

Treat composition and humanization as two related passes. First make the reasoning work; then revise for a particular reader and subject. This is adapted from [blader/humanizer](https://github.com/blader/humanizer), whose goal is to edit for human readers rather than to evade AI detectors.

1. State the point directly. Remove staged run-ups (`here's the thing`, `let's dive in`, `honestly?`) and unsupported objections (`this isn't about...`, `a tempting approach would be...`) unless the reader has actually raised that objection.
2. Keep meaningful contrast, but avoid the stock `not X but Y` frame when a plain sentence says the same thing. Do not turn every example into a moral or add a one-line closer that merely announces its importance. Treat phrases such as `at its core`, `at its heart`, `what really matters is`, and `that is the real...` as prompts to state the specific point or cut the sentence.
3. Replace abstract significance with the concrete fact, action, or consequence. Cut inflated language, sales language, vague associations, borrowed authority, and shallow `-ing` claims when the source does not support them. When the source itself contains promotional language, preserve the underlying invitation or benefit while removing unsupported promises such as `a pivotal moment`, `a brighter future`, or `a whole new way`. Prefer ordinary verbs such as `is`, `has`, and `does` when they are accurate.
4. Break visible formulas. Use only as many examples as the idea needs; vary sentence openings and lengths; do not make every paragraph a neat three-part list; and use dashes, fragments, bold, headings, and emojis only when they serve the reader.
5. Remove chatbot residue and document-talk (`Great question`, `I hope this helps`, `this essay will show`, `the paragraph below`). Let the prose discuss the subject rather than narrate the act of writing.
6. Choose specificity over performance. Add a real detail only when it comes from the user's material or a clearly marked example. Never invent a personal experience, name, number, quotation, citation, or source to make the prose feel lived-in.
7. Match a supplied writing sample's rhythm, word choice, punctuation, and deliberate quirks when the user asks for voice matching. Without a sample, aim for clear, warm, restrained prose; do not manufacture slang, typos, intimacy, or a fake personal voice.
8. Read the revision as one person addressing one audience. Remove explanations that audience already knows, but keep the reasoning needed to make the persuasion fair. Preserve the requested structure, length, formatting, claims, quotations, citations, and religious distinctions.

The final pass should be invisible: return the requested polished draft, not a detector score or a list of “humanization” edits, unless the user asks to see the editorial reasoning.

## Tone and safeguards

- Be warm, curious, and intellectually serious. Correct an assumption without humiliating the audience.
- Use repetition to reinforce a key idea, not to pad the draft. Remove rhetorical questions that do not advance the reasoning.
- Keep emotion grounded in the argument. Do not manufacture guilt, fear, certainty, intimacy, or spiritual authority.
- Write fresh language. Do not imitate a named living writer, reproduce recognizable catchphrases, or copy wording from a reference transcript.
- When the subject is religious, preserve reverence and distinguish quotation, paraphrase, interpretation, and personal reflection. Ask for or verify sources instead of fabricating them.
- Define unfamiliar terms on first use. Keep jargon and untranslated terminology proportionate to the audience.
- Do not optimize for defeating AI detectors. Optimize for specificity, honest authorship, and a believable relationship between the writer and the reader.

## Output

Return the requested format and length as a polished draft. For a complex request, provide a compact visible outline first with: hook, central question, example, reframe, consequence, and action. Otherwise, keep the process implicit and deliver the prose.

Before finishing, check that the draft:

- gives the audience a reason to think, not only an instruction to agree;
- contains a clear movement from example to principle to implication;
- uses questions, repetition, and analogy purposefully;
- avoids staged AI-like patterns, generic significance claims, and decorative filler without flattening the writer's personality;
- makes no unsupported factual or source-sensitive claims; and
- ends with a concrete or reflective invitation.
