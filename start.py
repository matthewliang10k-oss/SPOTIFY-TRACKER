import os
import subprocess
import sys
import time


PROJECT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PYTHON = sys.executable


def start_process(name, command):

    print(f"Starting {name}...")

    process = subprocess.Popen(
        command,
        cwd=PROJECT_DIR
    )

    print(
        f"{name} started. "
        f"PID={process.pid}"
    )

    return process


def main():

    api = None
    backend = None
    dashboard = None

    try:

        print("===================================")
        print("       Spotify Tracker")
        print("===================================")
        print()

        # --------------------------------
        # API
        # --------------------------------

        api = start_process(
            "API",
            [
                PYTHON,
                "-u",
                os.path.join(
                    PROJECT_DIR,
                    "api.py"
                )
            ]
        )

        time.sleep(2)

        # --------------------------------
        # BACKEND
        # --------------------------------

        backend = start_process(
            "Backend",
            [
                PYTHON,
                "-u",
                os.path.join(
                    PROJECT_DIR,
                    "backend.py"
                )
            ]
        )

        time.sleep(2)

        # --------------------------------
        # DASHBOARD
        # --------------------------------

        dashboard = start_process(
            "Dashboard",
            [
                PYTHON,
                "-m",
                "streamlit",
                "run",
                os.path.join(
                    PROJECT_DIR,
                    "dashboard.py"
                )
            ]
        )

        print()
        print("===================================")
        print("       Everything is running")
        print("===================================")
        print()
        print("API:       http://127.0.0.1:5000")
        print("Dashboard: http://localhost:8501")
        print("Backend:   RUNNING")
        print()
        print(
            "The backend will continue running "
            "independently of the dashboard."
        )
        print()
        print("Press CTRL+C to stop everything.")
        print()

        # --------------------------------
        # MONITOR
        # --------------------------------

        while True:

            # ----------------------------
            # API
            # ----------------------------

            if api.poll() is not None:

                print(
                    f"WARNING: API stopped "
                    f"with exit code "
                    f"{api.returncode}"
                )

                api = None

            # ----------------------------
            # BACKEND
            # ----------------------------

            if backend.poll() is not None:

                print(
                    f"WARNING: Backend stopped "
                    f"with exit code "
                    f"{backend.returncode}"
                )

                backend = None

            # ----------------------------
            # DASHBOARD
            # ----------------------------

            if dashboard is not None:

                if dashboard.poll() is not None:

                    print(
                        f"Dashboard stopped "
                        f"with exit code "
                        f"{dashboard.returncode}"
                    )

                    dashboard = None

            time.sleep(2)

    except KeyboardInterrupt:

        print()
        print(
            "Stopping Spotify Tracker..."
        )

    finally:

        print()
        print("Stopping services...")

        processes = [
            ("API", api),
            ("Backend", backend),
            ("Dashboard", dashboard)
        ]

        for name, process in processes:

            if process is not None:

                if process.poll() is None:

                    print(
                        f"Stopping {name}..."
                    )

                    process.terminate()

        print("All services stopped.")


if __name__ == "__main__":
    main()
