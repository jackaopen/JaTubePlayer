#define MyAppName "JaTubePlayer"
#define MyAppVersion "3.0.1"
#define MyAppPublisher "Jackaopen"
#define MyAppURL "https://github.com/jackaopen/JaTubePlayer"
#define MyAppExeName "JaTubePlayer.exe"

[Setup]
AppId={{8D923BBD-C758-4ED3-906A-E7407A94124A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=output
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-Setup
SetupIconFile=..\..\_internal\jtp.ico
LicenseFile=..\..\LICENSE
UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern polar includetitlebar
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes

; The installer seeds the installing user's first-run data. The application
; owns all later writes under %APPDATA%\JaTubePlayer.
UsedUserAreasWarning=no

VersionInfoVersion=3.0.1.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:";
Name: "deleteuserdata"; Description: "Delete my JaTubePlayer settings, account data, WebView2 profile, and cache when uninstalling";

[Files]
Source: "..\..\dist\JaTubePlayer\*"; DestDir: "{app}"; Excludes: "\chrome_ext_pack\*,\user_data\*"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\dist\JaTubePlayer\user_data\config.json"; DestDir: "{userappdata}\JaTubePlayer"; DestName: "config.json"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "..\..\dist\JaTubePlayer\user_data\starred_vid.json"; DestDir: "{userappdata}\JaTubePlayer"; DestName: "starred_vid.json"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "..\..\dist\JaTubePlayer\chrome_ext_pack\*"; DestDir: "{userappdata}\JaTubePlayer\chrome_ext_pack"; Flags: ignoreversion recursesubdirs createallsubdirs uninsneveruninstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\jtp.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\jtp.ico"; Tasks: desktopicon

[Registry]
Root: HKLM64; Subkey: "SOFTWARE\JaTubePlayer"; ValueType: string; ValueName: "UpdaterDir"; ValueData: "{app}\_internal"; Flags: uninsdeletevalue uninsdeletekeyifempty

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\JaTubePlayer"; Tasks: deleteuserdata

[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    with WizardForm do
    begin
      FinishedLabel.Caption :=
        FinishedLabel.Caption + #13#10#13#10 +
        'Chrome extension: ' +
        ExpandConstant('{userappdata}\JaTubePlayer\chrome_ext_pack') + #13#10 + 
        'Open chrome://extensions and select Load unpacked.';

      AdjustLabelHeight(FinishedLabel);
      RunList.Top := FinishedLabel.Top + FinishedLabel.Height + ScaleY(8);
    end;
  end;
end;