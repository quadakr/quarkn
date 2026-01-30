#!/usr/bin/env python3

import argparse  # args
import re  # to find patterns in user input and set f.ex "4m 1 hour 1 second" as 3841 seconds for time.sleep() function correctly
import readline  # without this when you press f.ex left arrow, it writes "^[[D", but single library somehow fix that
import shutil  # to find a player(s)
import subprocess  # sound playing
import sys  # for sys.exit(1) when there is a error or sys.exit(0) when it's everything ok
import threading  # time countdown thread
import time  # who would have thought, time


def validate_number_words(time_str, FORBIDDEN_NUMBER_WORDS):
    words = re.findall(r"[a-zA-Z]+", time_str.lower())

    for word in words:
        if word in FORBIDDEN_NUMBER_WORDS:
            print("Error: Numbers greater than ten must be written using digits.")
            print("Hint: '12 minutes', not 'twelve minutes'.")
            sys.exit(1)


def normalize_numbers(text, WORD_NUMBERS):  # one -> 1, Nine -> 9 e.t.c.
    for word, digit in WORD_NUMBERS.items():
        text = re.sub(
            rf"\b{word}\b",
            digit,
            text,
            flags=re.IGNORECASE,
        )
    return text


def progress_bar_print(reached, toreach, length):
    filled = int((reached / toreach) * length)
    unfilled = length - filled
    bar = "[" + "=" * filled + "-" * unfilled + "]"
    print(bar, end="", flush=True)


def timeprint(wait_time_float):  # accurate time count
    end_time = time.monotonic() + wait_time_float
    next_tick = time.monotonic()
    while True:
        breaknow = False
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            breaknow = True

        sys.stdout.write("\033[2K\r")  # erasing line
        print(
            str(int(remaining)) + "/" + str(int(wait_time_float)) + "s ",
            end="",
            flush=True,
        )
        progress_bar_print(wait_time_float - remaining, wait_time_float, 40)

        if breaknow:
            break

        next_tick += 1

        sleep_time = next_tick - time.monotonic()
        if sleep_time > 0:
            time.sleep(sleep_time)


