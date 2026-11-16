"""Launch the standalone Gmail polling worker with `py worker.py`."""

from app.email.imap_worker import main


if __name__ == "__main__":
    main()
