let modalLockedOpen = false; // Lock when modal is open
let previousData = {}; // Save last good state

async function updateDashboard() {
  try {
    const response = await fetch("/api/dashboard-status");
    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    if (JSON.stringify(data) !== JSON.stringify(previousData)) {
      previousData = data; // Save new snapshot

      // Update VPN Protection Label Icon
      const vpnProtectionLabel = document.querySelector("#vpn-status-card .stat-label");
      if (vpnProtectionLabel) {
        vpnProtectionLabel.innerHTML = `
          <img src="${data.vpn_status === "Protected" ? "/static/img/icon-small.png" : "/static/img/icon-small-blocked.png"}"
          style="height: 1.5em; vertical-align: middle; margin-right: 0.4em;">
          VPN Protection
        `;
      }

      // Update VPN Status (Protected / Leaking)
      const vpnStatusCard = document.getElementById("vpn-status-card");
      const vpnStatusText = document.getElementById("vpn-status");
      if (vpnStatusCard && vpnStatusText) {
        vpnStatusText.innerHTML = `
          <img src="${data.vpn_status === "Protected" ? "/static/img/icon-small.png" : "/static/img/icon-small-blocked.png"}"
          style="height: 1.5em; vertical-align: middle; margin-right: 0.5em;">
          ${data.vpn_status === "Protected" ? "Protected" : "Leaking"}
        `;
        vpnStatusCard.className = "stat-card " + (data.vpn_status === "Protected" ? "ok" : "fail");
      }

      // ── Update Public IP ─────────────────────────────────────────────
      const publicIpCard  = document.getElementById("public-ip-card");
      const publicIpText  = document.getElementById("public-ip");
      const trustedIpEl   = document.getElementById("trusted-ip");
      const trustedIpText = document.getElementById("trusted-ip-text");   // NEW
      const trustedIp     = trustedIpEl?.innerText.trim();

      if (publicIpCard && publicIpText) {
        publicIpText.innerHTML  = `Current: ${data.public_ip || "—"}`;
        trustedIpText.innerHTML = `Trusted: ${trustedIp || "—"}`;         // NEW
        publicIpCard.className  = "stat-card " +
            (trustedIp && data.public_ip === trustedIp ? "ok" : "fail");

        // Trigger GeoIP fetch when trusted IP matches
        if (trustedIp && data.public_ip === trustedIp) {
          console.log("✅ Trusted IP matches current Public IP. Fetching fresh GeoIP...");
          fetchGeoIP();
        }
      }

      // ── Update DNS Server ────────────────────────────────────────────
      const dnsCard          = document.getElementById("dns-card");
      const dnsServerText    = document.getElementById("dns-server");
      const trustedDnsTextEl = document.getElementById("trusted-dns-text");  // NEW
      const trustedDnsRaw    = document.getElementById("trusted-dns")?.innerText.trim();
      const trustedDnsList   = trustedDnsRaw ? trustedDnsRaw.split(',').map(d => d.trim()) : [];

      if (dnsCard && dnsServerText) {
        dnsServerText.innerHTML    = `Current: ${data.dns_server || "—"}`;
        trustedDnsTextEl.innerHTML = `Trusted: ${trustedDnsList.join(", ") || "—"}`; // NEW
        dnsCard.className          = "stat-card " +
              (trustedDnsList.includes(data.dns_server) ? "ok" : "fail");
      }

      // Update Adblock
      const adblockCard = document.getElementById("adblock-card");
      const adblockStatusText = document.getElementById("adblock-status");
      if (adblockCard && adblockStatusText) {
        adblockStatusText.innerHTML = data.adblock_status === "Working" ? "🟢 Working" : "🔴 Leaking";
        adblockCard.className = "stat-card " + (data.adblock_status === "Working" ? "ok" : "red");
      }

      // Handle Warnings
      const warningBanner = document.getElementById("warning-banner-container");
      if (warningBanner && !modalLockedOpen) {
        if (data.show_warning) {
          warningBanner.innerHTML = `
            <div class="warning-banner">
              <div style="font-weight: bold; font-size: 1.2em; margin-bottom: 0.8em;">
                🚰 VPN/DNS Change Detected!
                <div style="font-weight: normal; font-size: 0.9em; margin-top: 0.5em;">
                  Your network settings have changed.<br>Choose an action below:
                </div>
              </div>
              <div style="display: flex; gap: 1em; justify-content: center; flex-wrap: wrap; margin-top: 1em;">
                <form method="GET" action="/reset-onboarding" style="display: inline;">
                  <button type="submit" class="warning-button reonboard">
                    🧹 Re-Onboard<br><span style="display:block; font-weight: normal; font-size: 0.8em; margin-top: 2px;">Start Over Fresh</span>
                  </button>
                </form>
                <button onclick="openModal()" class="warning-button accept">
                  ✅ Accept Current Settings<br><span style="display:block; font-weight: normal; font-size: 0.8em; margin-top: 2px;">Trust New IP & DNS</span>
                </button>
              </div>
            </div>

            <div id="confirm-modal" class="modal hidden">
              <div class="modal-content">
                <h2>
                  <img src="/static/img/icon-small.png" alt="Brain Icon" style="height: 1.5em; vertical-align: middle; margin-right: 0.4em;">
                  Are you sure?
                </h2>
                <p>
                  You are about to save:<br><br>
                  <strong>New Public IP:</strong> ${data.public_ip || "Unavailable"}<br>
                  <strong>New DNS Server:</strong> ${data.dns_server || "Unavailable"}<br><br>
                  This will set them as your new trusted baseline.<br>
                  Only continue if you're sure you're connected to your intended VPN server.
                </p>
                <div class="modal-actions">
                  <button onclick="confirmAcceptNew()" class="button-accept">✅ Yes, Save New Settings</button>
                  <button onclick="closeModal()" class="button-cancel">❌ Cancel</button>
                </div>
              </div>
            </div>
          `;
        } else {
          warningBanner.innerHTML = "";
        }
      }
    }
  } catch (error) {
    console.error("Polling failed:", error);
  }
}

