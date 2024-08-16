import PyInstaller.__main__
import sys
import shutil
import subprocess
import re

# 安装requirements.txt中的包
subprocess.run(
    ["pip", "install", "-r", "requirements.txt", "--disable-pip-version-check"],
    check=True,
)
# 分析安装过程中的输出
install_output = subprocess.run(
    ["pip", "install", "-r", "requirements.txt", "--disable-pip-version-check"],
    check=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).stdout
# 解码字节输出为Unicode字符串
install_output_str = install_output.decode("utf-8")
# 提取安装的包的名称
required_packages = re.findall(
    r"Requirement already satisfied: (.+) in", install_output_str
)
current_required_packages_names = set(
    package.split("==")[0]
    .split(">")[0]
    .split("<")[0]
    .split("!=")[0]
    .replace("-", "_")
    .lower()
    for package in required_packages
)
# 使用pip freeze命令获取当前环境中安装的所有包
installed_packages = subprocess.run(
    ["pip", "freeze"], stdout=subprocess.PIPE, text=True
).stdout.splitlines()
current_installed_packages_names = set(
    package.split("==")[0].replace("-", "_").lower() for package in installed_packages
)
# 创建一个集合来存储不在installed_packages中的包
unneeded_packages = current_installed_packages_names - current_required_packages_names
# 卸载不在installed_packages中的包
for package in unneeded_packages:
    subprocess.run(["pip", "uninstall", package, "-y"], check=True)


# 打包成exe
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
