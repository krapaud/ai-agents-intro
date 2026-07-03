# AI Agents in Python

## Description

An AI Study Guide Generator built with a small multi-agent system. Given a
programming topic (e.g. "Python decorators"), it produces a structured
Markdown study guide containing an explanation, key concepts, an example, a
practice exercise, common mistakes, review comments, and a final summary.

The system uses three agents with distinct responsibilities, connected in a
sequential workflow, plus two deterministic Python tools (file writing and
section validation) to keep the parts of the pipeline that don't need
creativity predictable.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- ~1.5 GB free disk space for the local model

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama (macOS example via Homebrew)
brew install ollama
brew services start ollama

# 4. Pull the local model
ollama pull llama3.2:1b

# 5. Confirm the model responds directly (before touching the agent code)
ollama run llama3.2:1b "Say hello in one short sentence."
```

## Configuration

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

| Variable | Purpose | Example |
|---|---|---|
| `OLLAMA_API_BASE` | URL where the local Ollama server is running | `http://localhost:11434` |
| `MODEL_NAME` | LiteLLM-style model identifier used by all agents | `ollama_chat/llama3.2:1b` |

**Model provider used in this project:** local model `llama3.2:1b` served by
Ollama, accessed through LiteLLM's `ollama_chat/` provider prefix. No API
keys are required. If you have access to another LiteLLM-compatible provider
(Gemini, OpenAI, Claude, etc.), you can swap `MODEL_NAME` for that provider's
model string instead; the agent code itself does not change.

`.env` is gitignored and must never be committed. `.env.example` only lists
variable names, not secrets (this project uses no secrets since Ollama runs
without authentication).

## How to Run

```bash
source .venv/bin/activate
python main.py "Python decorators"
```

If no topic is passed as an argument, the program prompts for one:

```bash
python main.py
Enter a programming topic: Python list comprehensions
```

The generated guide is saved to `output/study_guide.md`.

## Example Input

```bash
python main.py "Python decorators"
```

## Example Output

Console output:

```text
[1/5] Running Explainer Agent for 'Python decorators'...
[2/5] Running Practice Designer Agent...
[3/5] Running Reviewer Agent...
[4/5] Assembling final Markdown and validating sections...
[5/5] Saving Markdown file...
Saved Markdown file to /path/to/output/study_guide.md
Validation: {'is_valid': True, 'missing_sections': []}
```

See [output/study_guide.md](output/study_guide.md) for a full generated
example (topic: Python decorators).

## Project Structure

```text
ai-agents-intro/
├── agents/
│   ├── explainer_agent.py
│   ├── practice_designer_agent.py
│   ├── reviewer_agent.py
│   └── runner_utils.py
├── tools/
│   ├── file_writer.py
│   └── validation.py
├── output/
│   └── study_guide.md
├── data/
│   └── topic_examples.json
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── main.py
```

## Agents

- **Explainer Agent** (`agents/explainer_agent.py`): receives the topic and
  produces a short beginner explanation, a bulleted list of key concepts,
  and one concrete code example.
- **Practice Designer Agent** (`agents/practice_designer_agent.py`):
  receives the topic and the explanation already written, and designs a
  small (10-20 minute) practice exercise with expected input/output and
  hints. It does not repeat the explanation.
- **Reviewer Agent** (`agents/reviewer_agent.py`): receives the assembled
  draft guide and produces a list of common beginner mistakes plus specific,
  actionable review comments. It does not rewrite the guide.

`agents/runner_utils.py` holds the shared logic for running any ADK `Agent`
with a single prompt via `InMemoryRunner` and returning the final text.

## Tools

- **`save_markdown_file`** (`tools/file_writer.py`): deterministic file I/O.
  Given a path and Markdown content, creates parent directories if needed,
  writes the file, and returns a success message or a clear error.
- **`validate_required_sections`** (`tools/validation.py`): deterministic
  structural check. Scans the final Markdown (ignoring fenced code blocks)
  for the required headings (`Topic`, `Simple Explanation`, `Key Concepts`,
  `Example`, `Practice Exercise`, `Common Mistakes`, `Review Comments`,
  `Final Summary`) and reports which, if any, are missing.

## Self-Validation Checklist

- [x] Project runs locally end to end with `python main.py "<topic>"`.
- [x] At least three agents exist, each with a distinct responsibility.
- [x] At least two deterministic Python tools exist and are used in the
      workflow (`save_markdown_file`, `validate_required_sections`).
- [x] Final output is saved as Markdown in `output/study_guide.md`.
- [x] Tested with multiple topics ("Python decorators", "Python list
      comprehensions", "HTTP status codes", "Recursion").
- [x] Validation tool correctly reports missing sections when tested against
      an incomplete draft.
- [x] `.env` is gitignored; `.env.example` documents variable names only.
- [x] README documents setup, configuration, usage, and known limitations.
- [x] Basic error handling: empty topic, missing config, agent/model
      failures, file-write errors, validation failures all produce readable
      messages instead of raw stack traces (where practical).

## Reflection

**Difference between a direct LLM call and an AI agent.** A direct LLM call
sends one prompt and returns one completion; there's no persistent role, no
tool access, and no orchestration. An agent wraps a model with a defined
role (system instruction), a place in a larger workflow, and (potentially)
tools it can call. In this project, "agent" mainly means "a model configured
with a narrow, fixed responsibility and a runner that manages the
conversation session," while the actual deterministic work (file writing,
validation) is delegated to plain Python functions rather than asked of the
model.

**Role of each agent.** The Explainer Agent turns a raw topic into
structured educational content (explanation, concepts, example). The
Practice Designer Agent builds on that content to produce a scoped exercise
without duplicating the explanation. The Reviewer Agent acts as a
quality-control pass over the assembled draft, surfacing mistakes and gaps
without regenerating the guide. Keeping each agent single-purpose made
prompts shorter and outputs more consistent.

**Role of each tool.** `save_markdown_file` guarantees the final guide is
written to disk predictably, regardless of what the model produced.
`validate_required_sections` gives a deterministic, testable signal about
structural completeness, decoupled from subjective judgments about content
quality: the model can be flexible about wording while the tool stays
strict about structure.

**Most difficult part.** Getting a small local model (`llama3.2:1b`) to
reliably reproduce exact Markdown heading text. Early runs occasionally
appended extra words to a heading (e.g. `## Practice Exercise: Enumerate and
Match HTTP Status Codes`) or treated a `#` code comment inside a fenced code
block as a heading, which broke strict validation. This was fixed by (a)
making the validator match on heading prefix rather than exact string, and
(b) making it ignore lines inside triple-backtick code fences, while keeping
the prompts explicit about not adding extra words to heading lines.

**Model limitations observed.** `llama3.2:1b` is fast and usually follows
the requested Markdown structure, but instruction-following is not perfect
at this size: it sometimes embellishes headings, nests sub-headings (`###`)
under a requested `##` heading, or pads sections with more content than
requested. A larger model (e.g. `llama3.2:3b`) would likely follow
formatting instructions more strictly, at the cost of slower generation.

## Known Limitations

- The local model occasionally adds sub-headings (`###`) or extra prose
  beyond what was requested; the validator tolerates heading-text variation
  via prefix matching but does not enforce exact formatting.
- No automatic retry/regeneration if an agent's output is structurally poor
  beyond the missing-section check; the workflow prints a warning and still
  saves the file.
- No tests directory; validation is done via the `validate_required_sections`
  tool and manual runs against multiple topics.
- Single-session, sequential execution only: no parallel agent calls, no
  persistent conversation memory across runs.