function pollStatus() {
  updateDashboard();
  setInterval(updateDashboard, 5000);
}

function openModal() {
  document.getElementById('confirm-modal').classList.remove('hidden');
  modalLockedOpen = true;
}

function closeModal() {
  document.getElementById('confirm-modal').classList.add('hidden');
  modalLockedOpen = false;
}

async function confirmAcceptNew() {
  try {
    const response = await fetch("/api/accept-new", { method: "POST" });
    if (!response.ok) throw new Error("Failed to accept new config");

    closeModal();

    /* ---- Update both the hidden <div> *and* the visible "Trusted:" labels ---- */
    const publicIpEl   = document.getElementById("public-ip");
    const dnsServerEl  = document.getElementById("dns-server");

    const publicIp  = publicIpEl  ? publicIpEl.innerText.replace("Current:", "").trim() : "";
    const dnsServer = dnsServerEl ? dnsServerEl.innerText.replace("Current:", "").trim() : "";

    document.getElementById("trusted-ip").innerText       = publicIp;
    document.getElementById("trusted-ip-text").innerText  = `Trusted: ${publicIp}`;

    document.getElementById("trusted-dns").innerText      = dnsServer;
    document.getElementById("trusted-dns-text").innerText = `Trusted: ${dnsServer}`;
    /* ------------------------------------------------------------------------- */

    updateDashboard();
    retryFetchGeoIP();

  } catch (error) {
    console.error("Accept new failed:", error);
  }
}

async function retryFetchGeoIP(attempts = 5, delay = 2000) {
  for (let i = 0; i < attempts; i++) {
    console.log(`GeoIP attempt ${i + 1}/${attempts}`);
    await fetchGeoIP();
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}

async function fetchGeoIP() {
  try {
    const response = await fetch('https://ipapi.co/json/');
    if (!response.ok) throw new Error('Failed to fetch GeoIP info');

    const data = await response.json();

    if (data && data.city && data.country_name && data.country_code) {
      const flagEmoji = countryCodeToEmoji(data.country_code);
      document.getElementById('geoip-location').innerText = `${flagEmoji} ${data.city}, ${data.country_name}`;
    } else {
      document.getElementById('geoip-location').innerText = "🌐 Unknown Location";
    }
  } catch (error) {
    console.error('Error fetching GeoIP:', error);
    document.getElementById('geoip-location').innerText = "🌐 Unknown Location";
  }
}

function countryCodeToEmoji(countryCode) {
  if (!countryCode) return "";
  return countryCode
    .toUpperCase()
    .replace(/./g, char => String.fromCodePoint(127397 + char.charCodeAt()));
}

// ✅ One clean DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  pollStatus();
  fetchGeoIP();
});
