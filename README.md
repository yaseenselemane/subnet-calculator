# Subnet calculator

A small IPv4 subnet calculator for the terminal (and a simple window, with `--gui`). Give it an address with a prefix or a mask, and it shows everything you need for planning a network or checking an exam answer.

Part of my networking labs: [ping and traceroute](https://github.com/yaseenselemane/ping-and-traceroute) · [nmap](https://github.com/yaseenselemane/nmap-field-notes) · [WiFi survey](https://github.com/yaseenselemane/wifi-survey) · [Packet Tracer](https://github.com/yaseenselemane/cisco-packet-tracer-labs) · **subnet calculator** · [vantage](https://github.com/yaseenselemane/vantage)

## Run it

Python 3.8+, nothing to install.

```bash
python subnet_calculator.py          # terminal
python subnet_calculator.py --gui    # window (tkinter)
```

It accepts either form:

```
192.168.1.130/26
10.0.0.1 255.255.255.252
```

## Example

```
> Enter IP: 172.16.5.4/20

  Input IP         172.16.5.4
  CIDR Notation    172.16.0.0/20
  Prefix Length    /20

  ── ADDRESSES ──────────────────────────────────
  Network Address  172.16.0.0
  Broadcast Addr   172.16.15.255
  First Host       172.16.0.1
  Last Host        172.16.15.254

  ── MASK ────────────────────────────────────────
  Subnet Mask      255.255.240.0
  Wildcard Mask    0.0.15.255
  Binary Mask      11111111.11111111.11110000.00000000

  ── DETAILS ─────────────────────────────────────
  Usable Hosts     4,094
  Total IPs        4,096
  Network Class    Class B
  Private Range    Yes
```

## Tests

```bash
python -m unittest test_subnet_calculator.py
```

They cover a normal /26, mask-style input, the /31 and /32 edge cases, a /8 (which must be instant), and bad input.

## Bugs I found and fixed

| Bug | Cause | Fix |
|---|---|---|
| A `/8` took **21 seconds** (the window froze) | It built a list of all 16.7 million hosts just to read the first and last one | Work them out directly: network + 1 and broadcast − 1 |
| `/31` and `/32` said **0 usable hosts** | It always subtracted 2 for network and broadcast | A /31 is a point-to-point link where both addresses are usable (RFC 3021), and a /32 is one host |
| It **crashed** when the output was piped, or on older Windows consoles | The box-drawing banner can't be encoded in the old Windows code page | Switch the output to UTF-8 at start-up |

## What I learned

1. **A subnet is just bit maths.** The prefix says how many bits are the network. Everything else (mask, wildcard, broadcast, host count) follows from it. The binary mask line makes that visible.
2. **The wildcard mask is the inverse of the subnet mask.** It's what Cisco ACLs and OSPF use (`0.0.15.255` for a /20).
3. **Usable hosts = 2^(host bits) − 2**, except for /31 and /32. The edge cases are where the bugs were.
4. **"Correct" isn't enough. It also has to be fast.** The first version gave the right answer for a /8 and froze anyway. Testing the biggest input, not just typical ones, caught it.
5. **Classful labels (A, B, C) are history.** Real networks use CIDR, but exams and older docs still mention classes, so the tool shows both.
