# -*- coding: utf-8 -*-
# OMG-NEXUS by YOGGS - github.com/artcasds
# Tools Spam OTP WhatsApp - 14 platform (CLI & Web Engine)
import os, sys, time, threading
from colorama import Fore, Style, init
from otp_engine import (
    ua, normalize, fmt08, fmtplus, fmtphone, rnd_name, rnd_email,
    get_ip, PLATFORMS, verdict
)

init(autoreset=True)

# paksa stdout UTF-8 biar karakter kotak nggak error di console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

LINE = Fore.LIGHTBLACK_EX   # garis abu-abu
TXT  = Fore.WHITE           # teks putih
ART  = Fore.GREEN + Style.BRIGHT  # ascii art hijau

def run_platforms(p62, only=None):
    """jalanin semua platform, return jumlah sukses"""
    total = len(PLATFORMS)
    success = 0
    for i, (name, fn) in enumerate(PLATFORMS, 1):
        if only and i not in only:
            continue
        try:
            resp = fn(p62)
        except Exception:
            resp = None
        status, detail = verdict(resp)
        prefix = f"[{i:02d}] {name:<16} -> {status} "
        head = prefix + detail
        if len(head) > 69:
            detail = detail[:69 - len(prefix) - 1] + "~"
        if status == "SUCCESS":
            success += 1
            col = Fore.GREEN
        elif status == "LIMIT":
            col = Fore.YELLOW
        else:
            col = Fore.RED
        plain = f"[{i:02d}] {name:<16} -> {status} {detail}"
        if len(plain) > 69:
            plain = plain[:68] + "~"
        row = plain.ljust(69)
        row = row.replace(f" {detail}", f" {LINE}{detail}", 1)
        row = row.replace(status, f"{col}{status}{Style.RESET_ALL}", 1)
        print(f"{LINE}│ {row}{LINE}│{Style.RESET_ALL}")
    return success

# ============================================================
# UI TERMINAL
# ============================================================

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{LINE}╭{'─' * 62}╮{Style.RESET_ALL}")
    print(f"{LINE}│{' ' * 62}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT} ██╗   ██╗ ██████╗ ██████╗ ████████╗███████╗ ██████╗██╗  ██╗  {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT} ██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝╚██╗██╔╝  {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT} ██║   ██║██║   ██║██████╔╝   ██║   █████╗  ██║      ╚███╔╝   {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT} ╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██╔══╝  ██║      ██╔██╗   {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT}  ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ███████╗╚██████╗██╔╝ ██╗  {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{TXT}   ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝  {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│{' ' * 62}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 62}╯{Style.RESET_ALL}")

def info_box():
    ip = get_ip()
    print(f"{LINE}╭{'─' * 30}╮{LINE}╭{'─' * 30}╮{Style.RESET_ALL}")
    print(f"{LINE}│ {TXT}Nama      {ART}:{TXT} NEX-OTP         {TXT} {LINE}│{LINE}│ {TXT}Platform  {ART}:{TXT} 14 WA OTP       {TXT} {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│ {TXT}Status    {ART}:{TXT} FREE            {TXT} {LINE}│{LINE}│ {TXT}IP Publik {ART}:{TXT} {ip:<16}{TXT} {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 30}╯{LINE}╰{'─' * 30}╯{Style.RESET_ALL}")
    print()

def input_phone():
    print(f"{LINE}╭{'─' * 62}╮{Style.RESET_ALL}")
    plain = "Masukkan nomor target (08xx / 62xx / +62xx):".ljust(60)
    plain = plain.replace(":", f"{ART}:{TXT}")
    print(f"{LINE}│ {TXT}{plain} {TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 5}╭{'─' * 56}╯{Style.RESET_ALL}")
    print(f"{LINE}      ╰─➤ {Style.RESET_ALL}", end="")
    try:
        raw = input().strip()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    print()
    p62 = normalize(raw)
    if not p62:
        print(f"{Fore.RED}Format nomor salah, coba 08xxxxxxxxxx{Style.RESET_ALL}")
        return None
    return p62

