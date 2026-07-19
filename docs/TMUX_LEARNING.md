# Beginner Guide to Terminal Autonomy

To run an autonomous agent that codes safely while you step away, you only need to master three phases: opening the hidden room (tmux), calling your worker (OpenCode), and walking out the door.

---

## Phase 1: Opening the Permanent Room (tmux)

Imagine a standard terminal window is a chalkboard—if you close the door or wipe it down, everything vanishes. `tmux` creates a magical whiteboard inside a secret backroom that never shuts down.

### Step 1.1: Launch a Named Session
Open your main terminal window on your machine and type this command to open your first hidden workspace:
```bash
tmux new -s garden-worker
```
*Visual Cue:* Your terminal screen will reset. You will see a solid green status bar appear at the very bottom edge of your window. You are now officially sitting inside your permanent room.

---

## Phase 2: Calling the Worker & Setting the Limits

Now that you are inside the room, you need to navigate to your coding project and wake up your OpenCode agent.

### Step 2.1: Go to Your Project Folder
Type the standard change-directory command to drop your terminal into your codebase folder:
```bash
cd c:\Code\feedless
```

### Step 2.2: Wake up OpenCode
Type the universal launch word to wake up your terminal agent:
```bash
opencode
```
*Visual Cue:* The screen will change, displaying the OpenCode logo and opening an interactive prompt line. You are now speaking directly to the AI agent.

### Step 2.3: Lock the Free Model Route
Before giving it a massive task, type the shortcut utility command to force it to use OpenRouter's zero-cost free model pool so you don't accidentally burn real money while learning:
```text
/models openrouter/free
```

---

## Phase 3: Giving the Order & Leaving the Room

This is the exact "Jarred Sumner" phase. You give the agent a strict, self-verifying task and walk away.

### Step 3.1: Paste the Autonomous Prompt Instruction
Type or paste this exact command structure into your active OpenCode line. This tells the agent exactly how to work without asking for your permission:
```text
"Look at my project files. Create a brand new file called 'TEST_PAGE.md'. Inside that file, write out a clean documentation overview of what this project does. Once you create the file, run a directory listing command to verify it exists, and then halt execution immediately. Do not ask for human approval."
```

### Step 3.2: Leaving the Room (The Detach Trick)
The exact millisecond you hit enter and the agent starts outputting text, you can safely exit the room and let it run completely unsupervised:
* Press and hold the **`Ctrl`** key, then press **`B`**.
* Release both keys.
* Immediately press **`D`** on your keyboard (D stands for **Detach**).

*Visual Cue:* The green status bar will vanish. You will instantly pop right back out to your normal computer terminal prompt screen. 

---

## Phase 4: Checking the Results in the Morning

You can now completely close VS Code, shut off your monitor, or open a different window to work on your other LLC project folders. OpenCode is still running silently inside your operating system's background cache.

When you want to see if the agent successfully completed its checklist assignment, open your terminal and type the re-attach command:
```bash
tmux a -t garden-worker
```

Your screen will instantly snap right back inside the permanent room, displaying the exact terminal outputs, file creation records, and logs the agent generated while you were away!


# Security Settings

A VM (Virtual Machine) is a complete, software-based simulation of an entire physical computer. It runs inside an isolated bubble on your actual machine, with its own virtual hard drive, virtual operating system, and virtual memory.
Think of a VM as a digital quarantine zone. Even if an AI agent gains absolute system root access inside a VM and executes a destructive command like rm -rf / (delete everything), it can only destroy the virtual bubble. Your real computer, actual files, and main operating system remain completely untouched [7].
------------------------------
## The Absolute Worst-Case Scenario (and how to prevent it)
If you run an autonomous agent directly on your main computer's terminal (without a VM or sandbox) and it encounters an infinite debugging loop or a severe hallucination, the absolute worst-case scenario is that it executes a bad shell script that wipes your local code folders, corrupts configuration registries, or exposes your .env private API keys.
Because you are keeping your project directories completely synchronized and pushed up to GitHub, you are already highly protected. If the agent mangles a file layout or deletes a folder locally, you can instantly restore your entire project to its perfect, pre-agent state with a single recovery command:

git reset --hard HEAD

------------------------------
## The 3 Levels of Agent Security (From Beginner to Pro)
As your checklist.garden project grows, you can gradually move your autonomous worker loops through three distinct levels of security isolation:
## Level 1: The Git Guardrail (Your Current Local Setup)

* The Setup: You run tmux and opencode directly on your machine's standard terminal, but you ensure every single local change is committed and pushed to GitHub first.
* The Security: Low, but completely recoverable. If the agent breaks your local file configurations, you wipe its changes using git reset.

## Level 2: Local Docker Containerization (Highly Recommended for Linux Transition)
When you transition your environment over to Linux, you should instantly adopt Docker. Docker allows you to spin up a specialized micro-VM (called a container) on your local hard drive in under a second.

* The Setup: You launch your opencode session inside an isolated Linux Docker container. You only link a single, cloned copy of your project folder to that specific container.
* The Security: High. The agent cannot see your computer's main desktop files, your browser history, or your system credentials. It can only see the specific project folder you handed it.

## Level 3: Serverless Cloud Sandboxes (Your Final checklist.garden SaaS Product Architecture)
This is the infrastructure layout we mapped out for your web app using providers like E2B or Fly.io.

* The Setup: The agent runs inside a secure, single-use, hardened micro-virtual machine hosted completely in the cloud.
* The Security: Absolute. The agent operates entirely in a remote cloud quarantine zone. It has zero physical path connection to your computer or your primary production databases, allowing your customers to run their checklists with total peace of mind.

------------------------------
## 🛡️ Your Copy-Paste Safety Rule Checklist
Before you hit enter on any autonomous background command, save this strict layout validation rule to protect your workflow:

# Autonomous Agent Pre-Flight Checklist
1. [ ] GIT CHECK: Run `git status`. Ensure all current local changes are committed and pushed to your remote GitHub repository.
2. [ ] RECOVERY SNAPSHOT: Verify that running `git reset --hard` is safe to execute if a code recovery is required.
3. [ ] BUDGET SHIELD: Double-check your OpenRouter/DeepSeek dashboard. Verify that Auto-Topup is toggled OFF and a strict dollar ceiling is applied to the key.
4. [ ] PROMPT CONSTRAINT: Ensure your text instructions explicitly end with a hard limit string (e.g., "Attempt the task once, run your test, write the log file, and then HALT immediately. Do not loop autonomously.")

By combining a hard spending cap with a strict single-task halt command, you can safely watch your autonomous agent experiment in its background room without any risk to your hardware!
When you are ready to start writing your project's technical specifications, let me know if you want to look at the exact Docker commands to launch a local agent sandbox on your upcoming Linux setup!

