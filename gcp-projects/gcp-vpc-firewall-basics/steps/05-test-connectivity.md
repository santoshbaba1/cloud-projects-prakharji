# Step 5 — Test Connectivity

Time to prove your network works. You'll SSH into the VMs, ping between them on their **internal**
IPs, serve a web page from `vm-a`, and — most importantly — *watch the firewall block* traffic you
didn't allow. This is where all four previous steps pay off.

---

## 5.1 SSH Into `vm-a`

### Console

On the **VM instances** page, click the **SSH** button next to `vm-a`. A browser terminal opens —
this uses your `demo-allow-ssh` rule.

### gcloud CLI (Alternative)

```bash
gcloud compute ssh vm-a --zone=us-east1-b
```

The first time, gcloud generates an SSH key for you. If it hangs, your `demo-allow-ssh` rule
probably doesn't match your **current** public IP (see [troubleshooting.md](../troubleshooting.md)).

---

## 5.2 Ping `vm-b` on Its Internal IP

From **inside the `vm-a` SSH session**, ping `vm-b`'s **internal** IP (from `gcloud compute instances
list`, e.g. `10.10.2.2`):

```bash
ping -c 4 10.10.2.2
```

You should see replies:

```
64 bytes from 10.10.2.2: icmp_seq=1 ttl=64 time=0.7 ms
...
```

✅ **This works because of `demo-allow-internal`** (which allowed `icmp` from `10.10.0.0/16`). Note
that `vm-a` and `vm-b` are on **different subnets** — the ping crosses subnets privately, proving a
GCP VPC routes between its subnets automatically.

---

## 5.3 Serve a Web Page From `vm-a`

Still inside `vm-a`, start the tiny Python web server. It uses only the standard library, so there's
nothing to install.

Create the file (copy [`src/hello_server.py`](../src/hello_server.py) — paste it in with `nano
hello_server.py`), then run it:

```bash
sudo python3 hello_server.py
```

You'll see `Serving on port 80 — press Ctrl+C to stop`. Leave it running.

> **Why `sudo`?** Ports below 1024 (like 80) are privileged on Linux.

---

## 5.4 Reach the Web Page — Two Ways

### From your laptop (external IP → tests `demo-allow-http`)

Open a browser to `http://<vm-a-EXTERNAL-IP>` (from `gcloud compute instances list`). You'll see:

```
Hello from vm-a (10.10.1.2)
```

✅ **This works because `vm-a` is tagged `web` and `demo-allow-http` opens port 80 to that tag.**

### From `vm-b` (internal IP → tests private routing)

Open a **second** terminal, SSH into `vm-b`, and curl `vm-a`'s **internal** IP:

```bash
gcloud compute ssh vm-b --zone=us-east1-b
# then, inside vm-b:
curl http://10.10.1.2
```

You'll get the same `Hello from vm-a` line — delivered entirely over the private `10.10.0.0/16`
network, never touching the internet.

---

## 5.5 See the Firewall *Block* Traffic (The Best Part)

Firewalls are easiest to understand when you watch one deny something. Two quick experiments:

**Experiment A — an un-opened port is refused.** On `vm-a`, stop the web server (Ctrl+C) and restart
it on port **8080** instead (edit `PORT = 8080` in the file). From your laptop, browse to
`http://<vm-a-EXTERNAL-IP>:8080`. It **hangs / times out** — because no firewall rule allows port
8080. Your `demo-allow-http` rule only opened **80**.

**Experiment B — the tag is what matters.** `vm-b` is *not* tagged `web`. Even if you ran a web
server on it, `http://<vm-b-EXTERNAL-IP>` would be blocked, because `demo-allow-http` targets only
the `web` tag. Change nothing on `vm-a`; just internalize that **the tag, not the VM, opened the
port.**

> **Takeaway:** In GCP, reachability = *a matching allow rule* × *the right target (tag)* × *the
> right port*. Miss any one and the traffic is silently dropped by the implied deny.

---

## 5.6 Clean Up the Server Process

Press **Ctrl+C** in the `vm-a` terminal to stop the Python server, then `exit` both SSH sessions.
(The VMs themselves are deleted in the next step.)

---

## Checkpoint

- [ ] SSH into `vm-a` worked (via your `demo-allow-ssh` rule)
- [ ] `ping 10.10.2.2` from `vm-a` got replies (via `demo-allow-internal`, across subnets)
- [ ] The browser showed `Hello from vm-a` on the **external** IP (via `demo-allow-http` + tag `web`)
- [ ] `curl` from `vm-b` to `vm-a`'s **internal** IP returned the same page (private routing)
- [ ] Port `8080` timed out — you saw the implied deny in action

---

**Next:** [Step 6 — Cleanup](./06-cleanup.md)
