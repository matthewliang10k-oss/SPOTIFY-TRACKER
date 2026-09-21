import time

import tracker
import historytracker


POLL_INTERVAL = 2
HISTORY_SYNC_INTERVAL = 60


def main():

    print("===================================")
    print("      Spotify Tracker Backend")
    print("===================================")

    live_tracker = tracker.LiveTracker()

    print(
        f"Backend tracking for "
        f"{live_tracker.display_name}"
    )

    print("Live tracker: ON")
    print("History sync: ON")
    print()

    last_history_sync = 0

    try:

        while True:

            # --------------------------------
            # LIVE TRACKING
            # --------------------------------

            try:
                live_tracker.check_current_track()

            except Exception as e:
                print(f"Live tracker error: {e}")


            # --------------------------------
            # HISTORY TRACKING
            # --------------------------------

            current_time = time.time()

            if (
                current_time - last_history_sync
                >= HISTORY_SYNC_INTERVAL
            ):

                try:

                    print("\nRunning history sync...")

                    historytracker.sync_recent_history()

                    last_history_sync = current_time

                except Exception as e:

                    print(
                        f"History tracker error: {e}"
                    )


            # --------------------------------
            # WAIT
            # --------------------------------

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:

        print("\nStopping backend...")

        live_tracker.stop()

        print("Backend stopped safely.")


if __name__ == "__main__":
    main()