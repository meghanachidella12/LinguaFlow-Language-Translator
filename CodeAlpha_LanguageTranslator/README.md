# Lingua AI — Smart Language Translator

CodeAlpha AI Internship — Task 1: Language Translation Tool.

## Features
- White, lavender, and blue responsive Streamlit UI
- 21 source/target language options
- Online translation with MyMemory as the primary service and GoogleTranslator as a fallback
- Language swap, character counter, clear, copy, listen, and download controls
- Input validation, loading indicator, and visible error feedback

## Requirements
- Python 3.10 or newer recommended
- Internet connection for translation services
- A modern browser

## Run in VS Code
Open a terminal in this folder and run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If `python` is not recognized on Windows, try `py` instead.

## Translation service note
This app calls public third-party translation services. It does not train its own translation model. Service availability, rate limits, supported languages, and translation quality can change. The app tries MyMemory first and then attempts GoogleTranslator if the first service fails. If both services are unavailable, check your internet connection, firewall/proxy settings, and try again later. Do not enter confidential text.

## Suggested GitHub repository
`CodeAlpha_LanguageTranslationTool`
