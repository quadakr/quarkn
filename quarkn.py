import argparse
import subprocess
import time
import threading
import sys
import shutil


def timeprint(wait_time_float):  # time countdown
    while wait_time_float > 0:
        print(wait_time_float)
        time.sleep(1)
        wait_time_float -= 1


def notify(count_of_notifications, text, debug):  # using notify-send command
    while count_of_notifications > 0:
        subprocess.run(
            ["notify-send", text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if debug:
            print("Debug: Notification sent.")

        time.sleep(0.1)
        count_of_notifications = count_of_notifications - 1


def play_sound(sound_path, debug):  # using external player
    if shutil.which("mpv"):
        subprocess.Popen(
            ["mpv", "--no-video", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return

    else:
        if debug:
            print("Debug: mpv player not found, trying ffplay")

    if shutil.which("ffplay"):
        subprocess.Popen(
            ["ffplay", "-nodisp", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    else:
        if debug:
            print("Debug: ffplay player not found, trying vlc")

    if shutil.which("vlc"):
        subprocess.Popen(
            ["vlc", "--intf", "dummy", "--play-and-exit", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    else:
        if debug:
            print("Debug: no supported players found, failed to play a sound.")


def main():
    wait_time_str = 0
    cmd = ""
    notification_text = "You have a scheduled notification from quarkn."
    print_time = False
    send_notification = True
    spam = False
    sound_path = ""
    debug = False

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
        help="Delay before notification (e.g. '10s', '5mins', not '1hour 10mins' but '1.3 hours' is supported). In seconds if only the number given. ",
    )

    parser.add_argument(
        "-c",
        "--cmd",
        help="Command to execute when notify. ",
    )

    parser.add_argument(
        "-r",
        "--remaining-time-countdown",
        action="store_true",
        help="Output remaining time every second. ",
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
        "--debug",
        action="store_true",
        help=("Enable debug output to the console. "),
    )

    args = parser.parse_args()

    if not any(vars(args).values()):  # checks if any agrument got any value
        print(
            "Missing arguments. Run 'quarkn -h' to get instructions or 'quarkn -i' for interactive mode. "
        )
        sys.exit(1)

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

    print_time = args.remaining_time_countdown

    spam = args.spam

    sound_path = args.sound

    debug = args.debug

    if args.interactive:
        print("Write every preference one by one. ")

        if (
            not args.wait_time
        ):  # arguments is a primary source, anything interactive can be skipped
            wait_time_str = input("Time to wait (essential, write 'ex' for examples): ")

            if wait_time_str == "ex":
                print("'1h' works, '1h 30m' not, but '1.5h' is a working example.")

            if wait_time_str == "":
                while wait_time_str == "" or wait_time_str == "ex":
                    print("It's essential setting.")
                    wait_time_str = input("Time to wait: ")
                    if wait_time_str == "ex":
                        print(
                            "'1h' works, '1h 30m' not, but '1.5h' or '90m' is a working examples."
                        )

        if not args.text:
            notification_text = input("Notification text (not essential): ")

        if not args.cmd:
            cmd = input("Cmd to execute (not essential): ")

        if not args.remaining_time_countdown:
            print_time_assinger = input(
                "Should the program output time countdown?[y/n]: "
            )
            if print_time_assinger == "y":
                print_time = True
            else:
                print_time = False

        if not args.no_text:
            notification_assinger = input(
                "Should the program send you a notification?[y/n]: "
            )
            if notification_assinger == "y":
                send_notification = True
            else:
                send_notification = False

        if not args.spam:
            spam_assinger = input(
                "Should the program spam notifications? (it will send 50 instead of 1)[y/n]: "
            )
            if spam_assinger == "y":
                spam = True
            else:
                spam = False

        if not args.spam:
            sound_assinger = input(
                "Should the program play sound after countdown? (not a part on notifications)[y/n]: "
            )
            if sound_assinger == "y":
                sound_path = input("Sound path: ")
                sound_path = sound_path.strip().strip('"').strip("'")

    wait_time_str = wait_time_str.replace(
        ",", "."
    )  # In some countries it's common to write "," in fractional number but doesn't work in python

    value = wait_time_str.rstrip(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )  # "value" will be a pure number from input
    unit = wait_time_str[len(value) :]

    value = float(value)

    if unit in (
        "m",
        "min",
        "mins",
        "minute",
        "minutes",
        "M",
        "Min",
        "Mins",
        "Minute",
        "Minutes",
    ):
        wait_time_float = value * 60
    elif unit in ("h", "hour", "hours", "hrs", "H", "Hour", "Hours", "Hrs"):
        wait_time_float = value * 3600
    elif unit in (
        "ms",
        "millisecond",
        "milisecond",
        "milliseconds",
        "miliseconds",
        "Ms",
        "Millisecond",
        "Milisecond",
        "Milliseconds",
        "Miliseconds",
    ):
        wait_time_float = value / 1000
    elif unit in (
        "s",
        "seconds",
        "sec",
        "secs",
        "second",
        "S",
        "Seconds",
        "Sec",
        "Secs",
        "Second",
        "",
    ):
        wait_time_float = value
    else:
        print(f"Unknown time unit: {unit}")
        sys.exit(1)

    if debug:
        print("Debug: everything set, executing main program. ")

    if print_time == True:
        timeprint_thread = threading.Thread(
            target=timeprint, args=(wait_time_float,), daemon=True
        )

        if debug:
            print("Debug: starting time countdown thread. ")
        timeprint_thread.start()

    time.sleep(
        wait_time_float
    )  # sleeping time that user set up earlier and after sending notify, executing cmd e.t.c.

    if cmd:
        if debug:
            print("Debug: executing command: " + cmd)
        subprocess.Popen(cmd, shell=True, start_new_session=True)

    if sound_path != "" and sound_path:
        if debug:
            print("Debug: trying to play a sound: " + sound_path)
        play_sound(sound_path, debug)

    if send_notification:
        if spam == True:
            notify(50, notification_text, debug)
        else:
            notify(1, notification_text, debug)

    if debug:
        print("Debug: nothing remaining to do, exiting. ")


if __name__ == "__main__":
    main()
