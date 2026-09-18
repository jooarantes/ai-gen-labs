# 🥩 Gogi Republic — AI Brand Workflow

> A practical case study demonstrating how a custom AI Brand Skill can capture a company's voice and consistently apply it across multiple marketing assets.

---

## Overview

This repository demonstrates an end-to-end workflow for transforming a company's brand identity into reusable AI instructions.

Instead of prompting an AI from scratch every time new marketing material is needed, this project shows how a **Brand Skill** can encapsulate the company's personality, tone, positioning, visual direction, and communication principles.

Once the skill exists, it becomes the foundation for generating consistent marketing assets such as:

- Landing pages
- Promotional flyers
- Marketing copy
- Future campaigns
- Brand communications

The business used in this case study is **Gogi Republic**, a Korean BBQ restaurant with five locations across Los Angeles.

---

# Project Goal

The objective is **not** to build the best prompt.

The objective is to demonstrate a scalable workflow where:

```
Brand Knowledge
        │
        ▼
Brand Skill
        │
        ▼
Consistent AI Outputs
```

This repository illustrates how a single AI skill can preserve a brand's voice across different deliverables.

---

# Repository Structure

```text
.
├── assets/
│   ├── hero_grill_table.png
│   ├── texture_grill_flame.png
│   ├── texture_banchan.png
│   ├── texture_neon_table.png
│   ├── mj_portrait.png
│   └── logo_concept.png
│
├── brand/
│   └── gogi_republic_brand_bible.md
│
├── docs/
│   └── prompts/
│       ├── prompt_1_create_brand_skill.md
│       ├── prompt_2_promotional_flyer.md
│       └── prompt_3_landing_page.md
│
└── README.md
```

---

# Repository Components

## Brand

The `brand/` directory contains the complete Brand Bible used throughout the project.

It defines:

- Brand personality
- Core values
- Target audience
- Tone of voice
- Messaging
- Visual identity
- Writing principles
- Communication guidelines

This document acts as the single source of truth for every AI-generated output.

---

## Assets

The `assets/` folder contains six pre-generated visual assets used during the exercises.

These images are intentionally fixed.

Their purpose is to serve as visual references for the Brand Skill rather than examples for image generation.

| Asset | Purpose |
|--------|---------|
| hero_grill_table.png | Hero section |
| texture_grill_flame.png | Background texture |
| texture_banchan.png | Supporting visual texture |
| texture_neon_table.png | Ambient branding |
| mj_portrait.png | Founder portrait |
| logo_concept.png | Brand logo |

---

## Documentation

The `docs/prompts` directory contains the complete workflow used in this project.

### Prompt 1

Builds the reusable Brand Skill from the Brand Bible.

Output:

- `AGENTS.md`
- `.agents/skills/gogi-republic/SKILL.md`

---

### Prompt 2

Uses the Brand Skill to generate a promotional flyer announcing the Koreatown location.

---

### Prompt 3

Uses the Brand Skill to generate a complete landing page while preserving the same brand voice.

---

# Workflow

```text
Brand Bible
      │
      ▼
Prompt 1
(Create Brand Skill)
      │
      ▼
Reusable Brand Skill
      │
      ├──────────────┐
      ▼              ▼
Prompt 2        Prompt 3
 Flyer        Landing Page
```

The Brand Skill becomes the reusable knowledge layer that every future communication can leverage.

---

# Learning Objectives

By exploring this repository, you will learn how to:

- Convert brand documentation into AI-readable instructions.
- Build reusable Brand Skills.
- Maintain a consistent tone of voice across multiple deliverables.
- Separate business knowledge from task-specific prompts.
- Create scalable AI workflows for marketing teams.

---

# Included Practice

This project includes three practical exercises.

| Step | Description |
|------|-------------|
| 01 | Build the Brand Skill |
| 02 | Generate a promotional flyer |
| 03 | Generate a landing page |

Each exercise builds upon the previous one to demonstrate how reusable brand knowledge improves consistency.

---

# Why This Matters

One of the biggest challenges in AI-assisted marketing is maintaining consistency.

Without reusable brand knowledge, every prompt starts from zero.

By encapsulating the company's identity into a Brand Skill, every future interaction begins with the same foundation, reducing prompt complexity while improving quality and consistency.

---

# Technologies

- Markdown
- Prompt Engineering
- AI Brand Skills
- AI Agents
- Structured Documentation
- Brand Systems
- Marketing Workflow Design

---

# License

This repository is intended for educational purposes and demonstrates AI workflow design using a fictionalized marketing case study based on Gogi Republic.