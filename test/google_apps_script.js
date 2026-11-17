function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();

    handleMushra(ss, data);

    const resultCount = (data.results || []).length;
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', rows: resultCount }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function handleMushra(ss, data) {
  let sheet = ss.getSheetByName('MUSHRA');
  if (!sheet) {
    sheet = ss.insertSheet('MUSHRA');
  }

  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      'timestamp',
      'participant_id',
      'experience',
      'headphones',
      'notes',
      'scenario',
      'reference',
      'sample_id',
      'sample_label',
      'score',
      'config_title'
    ]);
    formatHeaders(sheet, 11);
  }

  const participant = data.participant || {};
  const results = data.results || [];
  const configTitle = data.config_title || '';

  results.forEach(function (result) {
    sheet.appendRow([
      result.timestamp || participant.timestamp || new Date().toISOString(),
      result.participant_id || participant.id || '',
      result.experience || participant.experience || '',
      result.headphones || participant.headphones || '',
      participant.notes || '',
      result.scenario || '',
      result.reference || '',
      result.sample_id || '',
      result.sample_label || '',
      result.score !== undefined ? result.score : '',
      configTitle
    ]);
  });

  sheet.autoResizeColumns(1, 11);
}

function formatHeaders(sheet, numCols) {
  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange.setFontWeight('bold');
  headerRange.setBackground('#78350F');
  headerRange.setFontColor('#FFFFFF');
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ok',
      message: 'Listening test results collector is running. Send POST to submit results.'
    }))
    .setMimeType(ContentService.MimeType.JSON);
}