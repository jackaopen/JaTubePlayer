import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ACCOUNT_DIR = BASE_DIR / "account"
USER_DATA_DIR = BASE_DIR / "user_data"
PROJECT_FILE = BASE_DIR / "WebView2CookieHost.csproj"
HOST_EXE = BASE_DIR / "publish" / "WebView2CookieHost.exe"


def main():
    ACCOUNT_DIR.mkdir(parents=True, exist_ok=True)
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HOST_EXE.exists():
        command = (
            f'dotnet publish "{PROJECT_FILE}" '
            f'-c Release -r win-x64 --self-contained true '
            f'-p:PublishSingleFile=true '
            f'-o "{HOST_EXE.parent}"'
        )
        raise SystemExit(
            "Compiled WebView2 host not found.\n\n"
            "Build it once with .NET SDK:\n"
            f"{command}\n\n"
            f"Then run this script again."
        )

    result = subprocess.run(
        [str(HOST_EXE), str(BASE_DIR), "login"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.stdout.strip():
        print(result.stdout.strip())


if __name__ == "__main__":
    main()
