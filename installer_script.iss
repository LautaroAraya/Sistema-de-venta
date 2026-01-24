; Script de Inno Setup para Sistema de Ventas
; Este script crea un instalador completo con todas las dependencias

#define MyAppName "Sistema de Ventas"
#define MyAppVersion "1.0"
#define MyAppPublisher "Tu Empresa"
#define MyAppExeName "SistemaVentas.exe"

[Setup]
AppId={{SISTEMA-VENTAS-2026}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=SistemaVentas_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile={#SourcePath}\assets\logoinstalador.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SistemaVentas.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "serviceAccountKey.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "serviceAccountKey.json.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "firebase_config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "database\\*"; DestDir: "{app}\\database"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "reports\\*"; DestDir: "{app}\\reports"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\\*"; DestDir: "{app}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "logs\\*"; DestDir: "{app}\\logs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "views\\*"; DestDir: "{app}\\views"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "models\\*"; DestDir: "{app}\\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "utils\\*"; DestDir: "{app}\\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".update_config.json"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\database"; Permissions: users-full
Name: "{app}\reports"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
var
  WelcomeLabel: TNewStaticText;
begin
  WelcomeLabel := TNewStaticText.Create(WizardForm);
  WelcomeLabel.Parent := WizardForm.WelcomePage;
  WelcomeLabel.Caption := 
    'Este instalador configurará el Sistema de Ventas en su computadora.' + #13#10 + #13#10 +
    'Características:' + #13#10 +
    '- Registro de ventas y facturas' + #13#10 +
    '- Gestión de productos y proveedores' + #13#10 +
    '- Control de usuarios (Admin y Empleados)' + #13#10 +
    '- Reportes y estadísticas' + #13#10 +
    '- Base de datos SQLite incluida';
  WelcomeLabel.AutoSize := True;
  WelcomeLabel.Top := WizardForm.WelcomeLabel2.Top + WizardForm.WelcomeLabel2.Height + 20;
end;
