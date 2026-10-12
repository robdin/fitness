/* Play the retained MP4 offline after cloning, without a server or rebuild. */
(() => {
  const chunks = window.REP_MVP_PARTS.map(part => {
    const binary = atob(part);
    return Uint8Array.from(binary, char => char.charCodeAt(0));
  });
  const url = URL.createObjectURL(new Blob(chunks, {type: 'video/mp4'}));
  document.getElementById('mvp-video').src = url;
  document.getElementById('video-download').href = url;
  delete window.REP_MVP_PARTS;
  window.addEventListener('pagehide', () => URL.revokeObjectURL(url), {once: true});
})();
