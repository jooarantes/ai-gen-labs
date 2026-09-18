# Gogi Republic project guidance

## Scope

This practice uses **prompts 1 through 3** in `docs/prompts/`:

1. Create this file and `.agents/skills/gogi-republic/SKILL.md`.
2. Apply the skill to a promotional flyer.
3. Apply the skill to a landing page.

Complete only the prompt currently requested. Creating the skill does not also request the flyer or landing page.

## Sources and skill

- Read `brand/gogi_republic_brand_bible.md` as the source of truth for brand identity, voice, menu, and visual direction.
- Read `README.md` for the exercise workflow and asset inventory.
- For Gogi Republic copy, flyers, landing pages, or other brand communications, read and apply `.agents/skills/gogi-republic/SKILL.md` before creating the deliverable.
- Use the current prompt for campaign details. Ask for material missing facts instead of inventing dates, prices, addresses, booking links, or offers.

## Fixed images

Do not generate or regenerate images during this practice. Reuse the supplied files in `assets/` and preserve their contents and filenames.

All six images listed in the main README are present. The skill documents when to use each one. Recheck availability before use and report any missing required file instead of generating a replacement.

## Brand essentials

- Write like MJ talking to regulars: hungry, playful, communal, direct, and concrete.
- Include a food or table detail in each piece; keep promotional lines short.
- Preserve the exact signature phrase `Grill loud, eat louder.` Use it at most once per piece, or exactly once when the current prompt requires it.
- Use the exact sign-off `MJ and the crew.` for signed brand copy and founder notes.
- Follow the skill's vocabulary, palette, type, menu, and asset guidance.
- Treat this repository as an educational case study; example copy is not confirmation of a real event.

## Delivery checks

Keep `SKILL.md` under 350 lines with YAML frontmatter containing `name` and `description`. Check requested sections, exact brand wording, and asset paths before delivery. For later HTML outputs, resolve image paths from the output file's directory.

## Local shell convention

Follow `~\.codex\RTK.md`: prefix shell commands with `rtk`.
