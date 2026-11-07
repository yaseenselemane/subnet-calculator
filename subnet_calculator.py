#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║         SUBNET CALCULATOR v1.0               ║
║         Built by Yaseen Selemani             ║
║         github.com/yaseenselemane            ║
╚══════════════════════════════════════════════╝

Usage:
  CLI mode:  python subnet_calculator.py
  GUI mode:  python subnet_calculator.py --gui
"""

import ipaddress
import sys
import argparse


# ─────────────────────────────────────────────
#  CORE CALCULATION ENGINE
# ─────────────────────────────────────────────

def get_network_class(ip_str):
    """Determine the class of an IPv4 address."""
    first_octet = int(ip_str.split('.')[0])
    if 1 <= first_octet <= 126:
        return 'A'
    elif 128 <= first_octet <= 191:
        return 'B'
    elif 192 <= first_octet <= 223:
        return 'C'
    elif 224 <= first_octet <= 239:
        return 'D (Multicast)'
    elif 240 <= first_octet <= 255:
        return 'E (Reserved)'
    elif first_octet == 127:
        return 'Loopback (127.x.x.x)'
    return 'Unknown'


def is_private(ip_obj):
    """Check if IP is private."""
    return ip_obj.is_private


def calculate_subnet(ip_input):
    """
    Main calculation function.
    Accepts: '192.168.1.1/24' or '192.168.1.1 255.255.255.0'
    Returns: dict of all subnet info
    """
    ip_input = ip_input.strip()

    # Handle subnet mask format: '192.168.1.1 255.255.255.0'
    if ' ' in ip_input and '/' not in ip_input:
        parts = ip_input.split()
        if len(parts) == 2:
            try:
                mask_bits = ipaddress.IPv4Network(f'0.0.0.0/{parts[1]}').prefixlen
                ip_input = f'{parts[0]}/{mask_bits}'
            except ValueError:
                raise ValueError(f"Invalid subnet mask: {parts[1]}")

    try:
        # Parse the network (strict=False allows host bits to be set)
        interface = ipaddress.IPv4Interface(ip_input)
        network   = interface.network
        ip        = interface.ip

        prefix    = network.prefixlen
        netmask   = network.netmask
        wildcard  = network.hostmask
        network_addr = network.network_address
        broadcast    = network.broadcast_address
        net_class    = get_network_class(str(ip))
        private      = is_private(ip)

        # First and last usable host, worked out directly: listing every host
        # took ~20 s for a /8. A /31 (point-to-point, RFC 3021) and a /32 have
        # no network/broadcast address to reserve, so every address is usable.
        if prefix >= 31:
            num_hosts  = network.num_addresses
            first_host = str(network_addr)
            last_host  = str(broadcast)
        else:
            num_hosts  = network.num_addresses - 2
            first_host = str(network_addr + 1)
            last_host  = str(broadcast - 1)

        # Binary representation of subnet mask
        mask_binary = '.'.join(
            f'{int(o):08b}' for o in str(netmask).split('.')
        )

        return {
            'input_ip'      : str(ip),
            'cidr'          : f'{network_addr}/{prefix}',
            'prefix'        : f'/{prefix}',
            'network_addr'  : str(network_addr),
            'broadcast'     : str(broadcast),
            'subnet_mask'   : str(netmask),
            'wildcard_mask' : str(wildcard),
            'first_host'    : first_host,
            'last_host'     : last_host,
            'usable_hosts'  : f'{num_hosts:,}',
            'total_ips'     : f'{network.num_addresses:,}',
            'net_class'     : net_class,
            'private'       : 'Yes' if private else 'No',
            'mask_binary'   : mask_binary,
        }

    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")


# ─────────────────────────────────────────────
#  CLI MODE
# ─────────────────────────────────────────────

def print_banner():
    print("""