def notify(count_of_notifications, text):  # using notify-send command
    while count_of_notifications > 0:
        subprocess.run(
            ["notify-send", text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(0.1)
        count_of_notifications = count_of_notifications - 1


def play_sound(sound_path):  # using external player
    if shutil.which("mpv"):
        subprocess.Popen(
            ["mpv", "--no-video", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return

    if shutil.which("ffplay"):
        subprocess.Popen(
            ["ffplay", "-nodisp", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    if shutil.which("vlc"):
        subprocess.Popen(
            ["vlc", "--intf", "dummy", "--play-and-exit", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )


def parse_time_to_seconds(time_str, TIME_PATTERN, UNIT_TO_SECONDS):
    time_str = str(time_str).replace(",", ".")
    matches = TIME_PATTERN.findall(time_str)

    total_seconds = 0.0

    if matches:
        for value, unit in matches:
            total_seconds += float(value) * UNIT_TO_SECONDS[unit.lower()]
    else:
        total_seconds = float(time_str)

    return total_seconds


def main():
    wait_time_str = 0
    cmd = ""
    notification_text = "You have a scheduled notification from quarkn."
    print_time = False
    send_notification = True
    spam = False
    sound_path = ""
    repeat = False
    version = "v0.2.0"

    parser = argparse.ArgumentParser(
        description=(
            "Quarkn - simple unix cli notification sender. "
            "It can be used as a reminder, task scheduler, "
            "timer, or command executor. "
        )
    )

    parser.add_argument(
        "-m",
        "--text",
        help=(
            "Notification text. "
            "If omitted, the default message "
            "'You have a scheduled notification from quarkn.' "
            "will be used."
        ),
    )

    parser.add_argument(
        "-t",
        "--wait-time",
        required=False,
        help="Delay before notification (ex: '10mins 5 seconds' or '1 minute 3 hours'). In seconds if only the number given. ",
    )

    parser.add_argument(
        "-c",
        "--cmd",
        help="Command to execute when notify. ",
    )

    parser.add_argument(
        "-r",
        "--no-remaining-time-countdown",
        action="store_true",
        help="Don't output remaining time every second. ",
    )

    parser.add_argument(
        "-n",
        "--no-text",
        action="store_true",
        help="Disable notification text output. ",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run interactive mode. Displays input lines one by one to fill instead of using arguments, easier than fully read --help, can be used with any other arguments. ",
    )

    parser.add_argument(
        "-s",
        "--sound",
        required=False,
        help=(
            "Play a sound when the notification is sent. "
            "Note #1: only mpv, ffplay, vlc are supported. "
            "Note #2: it plays even without a notification. "
        ),
    )

    parser.add_argument(
        "--spam",
        action="store_true",
        help=("Send 50 notifications instead of 1. "),
    )

    parser.add_argument(
        "--repeat",
        action="store_true",
        help=(
            "Repeat countdown again after notification. (Infinite until stopped manually) "
        ),
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help=("Show program version and exit."),
    )

    args = parser.parse_args()

    if not any(vars(args).values()):  # checks if any agrument got any value
        print(
            "Missing arguments. Run 'quarkn -h' to get instructions or 'quarkn -i' for interactive mode. "
        )
        sys.exit(1)

    if args.version:
        print("quarkn: " + version)
        sys.exit(0)

    if (
        not args.wait_time and not args.interactive
    ):  # not args.interactive because time may be set in interactive mode
        print("Wait time is an essential preference. ")
        sys.exit(1)

    wait_time_str = args.wait_time

    if args.text:
        notification_text = args.text

    if args.cmd:
        cmd = args.cmd

    if args.no_text:
        send_notification = False

    print_time = not args.no_remaining_time_countdown

    spam = args.spam

    repeat = args.repeat

    sound_path = args.sound

    try:
        if args.interactive:
            print("Write every preference one by one. ")

            if (
                not args.wait_time
            ):  # arguments is a primary source, anything interactive can be skipped
                wait_time_str = input(
                    "Time to wait (essential, write 'ex' for examples): "
                )

                if wait_time_str == "ex":
                    print("ex: '10mins 5 seconds' or '1 day 2 hours'")
                    wait_time_str = ""

                if wait_time_str == "":
                    while wait_time_str == "" or wait_time_str == "ex":
                        print("It's essential setting.")
                        wait_time_str = input("Time to wait: ")
                        if wait_time_str == "ex":
                            print("ex: '10mins 5 seconds' or '1 minute 3 hours'")

            if not args.cmd:
                cmd = input("Cmd to execute (not essential): ")

            if not args.no_text:
                notification_assinger = input(
                    "Should the program send you a notification?[y/n]: "
                )
                if notification_assinger == "y":
                    send_notification = True
                else:
                    send_notification = False

                if not args.text:
                    notification_text = input(
                        "Custom notification text (not essential): "
                    )
                    if notification_text == "":  # reset to default if skipped
                        notification_text = (
                            "You have a scheduled notification from quarkn."
                        )

            if not args.spam:
                spam_assinger = input(
                    "Should the program spam notifications? (it will send 50 instead of 1)[y/n]: "
                )
                if spam_assinger == "y":
                    spam = True
                else:
                    spam = False

            if not args.repeat:
                repeat_assinger = input(
                    "Should the program repeat countdown and notification (and/or sound) until stopped manually?[y/n]: "
                )
                if repeat_assinger == "y":
                    repeat = True
                else:
                    repeat = False

            if not args.sound:
                sound_assinger = input(
                    "Should the program play sound after countdown? (not a part on notifications)[y/n]: "
                )
                if sound_assinger == "y":
                    sound_path = input("Sound path: ")
                    sound_path = sound_path.strip().strip('"').strip("'")

        TIME_PATTERN = re.compile(
            r"(\d+(?:[.,]\d+)?)\s*"  # In some countries it's common to write "," in fractional number but doesn't work in python
            r"(d|day|days|h|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)",
            re.IGNORECASE,  # uppercase = lowercase
        )

        UNIT_TO_SECONDS = {
            "d": 86400,
            "day": 86400,
            "days": 86400,
            "h": 3600,
            "hrs": 3600,
            "hour": 3600,
            "hours": 3600,
            "m": 60,
            "min": 60,
            "mins": 60,
            "minute": 60,
            "minutes": 60,
            "s": 1,
            "sec": 1,
            "secs": 1,
            "second": 1,
            "seconds": 1,
        }

        FORBIDDEN_NUMBER_WORDS = {  # it's hard to support numbers like "fiftyfivebillionshundredninetyeightmillionseleven" so the parsing is limited
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "sixty",
            "seventy",
            "eighty",
            "ninety",
            "hundred",
            "thousand",
            "million",
            "billion",
        }

        WORD_NUMBERS = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
        }

        validate_number_words(wait_time_str, FORBIDDEN_NUMBER_WORDS)

        wait_time_str = normalize_numbers(
            wait_time_str, WORD_NUMBERS
        )  # changing words like "two" to valid numbers like "2"

        wait_time_float = float(
            parse_time_to_seconds(wait_time_str, TIME_PATTERN, UNIT_TO_SECONDS)
        )

        print("", end="\n")
        while True:
            if print_time:
                timeprint_thread = threading.Thread(
                    target=timeprint, args=(wait_time_float,), daemon=True
                )

                timeprint_thread.start()

            time.sleep(
                wait_time_float
            )  # sleeping time that user set up earlier and after sending notify, executing cmd e.t.c.

            if cmd:
                subprocess.Popen(cmd, shell=True, start_new_session=True)

            if sound_path != "" and sound_path:
                play_sound(sound_path)

            if send_notification:
                if spam:
                    notify(50, notification_text)
                else:
                    notify(1, notification_text)

            if not repeat:
                print("", end="\n\n")
                sys.exit(0)

            sys.stdout.write("\033[2K\r")  # erasing line

    except KeyboardInterrupt:
        print("\n\nExited quarkn.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()



