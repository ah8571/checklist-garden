  [ USER BROWSER UI ] (Brings their own OpenRouter Key)
           │
           ▼
  [ CLOUDFLARE PAGES ] (Your main web dashboard frontend — 100% serverless)
           │
     ┌─────┴────────────────────────┐
     ▼                              ▼
[ SUPABASE DATABASE ]      [ FLY.IO MICRO-VM ] (Launches instantly)
(Saves checklist states)            │
                                    ├──► Reads your user's repository files
                                    ├──► Communicates via OpenRouter/DeepSeek
                                    └──► Runs build commands & updates states


Building the web UI for your own app, checklist.garden, using your current autonomous setup is the perfect way to test it. Letting an agent work on it inside a persistent Linux tmux session will give you a first-hand look at exactly how to build the application's underlying architecture.
To build a web UI where a user can paste a long checklist, close their browser, and return later to find the tasks completed, you are shifting from a local tool to a cloud-hosted platform.
You do not need to build or manage complex, raw Linux tmux clusters in the cloud. Instead, modern cloud engineering relies on isolated, serverless runtime environments to handle autonomous tasks safely and scalably.
------------------------------
## The Architecture of checklist.garden (Web UI Version)
To build this platform, your app requires four core engineering layers:
## 1. The Frontend (The Interface)
This is the simple dashboard you mentioned where a user interacts with the app.

* How it works: Built using a fast framework like Next.js or Remix. The user logs in, creates a project garden, and pastes their raw markdown text checklist.
* The Action: When they click "Start Agent," the frontend sends that checklist data to your database and closes out the user session. The browser tab can now be safely closed.

## 2. The Database & State Engine (The Status Ledger)
Because the user can close their browser, your app must save the status of every single task line in a central database.

* The Technology: A real-time database like Supabase (PostgreSQL).
* How it works: Your frontend splits the user's checklist into individual database rows (e.g., Task 1: Pending, Task 2: Pending). The background AI worker reads these rows one-by-one, updates their status to In Progress, and flips them to Completed when done. When the user logs back into the website, the UI queries the database and instantly displays the updated checklist garden.

3.2 Webhook State Updates
As the background sandbox agent crosses tasks off the checklist.md, it must send a quick HTTP POST request (a webhook) back to your Next.js server: Task 1 = Done. Your database updates, and your frontend uses WebSockets to instantly turn that checkbox green on the user's browser screen without them needing to refresh.

Secure Key Vaulting

Your database must securely store the user’s OpenRouter or Cerebras API keys. You must use AES-256 row-level encryption (which Supabase provides natively) so that no one—including you or a hacker—can read the users' raw keys in plain text.

## 3. The Backend Worker: Serverless Sandboxes (The "Cloud Tmux" Alternative)
In a local environment, you use tmux to keep your terminal running in the background. In a cloud architecture, having thousands of users running scripts on your main server would quickly crash it or expose you to massive security risks (like an AI agent accidentally deleting your main server files).

* The Technology: E2B Sandboxes or Fly.io Machines.
* How it works: The moment a user clicks "Start," your backend triggers a webhook that spins up an isolated, lightweight secure micro-container (a sandbox). Think of this as a temporary, blank Linux machine created just for that specific checklist.
* OpenCode's agent architecture (or an open framework like LangGraph) is loaded into that sandbox along with the user's codebase, their checklist data, and your OpenRouter/DeepSeek API connection. It runs entirely in the background, independent of your web server.

## 4. The Budget Guardrail (The Financial Valve)
Because this is a public web app, you must protect your own API key from being drained by your users.

* How it works: When a user initializes a run, you assign a Token Credit Budget to their specific sandbox container. You program your background loop to calculate token consumption in real time. If the sandbox encounters a complex bug and spends more than $1.00 of compute, the backend automatically issues a kill command to that specific sandbox, updates the web UI to read Halted: Budget Limit Reached, and saves the exact state for the user's review.

Kill-Switch

You must build a security daemon (a background timer script). If a user's agent gets stuck in an infinite debugging loop, your platform must automatically force-close and destroy that cloud container after 30 minutes to protect your own server bills from inflating.

## 





------------------------------
## How to Have Your Current Agent Build This Right Now
Before deploying this to the cloud, you can have your current terminal agent build the baseline mockup inside a local Linux tmux session:

   1. Create your local checklist.garden project folder.
   2. In your ROADMAP.md, write out the first small, chunked milestones:
   * "Step 1: Build a simple Next.js page with a large text-area input box and a submit button."
      * "Step 2: Set up a local Supabase schema with a tasks table containing columns for id, text, and status."
   3. Launch your agent inside tmux using your DeepSeek connection:
   
   opencode "Read ROADMAP.md and build Step 1. Run the local build script to verify there are no syntax errors, then stop."
   
   4. Detach from your terminal window and focus on your other active projects.

By enforcing strict, single-task completion limits on your agent, it can cleanly lay the brick-and-mortar foundations of your web application step-by-step.
As you prepare to map out the data structures for your project, let me know if you want to look at a sample database schema structure for tracking tasks, or if you need help setting up your first local Linux sandbox environment!

*written by: google.com/ai*