def spam_single():
    p62 = input_phone()
    if not p62:
        return
    print(f"{LINE}╭{'─' * 70}╮{Style.RESET_ALL}")
    t = f'SPAM 1x KE {fmtplus(p62)} | {len(PLATFORMS)} PLATFORM WA OTP'.ljust(69)
    t = t.replace(fmtplus(p62), f"{Fore.GREEN}{fmtplus(p62)}{Style.RESET_ALL}", 1)
    print(f"{LINE}│ {TXT}{t}{TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 70}╯{Style.RESET_ALL}")
    ok = run_platforms(p62)
    print(f"{LINE}╭{'─' * 70}╮{Style.RESET_ALL}")
    t = f'Hasil : {ok} sukses / {len(PLATFORMS) - ok} gagal'.ljust(69)
    t = t.replace(f'{ok} sukses', f"{Fore.GREEN}{ok} sukses{Style.RESET_ALL}", 1)
    t = t.replace(f'{len(PLATFORMS) - ok} gagal', f"{Fore.RED}{len(PLATFORMS) - ok} gagal{Style.RESET_ALL}", 1)
    print(f"{LINE}│ {TXT}{t}{TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 70}╯{Style.RESET_ALL}")
    try:
        input(f"{TXT}Enter buat lanjut...{Style.RESET_ALL}")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

def spam_loop():
    p62 = input_phone()
    if not p62:
        return
    try:
        delay = int(input(f"{TXT}Delay antar round (detik) [60]: {Style.RESET_ALL}") or 60)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except ValueError:
        delay = 60
    print(f"{LINE}╭{'─' * 70}╮{Style.RESET_ALL}")
    t = f'BRUTE LOOP KE {fmtplus(p62)} | Ctrl+C buat stop'.ljust(69)
    t = t.replace(fmtplus(p62), f"{Fore.GREEN}{fmtplus(p62)}{Style.RESET_ALL}", 1)
    print(f"{LINE}│ {TXT}{t}{TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 70}╯{Style.RESET_ALL}")
    round_no = 0
    total_ok = 0
    try:
        while True:
            round_no += 1
            t = f'Round {round_no} mulai...'.ljust(69)
            t = t.replace(str(round_no), f"{Fore.GREEN}{round_no}{Style.RESET_ALL}", 1)
            print(f"{LINE}│ {TXT}{t}{TXT}{LINE}│{Style.RESET_ALL}")
            ok = run_platforms(p62)
            total_ok += ok
            t = f'Round {round_no} -> sukses {ok}/{len(PLATFORMS)} | total {total_ok}'.ljust(69)
            print(f"{LINE}│ {TXT}{t}{TXT}{LINE}│{Style.RESET_ALL}")
            for s in range(delay, 0, -1):
                print(f"\r{TXT}Jeda {s:>3} detik... (Ctrl+C stop){Style.RESET_ALL}", end="")
                time.sleep(1)
            print()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Dihentikan. Round: {round_no} | total sukses: {total_ok}{Style.RESET_ALL}")
    try:
        input(f"{TXT}Enter buat lanjut...{Style.RESET_ALL}")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

