# Deploying ResearchConclave on AWS EC2

Free-tier friendly deployment: a `t3.micro` Ubuntu 24.04 instance running the
Streamlit app as a `systemd` service.

> ⚠️ Requires **Ubuntu 24.04 LTS** — its Python is 3.12. Ubuntu 22.04 ships
> Python 3.10, but this project needs **≥ 3.11**.

---

## 0. Prerequisite — push the code

The server pulls from GitHub, so the repo must be pushed — **including this
`deploy/` folder** — and must **not** contain `.env` (it's gitignored, so secrets
stay local).

```bash
git add deploy && git commit -m "Add EC2 deploy files" && git push
```

## 1. Launch the instance (EC2 → Launch instance)

| Setting | Value |
|---------|-------|
| AMI | Ubuntu Server **24.04 LTS** |
| Instance type | `t3.micro` (free-tier eligible) |
| Key pair | Create new (**ED25519**), download the `.pem` |
| Storage | **gp3**, **16 GiB** |
| File systems | **None** |
| Advanced details | defaults |
| **Security group** | `SSH (22)` from **My IP**; `Custom TCP 8501` from **Anywhere** (inbound). Outbound: default allow-all. |

## 2. SSH in

```bash
chmod 400 ~/.ssh/researchconclave-key.pem
ssh -i ~/.ssh/researchconclave-key.pem ubuntu@<ec2-public-ip>
```

## 3. One-command setup

```bash
git clone https://github.com/ankit8405/multi-agent-resource-system.git
cd multi-agent-resource-system
bash deploy/setup-ec2.sh
```

This installs packages, adds a 2 GiB swap file, creates the venv, installs
requirements, and starts the `researchconclave` systemd service.

## 4. Add secrets, then restart

```bash
printf 'OPENAI_API_KEY=sk-...\nTAVILY_API_KEY=tvly-...\n' > .env
chmod 600 .env
sudo systemctl restart researchconclave
```

## 5. Open the app

```
http://<ec2-public-ip>:8501
```

(Recommended) Allocate and associate an **Elastic IP** so the address stops
changing across stop/start.

---

## Optional — Nginx + HTTPS (clean URL, no `:8501`)

```bash
sudo apt-get install -y nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/researchconclave
sudo ln -sf /etc/nginx/sites-available/researchconclave /etc/nginx/sites-enabled/researchconclave
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```
Then open port 80/443 in the security group and (with a domain pointed at the
instance):
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Day-2 operations

| Task | Command |
|------|---------|
| Live logs | `journalctl -u researchconclave -f` |
| Restart | `sudo systemctl restart researchconclave` |
| Deploy an update | `cd ~/multi-agent-resource-system && git pull && sudo systemctl restart researchconclave` |
| Health check | `curl http://localhost:8501/_stcore/health` → `ok` |

## Troubleshooting

| Symptom | Cause |
|---------|-------|
| Connection times out | Port 8501 not open in security group, or app not bound to `0.0.0.0` |
| `OPENAI_API_KEY not found` | `.env` missing, or wrong `WorkingDirectory` |
| App dies on logout | Ran `streamlit` by hand instead of the systemd service |
| Random kills / OOM | 1 GiB RAM exhausted — confirm swap is on (`free -h`) |
| Live UI frozen behind proxy | Nginx missing websocket upgrade headers |

## Cost note

`t3.micro` is free for **12 months**; afterwards ~$8–10/month (billed 24/7
regardless of traffic). An unattached Elastic IP incurs a small charge.
