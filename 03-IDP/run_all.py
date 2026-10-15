"""
run_all.py
==========
Master Orchestrator script that starts all three servers simultaneously:
1. Identity Provider (IDP) on Port 5003
2. Protected Resource Server on Port 5004
3. Client Web Application on Port 5005

Features:
- Ensures RSA key pair exists before booting servers.
- Uses Python subprocess to launch all services.
- Real-time prefixed output streaming in terminal.
- Graceful shutdown of all child processes on Ctrl+C.
- Clean system dashboard banner with URLs and demo credentials.
"""

import os
import sys
import time
import socket
import signal
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from generate_keys import ensure_keys_exist

SERVERS = [
    {
        "name": "IDP-SERVER",
        "script": "idp_server.py",
        "port": 5003,
        "prefix": "\033[94m[IDP:5003]\033[0m",
        "url": "http://localhost:5003"
    },
    {
        "name": "RESOURCE-SERVER",
        "script": "resource_server.py",
        "port": 5004,
        "prefix": "\033[92m[RESOURCE:5004]\033[0m",
        "url": "http://localhost:5004"
    },
    {
        "name": "CLIENT-APP",
        "script": "client_app.py",
        "port": 5005,
        "prefix": "\033[95m[CLIENT:5005]\033[0m",
        "url": "http://localhost:5005"
    }
]

processes = []


def is_port_in_use(port):
    """Checks if a local TCP port is already open/in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def stream_output(process, prefix):
    """Streams stdout/stderr of a child process with a colored prefix."""
    try:
        for line in iter(process.stdout.readline, ""):
            if line:
                clean_line = line.rstrip()
                print(f"{prefix} {clean_line}", flush=True)
            else:
                break
    except (ValueError, IOError):
        pass


def stop_all_processes():
    """Terminates all running child server processes cleanly."""
    print("\n[RUN_ALL] Shutting down all servers...")
    for proc in processes:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    print("[RUN_ALL] All servers stopped cleanly. Goodbye!\n")


def print_banner():
    banner = f"""
========================================================================
   CUSTOM IDENTITY PROVIDER (IDP) & OAUTH 2.0 / OIDC ECOSYSTEM
========================================================================
  All 3 servers are starting up in parallel:

  1. Identity Provider (IDP):
     * Home:           http://localhost:5003
     * JWKS Keys:      http://localhost:5003/jwks
     * OIDC Discovery: http://localhost:5003/.well-known/openid-configuration
     * Authorization:  http://localhost:5003/authorize

  2. Protected Resource Server:
     * Base API:       http://localhost:5004
     * Profile:        http://localhost:5004/api/profile
     * Protected Data: http://localhost:5004/api/data

  3. Client Web Application (START HERE!):
     * Web Portal:     \033[1;36mhttp://localhost:5005\033[0m

  Pre-configured Demo Test Accounts:
     * Username: alice   | Password: password123
     * Username: bob     | Password: secret456

  Press Ctrl+C at any time in this window to stop all 3 servers.
========================================================================
"""
    print(banner, flush=True)


def main():
    # 1. Ensure RSA key pair exists
    print("[RUN_ALL] Step 1/3: Checking RSA key pair...")
    ensure_keys_exist()

    # 2. Check for port conflicts
    print("[RUN_ALL] Step 2/3: Checking ports 5003, 5004, 5005...")
    for srv in SERVERS:
        if is_port_in_use(srv["port"]):
            print(f"[RUN_ALL] WARNING: Port {srv['port']} ({srv['name']}) appears to be already in use!")

    # 3. Print Banner
    print_banner()

    # 4. Launch all 3 servers
    for srv in SERVERS:
        script_path = os.path.join(BASE_DIR, srv["script"])
        print(f"[RUN_ALL] Launching {srv['name']} on port {srv['port']}...")
        
        # Windows-friendly unbuffered execution
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        proc = subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=BASE_DIR,
            env=env
        )
        processes.append(proc)

        # Start thread to stream output
        t = threading.Thread(target=stream_output, args=(proc, srv["prefix"]), daemon=True)
        t.start()

    # 5. Monitor and handle Ctrl+C
    try:
        while True:
            time.sleep(1)
            # Check if any process exited unexpectedly
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    srv = SERVERS[i]
                    print(f"[RUN_ALL] Warning: {srv['name']} exited with code {proc.returncode}")
    except KeyboardInterrupt:
        stop_all_processes()


if __name__ == "__main__":
    main()
