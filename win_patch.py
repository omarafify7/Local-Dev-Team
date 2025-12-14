"""
Windows Compatibility Patch for CrewAI

This module patches the signal module to add missing POSIX signals
that CrewAI expects but don't exist on Windows.

IMPORTANT: This module MUST be imported BEFORE any crewai imports!
"""

import sys
import signal

if sys.platform == "win32":
    # CrewAI's system_events.py expects these POSIX signals
    # which don't exist on Windows. We add them as dummy values.
    _posix_signals = {
        "SIGHUP": 1,    # Hangup
        "SIGQUIT": 3,   # Quit
        "SIGTRAP": 5,   # Trace/breakpoint trap
        "SIGKILL": 9,   # Kill (cannot be caught)
        "SIGPIPE": 13,  # Broken pipe
        "SIGALRM": 14,  # Alarm clock
        "SIGCHLD": 17,  # Child status changed
        "SIGCONT": 18,  # Continue stopped process
        "SIGSTOP": 19,  # Stop (cannot be caught)
        "SIGTSTP": 20,  # Terminal stop
        "SIGTTIN": 21,  # Background read from tty
        "SIGTTOU": 22,  # Background write to tty
        "SIGURG": 23,   # Urgent condition on socket
        "SIGXCPU": 24,  # CPU time limit exceeded
        "SIGXFSZ": 25,  # File size limit exceeded
        "SIGVTALRM": 26,  # Virtual timer expired
        "SIGPROF": 27,  # Profiling timer expired
        "SIGWINCH": 28,  # Window size change
        "SIGIO": 29,    # I/O possible
        "SIGPWR": 30,   # Power failure restart
        "SIGSYS": 31,   # Bad system call
    }
    
    for sig_name, sig_val in _posix_signals.items():
        if not hasattr(signal, sig_name):
            setattr(signal, sig_name, sig_val)
    
    print("[win_patch] Applied POSIX signal compatibility patch for Windows")