def spam_pick():
    p62 = input_phone()
    if not p62:
        return
    print(f"{LINE}╭{'─' * 19} [ PILIH PLATFORM ] {'─' * 19}╮{Style.RESET_ALL}")
    for i, (name, _) in enumerate(PLATFORMS, 1):
        t = f"[{i:02d}] {name}".ljust(57)
        t = t.replace(f"[{i:02d}]", f"{ART}[{TXT}{i:02d}{ART}]{TXT}", 1)
        print(f"{LINE}│ {t}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 58}╯{Style.RESET_ALL}")
    try:
        sel = input(f"{TXT}Nomor platform (1-{len(PLATFORMS)}): {Style.RESET_ALL}").strip()
        jumlah = int(input(f"{TXT}Jumlah spam: {Style.RESET_ALL}") or 1)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except ValueError:
        jumlah = 1
    try:
        idx = int(sel)
    except ValueError:
        print(f"{Fore.RED}Pilihan nggak ada{Style.RESET_ALL}")
        return
    if idx < 1 or idx > len(PLATFORMS):
        print(f"{Fore.RED}Pilihan nggak ada{Style.RESET_ALL}")
        return
    name, fn = PLATFORMS[idx - 1]
    print(f"{LINE}╭{'─' * 70}╮{Style.RESET_ALL}")
    title = f"SPAM {name} x{jumlah} KE {fmtplus(p62)}"
    print(f"{LINE}│ {TXT}{title:<69}{TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 70}╯{Style.RESET_ALL}")
    ok = 0
    for j in range(1, jumlah + 1):
        try:
            resp = fn(p62)
        except Exception:
            resp = None
        status, detail = verdict(resp)
        if status == "SUCCESS":
            ok += 1
            col = Fore.GREEN
        elif status == "LIMIT":
            col = Fore.YELLOW
        else:
            col = Fore.RED
        plain = f"kirim ke-{j:>3} : {status} {detail}"
        if len(plain) > 69:
            plain = plain[:68] + "~"
        row = plain.ljust(69)
        row = row.replace(f" {detail}", f" {LINE}{detail}", 1)
        row = row.replace(status, f"{col}{status}{Style.RESET_ALL}", 1)
        print(f"{LINE}│ {row}{LINE}│{Style.RESET_ALL}")
        time.sleep(2)
    hasil = f"Hasil : {ok}/{jumlah} sukses".ljust(69)
    hasil = hasil.replace("Hasil :", f"Hasil {ART}:{TXT}", 1)
    print(f"{LINE}│ {TXT}{hasil}{TXT}{LINE}│{Style.RESET_ALL}")
    try:
        input(f"{TXT}Enter buat lanjut...{Style.RESET_ALL}")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

def info_system():
    import platform as pf
    print(f"{LINE}╭{'─' * 20} [ INFO SYSTEM ] {'─' * 21}╮{Style.RESET_ALL}")
    rows = [
        f"Sistem    : {pf.system()} {pf.release()}",
        f"Python    : {pf.python_version()}",
        f"CPU       : {os.cpu_count()} core",
        f"Public IP : {get_ip()}",
    ]
    try:
        import psutil
        mem = psutil.virtual_memory()
        rows.append(f"RAM       : {mem.percent}% ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB)")
    except ImportError:
        pass
    for row in rows:
        print(f"{LINE}│ {TXT}{row:<57}{TXT}{LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 58}╯{Style.RESET_ALL}")
    try:
        input(f"{TXT}Enter buat lanjut...{Style.RESET_ALL}")
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

def menu():
    print(f"{LINE}╭{'─' * 21} {TXT}[ MENU ]{LINE} {'─' * 31}╮{Style.RESET_ALL}")
    print(f"{LINE}│ {ART}[{TXT}01{ART}]{TXT} SPAM OTP 1X (SEMUA PLATFORM){TXT}                            {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│ {ART}[{TXT}02{ART}]{TXT} SPAM OTP BRUTE (LOOP TERUS){TXT}                             {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│ {ART}[{TXT}03{ART}]{TXT} SPAM OTP PILIH PLATFORM{TXT}                                 {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│ {ART}[{TXT}04{ART}]{TXT} INFO SYSTEM{TXT}                                             {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}│ {ART}[{TXT}05{ART}]{TXT} KELUAR{TXT}                                                  {LINE}│{Style.RESET_ALL}")
    print(f"{LINE}╰{'─' * 5}╭{'─' * 56}╯{Style.RESET_ALL}")
    try:
        pilih = input(f"{LINE}      ╰─➤ {Style.RESET_ALL}").strip()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    if pilih.lower() in ("exit", "keluar", "q"):
        sys.exit(0)
    pilih = pilih.zfill(2)
    if pilih == "01":
        spam_single()
    elif pilih == "02":
        spam_loop()
    elif pilih == "03":
        spam_pick()
    elif pilih == "04":
        info_system()
    elif pilih in ("00", "05"):
        sys.exit(0)
    else:
        print(f"{Fore.RED}  pilihan nggak ada, coba lagi.{Style.RESET_ALL}")
        time.sleep(1)

def main():
    while True:
        banner()
        info_box()
        menu()

if __name__ == "__main__":
    main()
