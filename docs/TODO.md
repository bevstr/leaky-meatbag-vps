# Leaky Meatbag: Phase 2 TODO List

## ✅ Completed
- [x] **1. Skip onboarding if config already exists**  
  - Skips `/onboarding` if config file has trusted IP and DNS  
  - Fully tested and working
- [x] **8. Add “Last Checked” timestamp + manual re-check button**  
  - Visible timestamp under status  
  - Force-refresh logic without full page reload

---

## 🔜 Remaining Items (Phase 2)

- [x] **2. Redesign Dashboard to show trusted vs actual**  
  - Compare current vs trusted for IP and DNS  
  - Use color-coded comparison rows for clarity  
  - Show explicit mismatches or confirmations

- [x] **3. Add warning logic for fallback DNS in use**  
  - If using Quad9/Cloudflare (fallback), warn that it’s safe but not VPN DNS  
  - ✅ This logic exists, but will be re-verified as UI evolves
  not relavaent due to mandatory onboarding

- [x] **4. Improve ad block test reliability**  
  - Add retry logic or fallback test to confirm adblock behavior  
  - Possibly check multiple domains or return types

- [x] **5. Visual dashboard refactor for status at a glance**  
  - Emoji + color bar + short label  
  - Easier for non-technical users to digest

- [x] **6. Add manual override field to config UI**  
  - Allow manual entry of trusted IP or DNS in config tab  
  - Provide warnings or tooltips

- [ ] **7. Add Nostr message preview/test utility**  
  - User can send themselves a test DM or view sample note  
  - Nice-to-have for privacy verification before alerts go live

- [x] **8. Add “Last Checked” timestamp + manual re-check button**  
  - Visible timestamp under status  
  - Force-refresh logic without full page reload

- [ ] **9. Add toggle for Nostr alerts in config UI**  
  - On/off switch for sending Nostr DMs  
  - Persisted in `config.yml`

- [x] **10. Scheduled re-checking using `check_interval_seconds`**  
  - Repeat leak checks in background  
  - Configurable interval with optional dashboard hint

- [ ] **11. Nostr/relay error detection**  
  - Show alert or warning if DMs fail to send  
  - Detect common relay disconnects or auth errors

- [ ] **12. Simple log viewer + export button**  
  - Show recent check history on a new tab or below dashboard  
  - Optional CSV/JSON export

- [ ] **13. Gamified Privacy Score / “Meatbag Score”**  
  - Color-coded score based on how well the user is locked down  
  - Add humor levels: “Fully Cloaked”, “Leaky Meatbag”, etc.

- [ ] **14. Mobile Dashboard PWA**  
  - Read-only dashboard with leak status  
  - Optional notification support  
  - Nice-to-have for mobile accessibility

- [ ] **15. DNS Leak Checker using `leakymeatbag.com`**  
  - Build custom backend that detects which DNS servers actually resolve  
  - Add result to dashboard ("Leak-free" vs "Meatbag exposed")  
  - Possibly auto-check from frontend (JS beacon)

- [ ] **16. PWA installable app support for phones**  
  - Add `manifest.json` and `service-worker.js`  
  - Allow users to install the app to their phone  
  - Optional offline access and notification support
