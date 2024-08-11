import PyInstaller.__main__
import sys
import shutil
import os
import zipfile

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

PyInstaller.__main__.run([
    'sound_analog_key_input.py',
    '--noconsole',
    '--clean',
    '--noconfirm'
])

shutil.copy("configuration.json", "dist/sound_analog_key_input/configuration.json")
shutil.copytree("language", "dist/sound_analog_key_input/language")
shutil.copy("temp.wav", "dist/sound_analog_key_input/temp.wav")

# 压缩文件夹
def compress_folder(source_dir, output_filename):
    # 获取文件总数
    total_files = sum([len(files) for _, _, files in os.walk(source_dir)])
    
    # 创建一个 ZipFile 对象，用于写入
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        processed_files = 0  # 已处理的文件数
        # 遍历指定目录及其子目录中的所有文件
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # 构建完整的文件路径
                file_path = os.path.join(root, file)
                # 在 ZIP 文件中存储文件
                zipf.write(file_path, os.path.relpath(file_path, source_dir))
                
                processed_files += 1
                # 显示进度
                print(f"Compressing: {processed_files}/{total_files} ({processed_files / total_files * 100:.2f}%)", end='\r')


# 使用方法
source_directory = 'dist/sound_analog_key_input'  # 替换为你要压缩的文件夹路径
output_zip_file = 'dist/sound_analog_key_input.zip'  # 输出的 ZIP 文件名

compress_folder(source_directory, output_zip_file)
print("Compression completed.")