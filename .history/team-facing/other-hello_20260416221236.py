import subprocess

subprocess.run(
        [
            r"C:\MinGW\bin\g++.exe",
            r"C:\Users\andre\PycharmProjects\code-jam\team-facing\submissions\submission.cpp",
            "-o",
            r"C:\Users\andre\PycharmProjects\code-jam\team-facing\submissions\submission"
        ],
        capture_output=True,
        text=True
        )
print("Other hello world")