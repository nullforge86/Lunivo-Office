# Windows: Installer (.exe)

Ergebnis: `Lunivo-Office_VERSION_Setup.exe` (Inno Setup, Skript `lunivo-office.iss`), Python ist eingebettet (PyInstaller).

Assistent mit wählbarem Installationsverzeichnis, Startmenü-Eintrag, optionaler Desktop-Verknüpfung (Aufgabe, standardmäßig aus) und Eintrag unter „Apps & Features“ zur vollständigen Deinstallation.

```powershell
python -m pip install -r requirements.txt pyinstaller pillow
python installationspakete\icons_erzeugen.py
pyinstaller installationspakete\lunivo-office.spec --noconfirm
iscc /DAppVersion=0.1.0 installationspakete\windows\lunivo-office.iss    # Inno Setup 6 nötig
```

Ohne Installation: `Lunivo-Office_VERSION_windows-portable.zip` entpacken, `lunivo-office\lunivo-office.exe` starten.
Aus dem Quellcode: `python -m venv .venv`, `.venv\Scripts\python -m pip install -r requirements.txt`, `.venv\Scripts\python main.py`.
Benutzerdaten: Einstellungen und Daten unter `%APPDATA%`, Zwischenspeicher unter `%LOCALAPPDATA%`; die Deinstallation lässt sie stehen.
Zusatzpakete: Die Offline-Übersetzung Deutsch↔Englisch liegt im Ordner `argos\` neben `lunivo-office.exe`. Die Lade-Skripte für Stimmen und Schriften gibt es nur für Linux.
Alle Wege für alle Systeme: `dokumentation/benutzerhandbuch/installation.md`.
Der Installer ist **nicht signiert**; Windows SmartScreen zeigt deshalb eine Warnung („Weitere Informationen → Trotzdem ausführen“). Zum Signieren ein Code-Signing-Zertifikat und `SignTool` in Inno Setup (`SignTool=`) einrichten.
