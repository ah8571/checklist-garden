# Long-Range AI Agent Architecture (OpenCode + DeepSeek + tmux)

This document outlines the background multiplexer setup used by world-class systems engineers to let AI agents safely and autonomously code all night.

[Jarred Sumner] (the creator of Bun) had an AI agent code all night on massive engineering tasks—was achieved by running Anthropic's official Claude Code CLI engine inside a persistent Unix utility multiplexer called tmux or screen. 
[Jarred Sumner] didn't use a standard graphical interface or a basic VS Code terminal tab. Instead, he combined automated agent loops with decoupled server processes, allowing the terminal instance to run indefinitely in the background even after he closed his laptop and went to bed.

---

## Step 1: The Core Infrastructure (The Background Multiplexer)

Running an agent directly in a standard VS Code terminal panel will crash the process if the editor closes or the computer enters sleep mode. You must decouple the execution engine using `tmux`.

Use a Persistent Multiplexer: Run your background project scripts inside tmux (on Mac/Linux) or Windows Terminal Named Sessions.
   2. How it handles long runs: Multiplexers create a detached pseudo-terminal server in your computer's operating system cache. When you start an agent loop, you can safely disconnect (Ctrl+B then D in tmux) or completely exit VS Code. The agent will continue executing file edits and testing code silently in the background all night.

### 1.1 Why tmux works
* It spawns a persistent, detached pseudo-terminal server directly inside your operating system's cache.
* The agent process runs continuously in the background even if you close VS Code or disconnect from the machine.

### 1.2 Basic Linux tmux Commands
* Create a new named session: `tmux new -s checklist-garden`
* Detach from the session (leaving it running all night): Press `Ctrl + B` then release and tap `D`
* List active background sessions: `tmux ls`
* Re-attach to your session later: `tmux a -t checklist-garden`

---

## Step 2: The Agent Setup (OpenCode + OpenRouter/DeepSeek)

OpenCode functions as a terminal-native, tool-use-driven framework. Unlike standard chat boxes, it seamlessly captures multi-file directory context, handles bash executions, and natively reads git diffs.

### 2.1 The Budget Shield Guardrail
Before running a long-range loop, enforce a hard spending cap directly on the specific OpenRouter API key inside your web dashboard (e.g., a \$3.00 maximum lifetime cap). If the agent gets stuck in a logic loop while you sleep, OpenRouter will sever the connection, safely preserving the code state for your morning review.

---

## Step 3: The Secret Sauce (The Instruction Ledger Files)

An unsupervised agent will quickly go off the rails without clear constraints. You must structure its guardrails using three specific markdown files placed directly into your project's root directory.

### 3.1 `CLAUDE.md` (or `AGENT.md`)
This serves as your project's constitution. It forces the model to adhere to your strict engineering patterns and coding rules.
```markdown
# Project Rules & Formatting Specs

- Language stack: TypeScript, Next.js (App Router), TailwindCSS.
- Database: Supabase/PostgreSQL schema.
- Code style: Use functional components, explicit type exports, and absolute imports (@/*).
- Tool boundaries: Run `npm run build` or `npm test` after editing any file.
- Error mitigation: If a terminal error occurs, you are forbidden from guessing fixes. Look at the exact line in the error trace, print the file content, and refactor carefully.
```

### 3.2 `ROADMAP.md`
This serves as the deterministic checklist. You must chunk tasks into small, isolated, step-by-step milestones.
```markdown
# checklist.garden Implementation Roadmap

- [ ] Task 1: Create a basic Next.js page UI with a markdown text-area input and a 'Start Garden' button.
- [ ] Task 2: Design the Supabase database migrations for the `tasks` and `projects` tables.
- [ ] Task 3: Build an API endpoint route to accept the text checklist and chunk it into individual database rows.
- [ ] Task 4: Connect the local test runners to verify model parsing accuracy.
```

### 3.3 `PROGRESS.md`
Leave this file entirely blank. The agent will use this as its internal ledger to report its state back to you.

---

## Step 4: Executing the Autonomous Loop

Open your terminal, launch your tmux environment, navigate to your root project path, and invoke OpenCode with a strict, recursive chunk-constrained instruction prompt.

