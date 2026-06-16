// Lifecycle board — entry switch, document upload, status + approval toggles.
(function () {
  const board = document.querySelector('.phase-board');

  // Switch between entries.
  const sel = document.getElementById('entry-select');
  if (sel) sel.addEventListener('change', () => { window.location = '/lifecycle/' + sel.value; });

  if (!board) return;
  const entryId = board.dataset.entryId;

  // Upload a document for an artifact.
  board.addEventListener('change', async (e) => {
    const input = e.target.closest('.doc-upload');
    if (!input || !input.files.length) return;
    const fd = new FormData();
    fd.append('file', input.files[0]);
    fd.append('phase', input.dataset.phase);
    fd.append('artifact', input.dataset.artifact);
    const res = await fetch(`/api/entries/${entryId}/documents`, { method: 'POST', body: fd });
    const out = await res.json();
    if (out.success) location.reload();
    else alert('Upload failed: ' + out.error);
  });

  // Advance document status + toggle approvals.
  board.addEventListener('click', async (e) => {
    const adv = e.target.closest('.doc-advance .mini');
    if (adv) {
      const docEl = e.target.closest('.doc');
      const res = await fetch(`/api/documents/${docEl.dataset.docId}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: adv.dataset.status }),
      });
      const out = await res.json();
      if (out.success) location.reload(); else alert('Update failed: ' + out.error);
      return;
    }

    const appr = e.target.closest('.approval');
    if (appr) {
      const next = appr.dataset.status === 'APPROVED' ? 'PENDING' : 'APPROVED';
      const res = await fetch(`/api/entries/${entryId}/approvals`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phase: +appr.dataset.phase, team: appr.dataset.team, status: next }),
      });
      const out = await res.json();
      if (out.success) location.reload(); else alert('Approval failed: ' + out.error);
    }
  });
})();
