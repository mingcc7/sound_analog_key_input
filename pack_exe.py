import PyInstaller.__main__

PyInstaller.__main__.run([
    'run.spec',
    "--contents-directory ."
    "--clean"
])