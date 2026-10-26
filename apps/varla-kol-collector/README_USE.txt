Varla Collector Portable Package

This package contains the actual program files, not only the Codex skill.

Included:
- KOL_recorder
- viral_video_finder
- chrome_extension
- current KOL xlsx
- current viral result xlsx/html
- Start_Varla_Collector.bat

First use:

1. Extract the full zip folder.

2. Double-click:
   Start_Varla_Collector.bat

3. Keep the two black service windows open.

4. Install Chrome extension:
   - Open Chrome
   - Go to chrome://extensions
   - Turn on Developer mode
   - Click Load unpacked
   - Select this folder:
     chrome_extension

5. Open TikTok / Instagram / YouTube Shorts.
   Use the floating "Varla" panel on the right side.

KOL records are saved here:
KOL_recorder\outputs\varla_kol_tracker.xlsx

Viral video results are saved here:
viral_video_finder\outputs

Important rules:
- KOL workbook is 16 columns.
- Do not add Content Type or Notes back.
- Do not write Moto.
- If email or views are not visible, leave them blank.

Troubleshooting:

If the extension says service is not running:
- Run Start_Varla_Collector.bat again.
- Keep both black windows open.

If xlsx cannot be written:
- Close the xlsx file in Excel/WPS.
- Click the collect button again.

If Python is missing:
- Install Python 3.10+ from python.org.
- During install, tick "Add Python to PATH".

If openpyxl is missing:
- The bat files will try to install it automatically.
