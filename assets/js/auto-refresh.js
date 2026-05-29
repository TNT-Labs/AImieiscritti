(function () {
  var meta = document.querySelector('meta[name="build-time"]');
  if (!meta) return;
  var current = meta.getAttribute("content");
  var endpoint = meta.getAttribute("data-endpoint") || "/build.json";
  var POLL_MS = 30 * 60 * 1000;

  function check() {
    fetch(endpoint + "?t=" + Date.now(), { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data && data.build && data.build !== current) {
          location.reload();
        }
      })
      .catch(function () { /* offline: riproveremo */ });
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") check();
  });
  setInterval(check, POLL_MS);
})();
