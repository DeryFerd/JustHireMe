# Windows Release Checklist

The first public release target is a Windows desktop installer.

## Build

```powershell
npm install
cd backend
uv sync --dev
cd ..
.\scripts\build-sidecar.ps1
npm run tauri build
```

## Smoke Test

- Install on a clean Windows machine or VM.
- Open the app without developer tools.
- Enter a local/Ollama or API provider setting.
- Import a profile or resume.
- Run a scan.
- Verify leads show signal, fit, and quality explanations.
- Generate resume PDF, cover letter PDF, and outreach drafts.

## Release Notes

Mention that browser automation is experimental. The supported workflow is scraper, ranker, vector matching, and customization.
