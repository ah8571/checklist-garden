## What Terraform is (plain terms)

Normally you create a server by clicking around the DigitalOcean website: choose Ubuntu, pick a size, add your SSH key, click Create. Terraform does the same thing, but you describe what you want in text files, and it talks to DigitalOcean's API to make it real.
The three ideas that matter:

1. Declarative config — your infra/terraform/main.tf says "I want one droplet, in region nyc1, size s-2vcpu-2gb, running Ubuntu 24.04, with SSH key X, ports 22/80/443 open." You don't script how to click; you describe what should exist.

2. State file — after it creates things, Terraform saves a snapshot (.tfstate) of everything it made. That's how terraform destroy knows exactly what to delete, and how it knows nothing changed when you re-run.

3. Plan → Apply — terraform plan shows you a preview ("I will create 1 droplet, 1 firewall, ...") without touching anything. terraform apply actually does it. This is the "safe preview" superpower that clicking a website doesn't have.


## Step-by-step walkthrough

*v2*
1. ✅ Terraform installed (done)
2. Create an API token in the DO website (the only console step) — NOT the droplet
3. Paste the token into PowerShell ($env:DIGITALOCEAN_TOKEN="...")
4. terraform plan — preview
5. terraform apply — this is what boots your Ubuntu droplet automatically
6. SSH in, fill .env, point Cloudflare at the IP

*v1*
1. Install Terraform
Open PowerShell and run one of:
winget install HashiCorp.Terraform
# or
choco install terraform
Verify: terraform version should print a version. (I can run the install for you if you'd like — just say so.)

2. Create a DigitalOcean API token
- Go to https://cloud.digitalocean.com/account/api/tokens
- Click Generate New Token
- Give it a name like terraform, set scopes to Read + Write, copy it.
- Treat it like a password — anyone with it can create/delete servers on your account.
Then set it in your current PowerShell session (this only lasts for that window — fine for now):
$env:DIGITALOCEAN_TOKEN="your_token_here"

3. Decide which SSH key
Terraform registers a public key on the droplet so you can log in. You have id_ed25519.pub and red-eye-agent.pub. On Windows, Terraform doesn't expand ~ in file paths, so pass the full path explicitly:
$env:USERPROFILE\.ssh\id_ed25519.pub     # absolute path form
I'd suggest reusing red-eye-agent if that's the key the old droplet used (its private key will be what you SSH with), but either works.

4. Run Terraform
cd C:\Code\checklistgarden\infra\terraform

terraform init      # downloads the DigitalOcean "provider" plugin (one-time)

terraform plan `
  -var ssh_public_key="C:\Users\bmaff\.ssh\id_ed25519.pub" `
  -var domain="checklist.garden"
plan will print a preview like "Plan: 3 to add" and show the exact droplet/firewall/key it will create. Read it. If it looks right:
terraform apply `
  -var ssh_public_key="C:\Users\bmaff\.ssh\id_ed25519.pub" `
  -var domain="checklist.garden"
Type yes when prompted. After ~1–2 minutes it prints the droplet IP (also in outputs.tf). A fresh Ubuntu box is now running your cloud-init.yaml.
Note: -var domain="..." also creates the DNS A record on DigitalOcean. If your domain is registered elsewhere (Cloudflare, Namecheap), instead leave domain empty and add the A record manually in that registrar's DNS pointing at the droplet IP.

5. After the droplet exists
- Put secrets on it once: ssh root@<ip>, then copy /opt/checklist-garden/.env.example → /opt/checklist-garden/.env and fill in DEEPSEEK_API_KEY, GITHUB_PAT, WEB_SECRET_KEY, ALLOWED_EMAILS. (These are the keys you currently have in the local .env file.)
- Add GitHub Actions secrets so the deploy workflow can reach it (see the table in infra/README.md).
- Push to main → the workflow installs deps, builds the opencode image, and starts the service.

6. When you're done / want to start over
cd C:\Code\checklistgarden\infra\terraform
terraform destroy -var domain="checklist.garden"
That deletes the droplet, firewall, and key — no orphaned bills, no clicking through the website. This is exactly why people love Terraform: the whole box is a text file you can recreate or throw away.
A few beginner tips / warnings
- Never commit the token — it goes in the env var or a git-ignored file, not in main.tf.
- terraform destroy is real — it deletes the droplet. That's what you'd want after testing.
- State file — terraform.tfstate will appear in infra/terraform/. Keep it; it's how Terraform tracks the droplet. (Don't commit it if you ever share the repo — though for solo dev it's fine locally.)
- Terraform is free; you only pay DigitalOcean for the droplet (~$18/mo for s-2vcpu-2gb).

# Domain Cloudflare (not DO)
[ ] you'll add an A record manually later
What you run now (in PowerShell, from C:\Code\checklistgarden\infra\terraform)

1. Set the token for this session (from https://cloud.digitalocean.com/account/api/tokens → Generate, read+write):
$env:DIGITALOCEAN_TOKEN="dop_v1_xxxxxxxx"

2. Preview (reads your token, shows everything it will create — free, no changes):
terraform plan -var ssh_public_key="C:\Users\bmaff\.ssh\red-eye-agent.pub"

3. Create the droplet (type yes when asked):
terraform apply -var ssh_public_key="C:\Users\bmaff\.ssh\red-eye-agent.pub". It'll take ~1–2 min, then prints droplet_ip. On first boot the box runs cloud-init.yaml (installs Docker, Caddy, Python, creates /opt/checklist-garden/...).

4. Then, once (manual):
ssh -i C:\Users\bmaff\.ssh\red-eye-agent root@<droplet_ip>
cp /opt/checklist-garden/.env.example /opt/checklist-garden/.env
nano /opt/checklist-garden/.env   # paste your real API keys

5. And point Cloudflare at it — A record for your domain → <droplet_ip> (that's what enables the Caddy HTTPS).
Two beginner warnings before you run apply: it bills you (~$18/mo for the 2GB droplet), and terraform destroy is how you'd remove it later (delete the box, stop paying).
Want to stop here and run those steps, or should I stick around to help with the next stage (filling .env, GitHub Actions secrets, first deploy) once the droplet is up?