#!/usr/bin/env python3
import time
import sys
import os
import subprocess
import signal
from datetime import datetime

# ANSI colors
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
GRAY    = "\033[90m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

WORK_MINUTES   = 25
SHORT_BREAK    = 5
LONG_BREAK     = 15
LONG_BREAK_EVERY = 4  # long break after every 4 pomodoros

running = True

def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def notify(title, message):
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message}" with title "{title}" sound name "Glass"'],
            capture_output=True
        )
    except Exception:
        pass

def progress_bar(elapsed, total, width=40, color=GREEN):
    filled = int(width * elapsed / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * elapsed / total)
    return f"{color}{bar}{RESET} {BOLD}{pct:3d}%{RESET}"

def format_time(seconds):
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"

def print_header(session_num, total_sessions, phase):
    os.system("clear")
    print(f"\n  {BOLD}{CYAN}🍅 ポモドーロタイマー{RESET}")
    print(f"  {GRAY}{'─' * 50}{RESET}")

    tomatoes = "🍅" * total_sessions + "○" * max(0, LONG_BREAK_EVERY - total_sessions % LONG_BREAK_EVERY if total_sessions % LONG_BREAK_EVERY != 0 else LONG_BREAK_EVERY)
    print(f"  {tomatoes}")

    if phase == "work":
        label = f"{RED}{BOLD}  作業中 — セッション #{session_num}{RESET}"
    elif phase == "short_break":
        label = f"{GREEN}{BOLD}  休憩中 (短){RESET}"
    else:
        label = f"{BLUE}{BOLD}  休憩中 (長){RESET}"

    print(f"\n{label}\n")

def countdown(duration_secs, phase, session_num, total_sessions):
    color = RED if phase == "work" else (GREEN if phase == "short_break" else BLUE)
    hide_cursor()
    start = time.time()
    try:
        while True:
            elapsed = time.time() - start
            remaining = duration_secs - elapsed
            if remaining <= 0:
                break

            bar = progress_bar(elapsed, duration_secs, width=42, color=color)
            time_str = format_time(int(remaining) + 1)

            print_header(session_num, total_sessions, phase)
            print(f"  {bar}")
            print(f"\n  {BOLD}{color}残り  {time_str}{RESET}")
            print(f"\n  {GRAY}Ctrl+C で中断{RESET}")

            time.sleep(0.5)
    finally:
        show_cursor()

def run_session(session_num, total_sessions):
    # Work phase
    print_header(session_num, total_sessions, "work")
    notify("🍅 ポモドーロ開始", f"セッション #{session_num} — 25分、集中！")
    countdown(WORK_MINUTES * 60, "work", session_num, total_sessions)
    notify("✅ 作業完了！", "よくできました。少し休みましょう。")

    # Decide break length
    if session_num % LONG_BREAK_EVERY == 0:
        phase = "long_break"
        duration = LONG_BREAK * 60
        break_label = f"長い休憩 ({LONG_BREAK}分)"
    else:
        phase = "short_break"
        duration = SHORT_BREAK * 60
        break_label = f"短い休憩 ({SHORT_BREAK}分)"

    print_header(session_num, total_sessions, phase)
    notify(f"☕ {break_label}", "リラックスしてください。")
    countdown(duration, phase, session_num, total_sessions)
    notify("🍅 次のセッションの準備ができました", "始める準備はいいですか？")

def wait_for_start(prompt):
    os.system("clear")
    print(f"\n  {BOLD}{CYAN}🍅 ポモドーロタイマー{RESET}")
    print(f"  {GRAY}{'─' * 50}{RESET}")
    print(f"\n  {prompt}")
    print(f"\n  {GRAY}Enter で開始 / Ctrl+C で終了{RESET}\n  ", end="")
    sys.stdout.flush()
    try:
        input()
        return True
    except (KeyboardInterrupt, EOFError):
        return False

def main():
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

    session_num = 1
    total_sessions = 0

    os.system("clear")
    print(f"\n  {BOLD}{CYAN}🍅 ポモドーロタイマーへようこそ{RESET}")
    print(f"  {GRAY}{'─' * 50}{RESET}")
    print(f"\n  {YELLOW}作業: {WORK_MINUTES}分  短い休憩: {SHORT_BREAK}分  長い休憩: {LONG_BREAK}分{RESET}")
    print(f"  {GRAY}{LONG_BREAK_EVERY}セッションごとに長い休憩があります{RESET}\n")
    print(f"  {GRAY}Enter で最初のセッションを開始{RESET}\n  ", end="")
    sys.stdout.flush()

    try:
        input()
    except (KeyboardInterrupt, EOFError):
        show_cursor()
        print(f"\n\n  {GRAY}またね！{RESET}\n")
        return

    while True:
        try:
            run_session(session_num, total_sessions)
            total_sessions += 1
            session_num += 1

            ok = wait_for_start(
                f"{GREEN}{BOLD}セッション #{session_num - 1} 完了！ 🎉{RESET}\n\n"
                f"  {YELLOW}合計: {total_sessions} ポモドーロ完了{RESET}\n\n"
                f"  次のセッションを始めますか？"
            )
            if not ok:
                break
        except (KeyboardInterrupt, SystemExit):
            break

    show_cursor()
    os.system("clear")
    print(f"\n  {BOLD}{CYAN}🍅 お疲れ様でした！{RESET}")
    print(f"  {YELLOW}今日のポモドーロ: {total_sessions} セッション ({total_sessions * WORK_MINUTES} 分){RESET}\n")

if __name__ == "__main__":
    main()
