# Installation Guide
## Standard Installation
1. Run the `.msi` installer.
2. Accept the UAC prompt.
3. The application installs to `C:\Program Files\GovTrack AI\`.
4. All your personal data is safely written to `C:\Users\<User>\AppData\Roaming\GovTrackAI\`. This ensures that updating the `.msi` in the future will **never** overwrite your databases or settings.

## Portable Mode
If you prefer not to install the application, or want to carry it on a USB drive:
1. Extract the `.zip` release.
2. Create an empty file named `.portable` in the same directory as the executable.
3. Run the executable. All databases and configurations will be stored directly inside a `data/` folder next to the executable.
