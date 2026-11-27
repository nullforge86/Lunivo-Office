; Inno-Setup-Skript für Lunivo Office. Aufruf aus dem Projektwurzelordner:
;   iscc /DAppVersion=0.1.0 installationspakete\windows\lunivo-office.iss
; Voraussetzung: dist\lunivo-office (PyInstaller) und erstellung\icons\lunivo-office.ico existieren.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6B0E3C34-5C61-4B7B-9A4E-3D0F7A6C1E21}
AppName=Lunivo Office
AppVersion={#AppVersion}
AppPublisher=Lunivo
AppPublisherURL=https://github.com/nullforge86/Lunivo-Office
DefaultDirName={autopf}\Lunivo Office
DefaultGroupName=Lunivo Office
DisableProgramGroupPage=yes
AllowNoIcons=yes
UninstallDisplayIcon={app}\lunivo-office.exe
SetupIconFile=..\..\erstellung\icons\lunivo-office.ico
LicenseFile=..\..\LICENSE
OutputDir=..\..\erstellung
OutputBaseFilename=Lunivo-Office_{#AppVersion}_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog
; Installationsverzeichnis ist im Assistenten wählbar
DisableDirPage=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\lunivo-office\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Lunivo Office"; Filename: "{app}\lunivo-office.exe"
Name: "{group}\Lunivo Office deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Lunivo Office"; Filename: "{app}\lunivo-office.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\lunivo-office.exe"; Description: "{cm:LaunchProgram,Lunivo Office}"; Flags: nowait postinstall skipifsilent
