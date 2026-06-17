; Inno Setup Script for Kagurazaka Core
; 用法:
;   1. 先跑 build.bat 生成 dist\Kagurazaka.exe
;   2. 安装 Inno Setup 6+: https://jrsoftware.org/isinfo.php
;   3. 用 Inno Setup 打开此文件 → Compile
;   输出: installer\Kagurazaka-Setup.exe

#define MyAppName "Kagurazaka"
#define MyAppVersion "1.0"
#define MyAppPublisher "Kagurazaka"
#define MyAppExeName "Kagurazaka.exe"

[Setup]
AppId={{B6F8A3D2-5C4E-4A1F-9D7E-8B2C6A4F3E1D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=.\installer
OutputBaseFilename=Kagurazaka-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "额外图标:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 Kagurazaka"; Flags: nowait postinstall skipifsilent
