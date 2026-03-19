"""Entry point для альтернативной веб-версии Corpus Manager (FastAPI + React)."""
import subprocess
import sys
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(SCRIPT_DIR, "frontend")


def main():
    print("=" * 50)
    print("  Corpus Manager — React Web Version")
    print("=" * 50)
    print()
    print("Starting FastAPI server on http://localhost:8000 ...")
    print("Starting Vite React app on http://localhost:5173 ...")
    print()
    print("Press Ctrl+C to stop both servers.")
    print()

    # Запуск FastAPI через uvicorn
    fastapi_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=SCRIPT_DIR,
    )

    # Небольшая задержка для запуска API
    time.sleep(2)

    # Запуск React/Vite
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    react_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
    )

    try:
        fastapi_proc.wait()
        react_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        fastapi_proc.terminate()
        react_proc.terminate()
        fastapi_proc.wait()
        react_proc.wait()
        print("Servers stopped.")


if __name__ == "__main__":
    main()
