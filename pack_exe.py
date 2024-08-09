import PyInstaller.__main__
import sys
import shutil

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

PyInstaller.__main__.run([
    'run.py',
    '--noconfirm'
])

shutil.copy("configuration.json", "dist/run/configuration.json")
shutil.copytree("language", "dist/run/language")
shutil.copy("temp.wav", "dist/run/temp.wav")

# pip install nuitka
# nuitka --standalone run.py