### 4.1 The Long-Range Execution Prompt
```text
opencode "Read ROADMAP.md and CLAUDE.md. You are strictly forbidden from attempting more than ONE task at a time. Begin executing Task 1. Once completed, run the project's build command (`npm run build`).

IF the build fails: Fix the bug and re-test. You have a maximum limit of 3 debugging attempts before you must halt execution completely.
IF the build succeeds: Document every file modified and error solved inside PROGRESS.md, mark Task 1 as [x] DONE in ROADMAP.md, and halt. Do not proceed to Task 2 without human review."
```

### 4.2 Detaching from the Loop
Once OpenCode prints its confirmation and begins analyzing the codebase layout, press `Ctrl + B` then `D` to safely detach. 

You can now completely close VS Code, switch to your other LLC project workflows, or log off for the night. The agent will execute, build, test, and safely freeze itself the exact moment it finishes its target chunk.


## Interview / advice from Bun Founder

Here is an interview of the bun founder to isolate more key points like with testing:
https://blog.pragmaticengineer.com/the-pulse-what-can-we-learn-from-buns-rapid-rust-rewrite-with-ai/?utm_source=tldrnewsletter
Here's the porting md: https://github.com/oven-sh/bun/commit/46d3bc29f270fa881dd5730ef1549e88407701a5?ref=blog.pragmaticengineer.com
https://bun.com/blog/bun-in-rust

## Original response from google.com/aimode


------------------------------
## Step 1: The Core Infrastructure (The Background Multiplexer)
If you run an AI agent inside a standard VS Code terminal panel and close your editor or your computer goes to sleep, the process instantly crashes.


------------------------------
## Step 2: The Agent Setup (Claude Code or OpenCode)
To replicate the exact workflow, you need a terminal-native agent that can execute shell commands, look at git diffs, and self-correct when its tests fail. [1, 2] 

* The Claude Code Route: You can globally initialize Anthropic's developer CLI tool:

npm install -g @anthropic-ai/claude-code

* The OpenCode Route (Your Setup): Since you already have OpenCode operational inside your terminal layouts, you can use it exactly the same way! OpenCode shares the identical architecture that allowed Jarred's setup to thrive: a clean command line capable of reading files, editing lines, and checking progress asynchronously. [1, 2] 

------------------------------
## Step 3: The Secret Sauce: The "Instruction Ledger" Files
An agent left to code entirely on its own all night will usually go off the rails or loop endlessly on a single bug. To make an agent succeed over a long range, you must use Instruction Ledgering. [3] 
Before you launch the agent and walk away, create three markdown structural files directly inside your project's root folder: [3] 

   1. CLAUDE.md (or AGENT.md): This acts as the project’s hardcoded constitution. It explicitly tells the agent your coding styling preferences, what file formatting frameworks to use, and how it should behave. [3] 
   2. ROADMAP.md: Paste a highly detailed, step-by-step checklist of the feature you want built. (e.g., "Step 1: Create the user table schema. Step 2: Write the Next.js API endpoint. Step 3: Run the local test suite."). [2, 3] 
   3. PROGRESS.md: Leave this file blank. Tell the agent in your initial prompt: "You must record every file change, terminal error, and completed task into PROGRESS.md after every single loop so I can audit your work in the morning." [3] 

------------------------------
## Executing Your First Long-Range Loop
Once your markdown guides are written, navigate into your detached tmux or project background shell session and launch the agent using a specific recursive multi-step instruction prompt:

opencode "Read ROADMAP.md, CLAUDE.md, and then begin executing Step 1 autonomously. If a step compiles successfully, run the automated test suite. If the test passes, proceed immediately to Step 2. Update PROGRESS.md continuously. Do not stop for user approval unless you encounter a system roadblock you cannot resolve."

Once the agent prints its confirmation and begins analyzing your codebase, safely detach from that background tab panel. You can now open a completely separate VS Code window to work on your other LLC project folders while the terminal agent spends the next several hours running background tests, editing files, and crossing items off your checklist in the background.
If you are ready to configure this automated loop layout, let me know:

* Are you running this on a Mac terminal or a Windows machine (so I can give you the exact tmux/background detachment shortcut syntax)?
* Do you have an automated test suite (like Jest, Vitest, or PyTest) set up in your project to let the agent auto-verify its code?


[1] [https://www.loopnews.io](https://www.loopnews.io/academy/claude-code-beginners)
[2] [https://www.xda-developers.com](https://www.xda-developers.com/claude-code-settings-i-change-before-letting-it-touch-a-project/)
[3] [https://aiblewmymind.substack.com](https://aiblewmymind.substack.com/p/claude-code-content-distribution-ai-agent)

*written by: google.com/ai*