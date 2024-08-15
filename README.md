# 声音模拟按键输入

## 1.简介

每个声音录入多个音频，作为数据集进行模型训练，绑定设备输入按键后，使生成模型对监听到的每段声音进行预测，将结果绑定的按键进行模拟输入。

## 2.安装

### (1)conda创建环境

conda create -n sound_analog_key_input python=3.8

### (2)激活环境

conda activate sound_analog_key_input

### (3)进入项目路径

cd sound_analog_key_input

### (4)安装依赖包

pip install -r requirements.txt

### (5)运行项目

python sound_analog_key_input.py

### (6)打包成exe并压缩，文件在dist路径中

python pack_exe.py

## 3.提示

### (1)手机变成计算机的麦克风
https://wolicheng.com/womic/download.html