# Generative AI Labs

A practical laboratory for exploring generative AI applications, agentic workflows, prompt engineering, structured documentation, and AI-assisted automation.

The repository brings together focused projects that turn AI concepts into documented, reproducible experiments. Each project explains the problem, the approach, the artifacts produced, and the limitations of the work.

## Repository scope

- LLM applications and AI-assisted workflows
- Prompt engineering and reusable AI skills
- Agent orchestration and tool use
- Data analysis and workflow automation
- Structured outputs and documentation-driven execution
- Brand, content, and marketing workflows
- Evaluation, reproducibility, and explicit limitations

## Projects

| Project | Problem addressed | Approach | Main deliverables |
| --- | --- | --- | --- |
| [AI Data Analyst Agent](./ai-assistant-data-analyst/) | Repetitive and inconsistent processing of customer research data. | A process-oriented AI agent coordinates documented skills and Python scripts for validation, cleaning, consolidation, metric calculation, and dashboard generation. | NPS and CSAT dashboards, reusable data process documentation, specialized skills, and executable Python scripts. |
| [Gogi Republic AI Brand Workflow](./gogi-republic-ai-brand-skill-workflow/) | Maintaining a consistent brand voice across multiple AI-generated marketing assets. | A Brand Bible is transformed into a reusable Brand Skill and applied to promotional and landing-page workflows. | Brand documentation, reusable AI instructions, fixed visual assets, prompt workflow, flyer, and landing-page materials. |

## Project categories

### Agentic data workflows

The [AI Data Analyst Agent](./ai-assistant-data-analyst/) demonstrates how an AI agent can execute a predefined analytical process instead of improvising business rules. The project covers:

- input validation and data-quality checks;
- cleaning and standardization with pandas;
- historical consolidation of monthly NPS files;
- NPS and CSAT calculations;
- HTML dashboard generation; and
- process memory and operational documentation through Markdown and Obsidian.

The project includes a demonstrative NPS workflow covering April to June 2026 and a point-in-time customer-satisfaction analysis. Its results are based on versioned project data and are not presented as official business indicators.

### Prompt and brand-skill workflows

The [Gogi Republic AI Brand Workflow](./gogi-republic-ai-brand-skill-workflow/) is an educational case study showing how brand knowledge can be organized into reusable AI instructions. The workflow separates:

- brand knowledge and identity;
- reusable skill instructions;
- task-specific prompts; and
- final marketing deliverables.

The case study uses a fictionalized Korean BBQ restaurant context and includes exercises for creating the Brand Skill, producing a promotional flyer, and generating a landing page.

## Technologies and practices

- Python and pandas
- HTML, CSS, and JavaScript
- Chart.js
- Markdown-based technical documentation
- Prompt engineering and AI skills
- Agentic workflows and process orchestration
- Data cleaning, ETL, and dashboard generation
- Git and GitHub Pages-oriented artifacts
- Obsidian as a knowledge and process-documentation layer

## Repository structure

```text
.
├── README.md
├── ai-assistant-data-analyst/
│   ├── dados_brutos/
│   ├── dados_tratados/
│   ├── dashboards/
│   ├── processos/
│   ├── .agents/
│   └── README.md
└── gogi-republic-ai-brand-skill-workflow/
    ├── assets/
    ├── brand/
    ├── docs/
    ├── .agents/
    └── README.md
```

## Project documentation conventions

Each project should make the following information explicit whenever it applies:

- problem or objective;
- architecture and workflow;
- models, tools, and dependencies;
- prompts, skills, or context strategy;
- implementation details and reproducible commands;
- generated artifacts and evidence;
- evaluation or validation approach; and
- limitations, assumptions, and next steps.

Projects should distinguish educational demonstrations, prototypes, simulations, and production-validated applications. Claims about business impact or operational performance should only be made when supported by project evidence.

## Getting started

Start with the README inside the project you want to explore:

- [AI Data Analyst Agent README](./ai-assistant-data-analyst/README.md)
- [Gogi Republic AI Brand Workflow README](./gogi-republic-ai-brand-skill-workflow/README.md)

Each project contains its own structure, workflow description, artifacts, and execution guidance.

## Author

João Carlos Arantes
