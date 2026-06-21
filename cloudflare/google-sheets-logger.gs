/**
 * AISearch Global — AEO Score Calculator: Google Sheets Logger
 * Google Apps Script — deploy as a Web App to receive scan data from the Cloudflare Worker.
 *
 * SETUP (do this once):
 *  1. Go to https://sheets.new — create a blank Google Sheet named "AEO Score Scans"
 *  2. In the Sheet, go to Extensions → Apps Script
 *  3. Paste this entire file, replacing the default code
 *  4. Click Save, then Run → setupTrigger (approve permissions when prompted)
 *  5. Click Deploy → New deployment → Type: Web app
 *     - Execute as: Me
 *     - Who has access: Anyone
 *  6. Click Deploy, copy the Web App URL
 *  7. In your terminal, run:
 *       cd cloudflare
 *       npx wrangler secret put SHEETS_WEBHOOK_URL
 *     Paste the Web App URL when prompted
 *  8. Deploy the Worker: npx wrangler deploy aeo-score-worker.js
 *
 * COLUMNS (auto-created on first submission):
 *  A: Timestamp (ISO)
 *  B: URL Submitted (raw input from user)
 *  C: Domain (parsed)
 *  D: Industry
 *  E: Location
 *  F: AEO Score (/100)
 *  G: Grade (A+–F)
 *  H: Marketing Consent (Yes/No)
 *  I: Delete After (date — rows auto-deleted after this date by daily trigger)
 */

const SHEET_NAME = 'Scans';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss   = SpreadsheetApp.getActiveSpreadsheet();
    let sheet  = ss.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      const headers = ['Timestamp', 'URL Submitted', 'Domain', 'Industry', 'Location', 'AEO Score', 'Grade', 'Marketing Consent', 'Delete After'];
      sheet.appendRow(headers);
      sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#0ABAB5').setFontColor('#ffffff');
      sheet.setFrozenRows(1);
      sheet.setColumnWidth(1, 180);
      sheet.setColumnWidth(2, 240);
      sheet.setColumnWidth(3, 160);
    }

    const now         = new Date();
    const deleteAfter = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);

    sheet.appendRow([
      now.toISOString(),
      data.urlSubmitted  || '',
      data.domain        || '',
      data.industry      || '',
      data.location      || '',
      data.score         !== undefined ? data.score : '',
      data.grade         || '',
      data.promoConsent  ? 'Yes' : 'No',
      Utilities.formatDate(deleteAfter, 'UTC', 'yyyy-MM-dd'),
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Deletes rows whose "Delete After" date (column I) has passed.
 * Run setupTrigger() once to schedule this automatically at 2am UTC daily.
 */
function deleteExpiredRows() {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) return;

  const data  = sheet.getDataRange().getValues();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (let i = data.length - 1; i >= 1; i--) {
    const val         = data[i][8];
    if (!val) continue;
    const deleteAfter = new Date(val);
    if (!isNaN(deleteAfter) && deleteAfter < today) {
      sheet.deleteRow(i + 1);
    }
  }
}

/**
 * Run this once from the Apps Script editor to create the daily cleanup trigger.
 * Extensions → Apps Script → Run → setupTrigger
 */
function setupTrigger() {
  const existing = ScriptApp.getProjectTriggers();
  existing.forEach(t => { if (t.getHandlerFunction() === 'deleteExpiredRows') ScriptApp.deleteTrigger(t); });

  ScriptApp.newTrigger('deleteExpiredRows')
    .timeBased()
    .everyDays(1)
    .atHour(2)
    .create();

  Logger.log('Daily cleanup trigger set — deleteExpiredRows runs at 2am UTC every day.');
}
