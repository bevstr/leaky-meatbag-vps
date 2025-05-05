document.addEventListener("DOMContentLoaded", function () {
  const ipDisplay = document.getElementById("current-ip");
  const dnsDisplay = document.getElementById("current-dns");
  const pollingStatus = document.getElementById("polling-status");
  const nextBtn = document.getElementById("next-btn");

  const baselineIP = window.baselineIP;
  const baselineDNS = window.baselineDNS;
  
  let pollingInterval = null;

  function dnsChanged(current, baseline) {
    if (!Array.isArray(current) || !Array.isArray(baseline)) return true;
    if (current.length !== baseline.length) return true;
    for (let i = 0; i < current.length; i++) {
      if (current[i] !== baseline[i]) return true;
    }
    return false;
  }

  function checkForChange() {
    fetch("/api/network-status")
      .then(response => response.json())
      .then(data => {
        const currentIP = data.ip;
        const currentDNS = data.dns;

        ipDisplay.textContent = currentIP || "Unavailable";
        dnsDisplay.innerHTML = Array.isArray(currentDNS) ? currentDNS.join('<br>') : (currentDNS || "Unavailable");

        if (currentIP !== baselineIP || dnsChanged(currentDNS, baselineDNS)) {
          clearInterval(pollingInterval);
          pollingStatus.innerHTML = '✅ Change detected! You can now click "Next."';
          pollingStatus.className = 'text-green-400 mt-2';
          pollingStatus.closest('.stat-card').classList.add('ok');
          nextBtn.disabled = false;
        }
      })
      .catch(error => {
        console.error("Error fetching network status:", error);
      });
  }

  function animateDots() {
    const dots = document.getElementById("dots");
    let dotCount = 1;
    setInterval(() => {
      dots.textContent = ".".repeat(dotCount);
      dotCount = (dotCount % 3) + 1;
    }, 600);
  }

  if (pollingStatus && nextBtn && ipDisplay && dnsDisplay) {
    pollingInterval = setInterval(checkForChange, 5000); // Poll every 5 seconds
    animateDots();
  }
});
