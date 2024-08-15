import PyInstaller.__main__
import sys
import shutil
import subprocess

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

PyInstaller.__main__.run(
    ["sound_analog_key_input.py", "--noconsole", "--clean", "--noconfirm"]
)

shutil.copy("configuration.json", "dist/sound_analog_key_input/configuration.json")
shutil.copytree("language", "dist/sound_analog_key_input/language")

# 压缩
command = [
    "7z/7za.exe",
    "a",
    "-t7z",
    "-v100m",
    "sound_analog_key_input.7z",
    "sound_analog_key_input",
]
subprocess.run(command, cwd="dist")
