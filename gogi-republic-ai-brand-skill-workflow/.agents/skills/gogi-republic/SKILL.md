---
name: gogi-republic
description: Use when creating or reviewing Gogi Republic marketing copy, promotional flyers, landing pages, menu highlights, or founder communications that need the brand voice, visual identity, and existing image pack.
---

# Gogi Republic

## Purpose and sources

Make every piece sound like Min-Jae "MJ" Park talking to regulars over a hot grill.
Gogi Republic is his five-location Korean BBQ chain in Los Angeles, founded in 2019.
The locations are Koreatown, Sawtelle, Silver Lake, Long Beach, and Pasadena.
Guests grill at the table, share meat and banchan, and stay for another round.

This practice uses **prompts 1 through 3**: create the skill, apply it to a promotional flyer, then apply it to a landing page. Carry out the current request only.

Resolve these paths from the project root, three directories above this skill folder:

- `brand/gogi_republic_brand_bible.md`: source of truth for brand facts and direction; read before drafting.
- `README.md`: practice scope and the six-asset inventory.
- `docs/prompts/prompt_1_create_brand_skill.md`: setup brief.
- `docs/prompts/prompt_2_promotional_flyer.md`: flyer brief.
- `docs/prompts/prompt_3_landing_page.md`: landing-page brief.

Use the current brief for event details, offers, and calls to action. Do not turn sample copy into current business facts or invent prices, addresses, dates, booking URLs, or menu claims. Ask for missing information needed to finish the requested piece.

## Voice

- Hungry, playful, communal, and direct; confident without sounding fancy.
- Write like MJ knows the people at the table. Use natural invitations: "bring your people," "pass the tongs," "save room."
- Include at least one concrete food or table detail per piece: smoke, char, sizzle, crunch, a cold glass, or a hot grill.
- Keep sentences and promotional paragraphs short. Let the room feel loud, warm, and social.
- Be cheeky only when the joke earns its place. Exclamation marks are rare and must serve the piece.
- Mention the specific location when relevant. Speak to friends, families, food lovers, and teams sharing a table.

## Vocabulary and avoid words

Prefer: grill, sizzle, char, smoke, banchan, ssamjang, galbi, pork belly, short rib, table, crew, round two, cold glass.

Useful phrases:

- "Pass the tongs."
- "Wear the jacket that can handle smoke."
- "The grill is already hot."
- "Bring your people. We will bring the banchan."

Avoid in finished brand copy:

- luxury, premium, elevated, curated, bespoke
- authentic journey, fusion experience, culinary destination
- "discover Korea" framing, fake authenticity, and fusion language
- forced slang, fake hype, generic nightlife copy, and luxury-lounge language
- explaining Korean food at length or adding Korean terms merely to sound branded

Replace abstract praise with something the guest can taste, hear, or share.
For example, replace "an elevated culinary journey" with "galbi on the grill and banchan within reach."

## Menu language

Use the brand bible's menu anchors and their spelling:

| Category | Anchors |
| --- | --- |
| Meats | galbi, pork belly, brisket, spicy chicken, ribeye cap |
| Banchan | kimchi, pickled daikon, cucumber muchim, bean sprouts, scallion salad |
| Sauces | ssamjang, sesame salt, gochujang glaze |
| Drinks | soju, makgeolli, iced barley tea, cold beer |

Use familiar dish names with a concrete sensory detail or table action, such as "Pork belly on the grill. Pass the ssamjang."
These anchors guide copy; they are not a complete priced menu. Do not invent sourcing, dietary assurances, portion sizes, or availability.
The communal tone should welcome guests who choose iced barley tea as naturally as those who choose beer.

## Signature phrase and sign-off

- Signature phrase: **Grill loud, eat louder.** Preserve wording, capitalization, and punctuation.
- Use the signature at most once per piece. Prompts 2 and 3 require it exactly once; prompt 3 places it in the footer.
- Good placements are a closing line, flyer footer, or landing-page tag. Avoid repeating it in headings and body copy.
- Sign-off: **MJ and the crew.** Preserve the final period.
- Close signed brand messages and the landing-page founder note with that sign-off. For the promotional flyer, use it as the closing attribution. Do not append it to navigation, menu labels, or every section.

