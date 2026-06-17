# Kagurazaka Core - 开箱即用

## 快速打包

1. 安装 Python 3.10+（如未安装）
2. 双击 `build.bat`
3. 等待编译完成
4. 输出在 `dist\Kagurazaka.exe`

## 制作安装包（可选）

1. 先完成上述打包步骤
2. 安装 [Inno Setup 6+](https://jrsoftware.org/isinfo.php)
3. 用 Inno Setup 打开 `installer.iss`
4. 点击 Compile → 输出 `installer\Kagurazaka-Setup.exe`

## 使用

- 双击 `Kagurazaka.exe` 启动
- 首次运行自动生成 `config.json` 模板
- 填好 API key 后刷新页面即可使用
- 浏览器访问 http://localhost:7860
