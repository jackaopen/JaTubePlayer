#define MyAppName "JaTubePlayer"
#define MyAppVersion "3.0"
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
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes

; The installer seeds the installing user's first-run data. The application
; owns all later writes under %APPDATA%\JaTubePlayer.
UsedUserAreasWarning=no

VersionInfoVersion=3.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "deleteuserdata"; Description: "Delete my JaTubePlayer settings, account data, WebView2 profile, and cache when uninstalling"; GroupDescription: "User data:"; Flags: unchecked

[Files]
Source: "..\..\dist\JaTubePlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "..\..\dist\JaTubePlayer\user_data\config.json"; DestDir: "{userappdata}\JaTubePlayer"; DestName: "config.json"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "..\..\dist\JaTubePlayer\user_data\starred_vid.json"; DestDir: "{userappdata}\JaTubePlayer"; DestName: "starred_vid.json"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\jtp.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\_internal\jtp.ico"; Tasks: desktopicon

[Registry]
; Store the selected uninstall-data policy. Both entries are present so a
; later upgrade can change the previous choice in either direction.
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "DeleteUserDataOnUninstall"; ValueData: "1"; Tasks: deleteuserdata; Flags: uninsdeletekeyifempty
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: dword; ValueName: "DeleteUserDataOnUninstall"; ValueData: "0"; Tasks: not deleteuserdata; Flags: uninsdeletekeyifempty

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent runasoriginaluser

[Code]
var
  DeleteUserDataOnUninstall: Boolean;

function InitializeUninstall(): Boolean;
var
  DeleteUserDataValue: Cardinal;
begin
  DeleteUserDataOnUninstall := False;

  if RegQueryDWordValue(
    HKLM,
    'Software\{#MyAppPublisher}\{#MyAppName}',
    'DeleteUserDataOnUninstall',
    DeleteUserDataValue) then
  begin
    DeleteUserDataOnUninstall := DeleteUserDataValue <> 0;
  end;

  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  UserDataDir: String;
begin
  if (CurUninstallStep = usPostUninstall) and DeleteUserDataOnUninstall then
  begin
    // Delete only this exact application-owned directory.
    UserDataDir := AddBackslash(ExpandConstant('{userappdata}')) + '{#MyAppName}';
    if DirExists(UserDataDir) then
      DelTree(UserDataDir, True, True, True);
  end;
end;