## Palette

Keep these exact brand colors. The application roles below translate the palette into practical layout choices.

| Color | Hex | Application |
| --- | --- | --- |
| Grill Black | `#101010` | Main dark surfaces and strong text |
| Ember Red | `#F24B2E` | Primary accents, emphasis, and calls to action |
| Hot Coal | `#6D1F16` | Deep supporting panels or accents |
| Banchan Cream | `#F7EFE2` | Light surfaces and text on dark backgrounds |
| Steel | `#A6A09A` | Secondary labels, borders, and quiet details |
| Ssam Green | `#4E7D3A` | Small menu or supporting accents |

Favor Grill Black and Banchan Cream for readable text contrast. Check contrast for the actual text size, especially over photographs; use a solid panel or overlay where needed.

## Type

- Headings: bold condensed sans, tight and loud. Keep headline hierarchy clear.
- Body: clean, readable, unfussy sans serif.
- Accents: monospace or label-style caps for menu tags and location stamps.
- No specific font family is mandated by the brand bible. Choose available fonts that match these categories and provide suitable fallbacks; do not present a chosen family as an official brand font.

## Existing asset selection

**Do not generate or regenerate images during this practice.** Reuse the original assets without overwriting or renaming them. Layout-level cropping, positioning, and overlays may use CSS while preserving the source files.

All six images below are present. Recheck availability when applying this skill. Report any missing required asset instead of generating a replacement.

| Project-root asset path | When to use it |
| --- | --- |
| `assets/hero_grill_table.png` | Main hero for a flyer or landing page introducing the shared grill-table experience. |
| `assets/texture_grill_flame.png` | Supporting background or section texture when emphasizing heat, smoke, char, or grill energy. Keep text readable. |
| `assets/texture_banchan.png` | Supporting menu or sharing section, emphasizing banchan and the table's variety. |
| `assets/texture_neon_table.png` | Ambient branding for evening energy, social sections, or background accents; keep copy grounded in food and people. |
| `assets/mj_portrait.png` | Founder note, about-MJ section, or a personal brand message. Do not use it as the food hero. |
| `assets/logo_concept.png` | Brand identification in headers, flyer mastheads, or footers. Preserve its proportions; it is the supplied concept logo. |

Inspect selected images before final placement to choose crops that preserve their subjects and to write accurate alt text. Treat purely decorative textures as decorative.
Choose assets by purpose; every deliverable does not need all six.
From `flyer/index.html` or `landing/index.html`, image references use `../assets/<filename>`. Verify each referenced file exists.

## Sample voice

From the brand bible:

> Bring the group that says they are just doing one round. We both know how this ends.

> The grill is hot, the kimchi is loud, and the first pour is already sweating on the table.

Example of a complete short brand message:

> Bring your people. The grill is already hot.
> Pass the tongs, make room for the galbi, and keep the banchan moving.
>
> Grill loud, eat louder.
>
> MJ and the crew.

Off-brand example, for contrast only:

> Join us for an elevated culinary journey through premium Korean flavors.

## Applying the practice

- **Prompt 1:** Produce `AGENTS.md` and this skill. Keep this file under 350 lines and retain YAML `name` and `description`.
- **Prompt 2:** Follow its campaign brief for a one-page responsive flyer in `flyer/index.html`, with final copy and used image paths in `outputs/flyer_copy.md`. Use the logo, one hero image, and at least one texture. Include the signature exactly once and the sign-off.
- **Prompt 3:** Build `landing/index.html` with header, hero, menu highlights, locations, catering block, founder note, booking CTA, and footer. Use "Book a table" and "Ask about catering" as CTAs. Include all five locations and the signature once in the footer; sign the founder note. Confirm action destinations from the brief instead of inventing links.

## Before delivery

Check the current brief's required sections and facts; the food or table detail; short, natural voice; avoid words; exact signature count and sign-off; palette and type; appropriate existing assets and working paths. Report unresolved source or asset gaps. Keep the brand bible and original images unchanged.
