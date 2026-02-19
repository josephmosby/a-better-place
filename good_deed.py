#!/usr/bin/env python3
"""
good_deed.py — suggest one concrete thing you can do right now.

Usage:
    python good_deed.py          # asks how much time you have
    python good_deed.py --log    # show what you've done this week
"""

import argparse
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

LOG_FILE = Path.home() / ".good_deeds.json"

DEEDS = {
    "30s": [
        "Text someone you haven't spoken to in a while — just to say you thought of them.",
        "Leave a genuine compliment on someone's work (a post, a project, a newsletter).",
        "Write a specific 'thank you' to someone who helped you, even months ago.",
        "Check if you're registered as an organ donor. If not, take 2 minutes to sign up.",
        "Smile and make eye contact with the next stranger you pass.",
        "Look up. Literally. The sky, clouds, stars. Awe reduces stress and increases generosity.",
        "Put your phone away for the next conversation you have. Full attention is a radical act of kindness.",
        "Say 'I might be wrong about this' before your next strong opinion — and mean it.",
    ],
    "5m": [
        "Write a kind, honest review for a small business that deserves it.",
        "Forward an article or resource that genuinely changed how you think about something.",
        "Call your elected representative about something you care about. Calls are counted.",
        "Set up a small recurring donation to a cause you believe in.",
        "Reply to someone's creative work with something more thoughtful than a like.",
        "Write down three specific things you're grateful for. Studies show this boosts happiness after just 10 weeks.",
        "Check on someone who's been quiet lately. The people who stop reaching out often need connection most.",
        "Thank a coworker for something specific they did. Only 10% of people express gratitude at work on any given day.",
    ],
    "1h": [
        "Offer to review someone's resume, portfolio, or code — and actually do it well.",
        "Give blood. One donation can save up to three lives.",
        "Cook extra food and bring it to a neighbor, shelter, or food bank.",
        "Mentor someone earlier in their career. One honest conversation changes trajectories.",
        "Participate in a local park or neighborhood cleanup.",
        "Take an 'awe walk' — go somewhere with trees, old buildings, or open sky and pay attention to what's bigger than you.",
        "Write a gratitude letter to someone who changed your life. Be specific about what they did and how it affected you.",
        "Invite someone to eat with you. Shared meals are one of the oldest forms of human bonding.",
    ],
    "ongoing": [
        "Learn basic first aid and CPR — most emergencies happen around people who could help.",
        "Plant something: a tree, a pollinator garden, or a window box of flowers.",
        "Join a local mutual aid network. Show up consistently.",
        "Reduce food waste: plan meals, use scraps, compost what's left.",
        "Be a reliable presence for someone in your life who is struggling.",
        "Practice steelmanning: before arguing against something, articulate the strongest version of the opposing view.",
        "Keep a weekly gratitude journal. The research is clear — it compounds.",
        "Practice active listening: repeat back what people say, ask follow-ups, resist the urge to pivot to your own story.",
    ],
}

BUCKETS = {
    "1": "30s",
    "2": "5m",
    "3": "1h",
    "4": "ongoing",
}

BUCKET_LABELS = {
    "30s": "30 seconds",
    "5m": "5 minutes",
    "1h": "about an hour",
    "ongoing": "an ongoing commitment",
}


def pick_deed(bucket: str) -> str:
    return random.choice(DEEDS[bucket])


def ask_time() -> str:
    print("\nHow much time do you have?\n")
    print("  1. 30 seconds")
    print("  2. 5 minutes")
    print("  3. About an hour")
    print("  4. I want something ongoing\n")

    while True:
        choice = input("Choose (1–4): ").strip()
        if choice in BUCKETS:
            return BUCKETS[choice]
        print("Please enter 1, 2, 3, or 4.")


def log_deed(deed: str, bucket: str) -> None:
    log = load_log()
    entry = {
        "date": str(date.today()),
        "bucket": bucket,
        "deed": deed,
        "done": False,
    }
    log.append(entry)
    LOG_FILE.write_text(json.dumps(log, indent=2))


def load_log() -> list:
    if not LOG_FILE.exists():
        return []
    try:
        return json.loads(LOG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def mark_done(index: int) -> None:
    log = load_log()
    if 0 <= index < len(log):
        log[index]["done"] = True
        LOG_FILE.write_text(json.dumps(log, indent=2))
        print("Marked as done.")
    else:
        print("Invalid entry number.")


def show_log(days: int = 7) -> None:
    log = load_log()
    cutoff = date.today() - timedelta(days=days)
    recent = [e for e in log if date.fromisoformat(e["date"]) >= cutoff]

    if not recent:
        print(f"\nNo deeds logged in the last {days} days.\n")
        return

    done = sum(1 for e in recent if e.get("done"))
    print(f"\nLast {days} days: {len(recent)} suggested, {done} marked done.\n")
    for i, entry in enumerate(recent):
        status = "✓" if entry.get("done") else "·"
        print(f"  {status} [{entry['date']}] ({BUCKET_LABELS[entry['bucket']]})")
        print(f"    {entry['deed']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest one good thing you can do right now.")
    parser.add_argument("--log", action="store_true", help="Show your logged deeds this week")
    parser.add_argument("--done", type=int, metavar="N", help="Mark log entry N as done")
    args = parser.parse_args()

    if args.log:
        show_log()
        return

    if args.done is not None:
        mark_done(args.done)
        return

    bucket = ask_time()
    deed = pick_deed(bucket)

    print(f"\nThis takes {BUCKET_LABELS[bucket]}:\n")
    print(f"  {deed}\n")

    answer = input("Log this so you can come back to it? (y/n): ").strip().lower()
    if answer == "y":
        log_deed(deed, bucket)
        print("Logged. Run `python good_deed.py --log` to see your history.\n")
    else:
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)