\033[92m╔══════════════════════════════════════════════════╗
║        S U B N E T   C A L C U L A T O R        ║
║              by Yaseen Selemani                  ║
╚══════════════════════════════════════════════════╝\033[0m
  Enter IP in CIDR format:   192.168.1.1/24
  Or with subnet mask:       192.168.1.1 255.255.255.0
  Type 'exit' to quit | Type 'help' for examples
""")


def print_result(data):
    GREEN  = '\033[92m'
    CYAN   = '\033[96m'
    WHITE  = '\033[97m'
    DIM    = '\033[90m'
    RESET  = '\033[0m'

    print(f"""
{GREEN}┌─────────────────────────────────────────────────┐
│               SUBNET INFORMATION                │
└─────────────────────────────────────────────────┘{RESET}
  {DIM}Input IP       {RESET}  {WHITE}{data['input_ip']}{RESET}
  {DIM}CIDR Notation  {RESET}  {CYAN}{data['cidr']}{RESET}
  {DIM}Prefix Length  {RESET}  {WHITE}{data['prefix']}{RESET}

{GREEN}  ── ADDRESSES ──────────────────────────────────{RESET}
  {DIM}Network Address{RESET}  {WHITE}{data['network_addr']}{RESET}
  {DIM}Broadcast Addr {RESET}  {WHITE}{data['broadcast']}{RESET}
  {DIM}First Host     {RESET}  {GREEN}{data['first_host']}{RESET}
  {DIM}Last Host      {RESET}  {GREEN}{data['last_host']}{RESET}

{GREEN}  ── MASK ────────────────────────────────────────{RESET}
  {DIM}Subnet Mask    {RESET}  {WHITE}{data['subnet_mask']}{RESET}
  {DIM}Wildcard Mask  {RESET}  {WHITE}{data['wildcard_mask']}{RESET}
  {DIM}Binary Mask    {RESET}  {CYAN}{data['mask_binary']}{RESET}

{GREEN}  ── DETAILS ─────────────────────────────────────{RESET}
  {DIM}Usable Hosts   {RESET}  {WHITE}{data['usable_hosts']}{RESET}
  {DIM}Total IPs      {RESET}  {WHITE}{data['total_ips']}{RESET}
  {DIM}Network Class  {RESET}  {WHITE}Class {data['net_class']}{RESET}
  {DIM}Private Range  {RESET}  {WHITE}{data['private']}{RESET}
""")


def print_help():
    print("""
\033[96mExamples:\033[0m
  192.168.1.0/24          → Class C private network
  10.0.0.1/8              → Class A private network
  172.16.0.1/12           → Class B private network
  192.168.1.1 255.255.255.0  → Using subnet mask instead of CIDR
  10.10.10.10/30          → Small point-to-point link (2 hosts)
""")


def run_cli():
    print_banner()
    while True:
        try:
            user_input = input('\033[92m>\033[0m Enter IP: ').strip()

            if not user_input:
                continue
            if user_input.lower() == 'exit':
                print('\033[90mGoodbye.\033[0m')
                break
            if user_input.lower() == 'help':
                print_help()
                continue

            result = calculate_subnet(user_input)
            print_result(result)

        except ValueError as e:
            print(f'\033[91m[ERROR] {e}\033[0m\n')
        except KeyboardInterrupt:
            print('\n\033[90mGoodbye.\033[0m')
            break


# ─────────────────────────────────────────────
#  GUI MODE (Tkinter)
# ─────────────────────────────────────────────

def run_gui():
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except ImportError:
        print("[ERROR] tkinter is not available. Run in CLI mode.")
        sys.exit(1)

    # ── Colours ──
    BG       = '#0d1117'
    SURFACE  = '#161b22'
    BORDER   = '#00ff9f'
    GREEN    = '#00ff9f'
    CYAN     = '#00e5ff'
    TEXT     = '#c9d1d9'
    DIM      = '#6e7681'
    WHITE    = '#ffffff'
    RED      = '#ff3860'
    INPUT_BG = '#0a0e13'

    root = tk.Tk()
    root.title('Subnet Calculator — Yaseen Selemani')
    root.configure(bg=BG)
    root.resizable(False, False)

    # ── Window size & centre ──
    W, H = 700, 700
    root.geometry(f'{W}x{H}')
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f'{W}x{H}+{(sw-W)//2}+{(sh-H)//2}')

    mono   = ('Courier New', 10)
    mono_b = ('Courier New', 10, 'bold')
    title_f= ('Courier New', 16, 'bold')
    sub_f  = ('Courier New', 9)

    # ── Header ──
    header = tk.Frame(root, bg=BG)
    header.pack(fill='x', padx=24, pady=(24, 0))

    tk.Label(header, text='SUBNET CALCULATOR',
             font=title_f, fg=GREEN, bg=BG).pack()
    tk.Label(header, text='by Yaseen Selemani  ·  github.com/yaseenselemane',
             font=sub_f, fg=DIM, bg=BG).pack()

    # Separator
    sep = tk.Frame(root, bg=BORDER, height=1)
    sep.pack(fill='x', padx=24, pady=12)

    # ── Input area ──
    input_frame = tk.Frame(root, bg=SURFACE, pady=16, padx=16,
                           highlightbackground=BORDER, highlightthickness=1)
    input_frame.pack(fill='x', padx=24, pady=(0, 12))

    tk.Label(input_frame, text='> Enter IP Address (CIDR or with mask):',
             font=mono, fg=GREEN, bg=SURFACE, anchor='w').pack(fill='x')

    entry_var = tk.StringVar()
    entry = tk.Entry(input_frame, textvariable=entry_var,
                     font=('Courier New', 13), fg=WHITE, bg=INPUT_BG,
                     insertbackground=GREEN, relief='flat',
                     highlightbackground=BORDER, highlightthickness=1)
    entry.pack(fill='x', pady=(8, 4), ipady=8)

    tk.Label(input_frame,
             text='e.g.  192.168.1.1/24   or   10.0.0.1 255.0.0.0',
             font=sub_f, fg=DIM, bg=SURFACE).pack(anchor='w')

    # ── Status label ──
    status_var = tk.StringVar(value='')
    status_lbl = tk.Label(root, textvariable=status_var,
                          font=mono, fg=RED, bg=BG)
    status_lbl.pack(pady=(0, 4))

    # ── Results frame ──
    results_frame = tk.Frame(root, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
    results_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

    results_inner = tk.Frame(results_frame, bg=SURFACE)
    results_inner.pack(fill='both', expand=True, padx=16, pady=16)

    # Result rows stored as dict of StringVars
    fields = [
        ('── ADDRESSES ──', None),
        ('Network Address', 'network_addr'),
        ('Broadcast Addr' , 'broadcast'),
        ('First Host'     , 'first_host'),
        ('Last Host'      , 'last_host'),
        ('── MASK ──'     , None),
        ('Subnet Mask'    , 'subnet_mask'),
        ('Wildcard Mask'  , 'wildcard_mask'),
        ('Prefix Length'  , 'prefix'),
        ('Binary Mask'    , 'mask_binary'),
        ('── DETAILS ──'  , None),
        ('CIDR Notation'  , 'cidr'),
        ('Usable Hosts'   , 'usable_hosts'),
        ('Total IPs'      , 'total_ips'),
        ('Network Class'  , 'net_class'),
        ('Private Range'  , 'private'),
    ]

    row_vars = {}
    for i, (label, key) in enumerate(fields):
        if key is None:
            # Section header
            tk.Label(results_inner, text=label,
                     font=('Courier New', 9, 'bold'),
                     fg=GREEN, bg=SURFACE, anchor='w').grid(
                row=i, column=0, columnspan=2,
                sticky='w', pady=(8, 2))
        else:
            tk.Label(results_inner, text=f'  {label}',
                     font=mono, fg=DIM, bg=SURFACE,
                     width=18, anchor='w').grid(
                row=i, column=0, sticky='w', pady=1)

            var = tk.StringVar(value='—')
            row_vars[key] = var
            tk.Label(results_inner, textvariable=var,
                     font=mono_b, fg=CYAN, bg=SURFACE,
                     anchor='w').grid(
                row=i, column=1, sticky='w', padx=(8, 0))

    results_inner.columnconfigure(1, weight=1)

    # ── Calculate function ──
    def calculate(event=None):
        ip_str = entry_var.get().strip()
        if not ip_str:
            status_var.set('[ERROR] Please enter an IP address.')
            return
        try:
            data = calculate_subnet(ip_str)
            status_var.set('')
            for key, var in row_vars.items():
                var.set(data.get(key, '—'))
                # Colour first/last host green, broadcast red
                # (handled via fixed colours above)
        except ValueError as e:
            status_var.set(f'[ERROR] {e}')
            for var in row_vars.values():
                var.set('—')

    # ── Button ──
    btn_frame = tk.Frame(root, bg=BG)
    btn_frame.pack(pady=(0, 8))

    calc_btn = tk.Button(btn_frame, text='[ CALCULATE ]',
                         font=('Courier New', 11, 'bold'),
                         fg=BG, bg=GREEN, activebackground='#00cc7a',
                         activeforeground=BG, relief='flat',
                         padx=24, pady=8, cursor='hand2',
                         command=calculate)
    calc_btn.pack(side='left', padx=6)

    clear_btn = tk.Button(btn_frame, text='[ CLEAR ]',
                          font=('Courier New', 11, 'bold'),
                          fg=GREEN, bg=SURFACE, activebackground=SURFACE,
                          activeforeground=WHITE, relief='flat',
                          highlightbackground=BORDER, highlightthickness=1,
                          padx=24, pady=8, cursor='hand2',
                          command=lambda: [entry_var.set(''),
                                           status_var.set(''),
                                           [v.set('—') for v in row_vars.values()]])
    clear_btn.pack(side='left', padx=6)

    # Bind Enter key
    entry.bind('<Return>', calculate)
    entry.focus()

    # ── Footer ──
    tk.Label(root, text='Press ENTER or click CALCULATE  ·  Supports CIDR & subnet mask input',
             font=sub_f, fg=DIM, bg=BG).pack(pady=(0, 12))

    root.mainloop()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == '__main__':
    # The box-drawing banner crashed on non-UTF-8 output (piped, older Windows consoles).
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description='Subnet Calculator by Yaseen Selemani')
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        run_cli()
