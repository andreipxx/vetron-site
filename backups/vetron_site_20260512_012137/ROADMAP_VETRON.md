# VETRON — ROADMAP COMPLET DE LA ZERO
## Performance Intelligence for Bolt Drivers (Romania)

**Brand:** VETRON
**Company:** GO PAMPA S.R.L., Baia Mare
**Fondator:** Andrei
**Data:** 12 Mai 2026
**Estimare lansare comerciala:** August 2026

---

## STAREA CURENTA

| Ce exista | Status |
|-----------|--------|
| APK functional (overlay + tracker + 6 filtre + Google Routes) | Build #16 pe EAS |
| Site vitrina `Vetron/index.html` (calculator, planuri, FAQ) | 80% gata |
| Pagini `gdpr.html`, `termeni.html`, `contact.html` | Schelet, de completat |
| `favicon.svg`, `robots.txt`, `sitemap.xml` | Existente |
| Licente hardcoded offline | Functional, nu scaleaza |

---

## FAZA 1 — SITE COMPLET + DEPLOY (Saptamana 1-2)
**Prioritate: CRITICA** — necesar pt Play Store + prezenta online

### 1.1 Finalizare pagini site

| # | Task | Detalii | Status |
|---|------|---------|--------|
| 1.1.1 | Refactor `index.html` | Inlocuieste "DriverPowerRO" peste tot cu "VETRON", curata referinte vechi | ❌ |
| 1.1.2 | `gdpr.html` complet | Privacy Policy GDPR Romania: date locale, Accessibility Service, Google Routes, drepturi, contact DPO | ❌ |
| 1.1.3 | `termeni.html` complet | T&C: descriere serviciu, eligibilitate 18+, planuri/preturi, rambursare 14 zile, limitare raspundere, lege RO | ❌ |
| 1.1.4 | `contact.html` complet | Email, WhatsApp, formular simplu (nume + tip serviciu + mesaj) | ❌ |
| 1.1.5 | Pagina `instalare.html` | Ghid pas-cu-pas: cum instalezi APK, cum activezi "surse necunoscute", cum activezi Accessibility | ❌ |
| 1.1.6 | OG Image | 1200x630px pentru share Facebook/WhatsApp | ❌ |

### 1.2 SEO basics

| # | Task | Status |
|---|------|--------|
| 1.2.1 | `robots.txt` — allow all | ✅ exista |
| 1.2.2 | `sitemap.xml` — update cu toate paginile | ❌ |
| 1.2.3 | Meta tags OG complete pe toate paginile | ❌ |
| 1.2.4 | `favicon.svg` — V verde pe negru | ✅ exista |

### 1.3 Deploy site

| # | Task | Status |
|---|------|--------|
| 1.3.1 | Init git repo in `Vetron/` | ❌ |
| 1.3.2 | Creare repo GitHub: `vetron` sau `vetron-site` | ❌ |
| 1.3.3 | Push toate fisierele | ❌ |
| 1.3.4 | Activare GitHub Pages (branch main, folder /) | ❌ |
| 1.3.5 | Test pe mobil + desktop | ❌ |
| 1.3.6 | (Optional) Domeniu `vetron.ro` — ~50 RON/an la RoTLD | ❌ |

### 1.4 APK download link

| # | Task | Status |
|---|------|--------|
| 1.4.1 | Host APK Build #16 pe GitHub Releases | ❌ |
| 1.4.2 | Link real "DESCARCA APK" in `index.html` | ❌ |
| 1.4.3 | Pagina `instalare.html` cu screenshots | ❌ |

---

## FAZA 2 — REBRAND APK: DriverPowerRO → VETRON (Saptamana 2-3)
**Prioritate: MARE** — inainte de Play Store

| # | Task | Detalii | Status |
|---|------|---------|--------|
| 2.1 | `app.json` / `app.config.js` | Schimba name/slug "DriverPowerRO" → "VETRON" | ❌ |
| 2.2 | Package name Android | Decide: pastram `com.driverpowerro` sau `ro.vetron.app` (app noua pe Play Store) | ❌ |
| 2.3 | Icon app | Logo VETRON (V verde pe negru), adaptive icon Android 512x512 | ❌ |
| 2.4 | Splash screen | Logo VETRON pe fundal #0A0E0B | ❌ |
| 2.5 | UI text | Inlocuieste orice "DriverPower" in ecrane | ❌ |
| 2.6 | Overlay branding | Daca apare "DP" → "V" sau logo VETRON | ❌ |
| 2.7 | Onboarding wizard | 3 ecrane: Bun venit + Setari masina + Activare Accessibility | ❌ |
| 2.8 | Privacy Policy in-app | Link in Settings → site VETRON `/gdpr.html` | ❌ |
| 2.9 | EAS build preview | Test APK rebrandat pe S23 | ❌ |
| 2.10 | EAS build production | AAB pentru Play Store | ❌ |

---

## FAZA 3 — AUTH + CONT USER (Saptamana 3-5)
**Prioritate: MARE** — necesar pentru plati + scalare licente

### 3.1 Backend — Supabase

| # | Task | Status |
|---|------|--------|
| 3.1.1 | Creare proiect Supabase (free tier, EU region pt GDPR) | ❌ |
| 3.1.2 | Auth: Email + Password | ❌ |
| 3.1.3 | (Optional) Google OAuth | ❌ |
| 3.1.4 | Tabel `users` — id, email, plan, plan_expires_at, created_at | ❌ |
| 3.1.5 | Tabel `device_activations` — user_id, device_id, activated_at | ❌ |
| 3.1.6 | Row Level Security (RLS) | ❌ |
| 3.1.7 | Edge Function: `verify-license` | ❌ |

### 3.2 Ecrane noi APK

| # | Task | Status |
|---|------|--------|
| 3.2.1 | `WelcomeScreen` — logo VETRON + LOGIN / REGISTER | ❌ |
| 3.2.2 | `RegisterScreen` — email + parola + confirm + accept TOS | ❌ |
| 3.2.3 | `LoginScreen` refactor — email + parola + Google + "Am uitat parola" | ❌ |
| 3.2.4 | `VerifyEmailScreen` — confirmare email | ❌ |
| 3.2.5 | `ForgotPasswordScreen` — reset link | ❌ |
| 3.2.6 | `AccountScreen` (Settings) — email, plan, butoane: Schimba parola / Sterge cont / Logout | ❌ |

### 3.3 Securitate

| # | Task | Status |
|---|------|--------|
| 3.3.1 | `expo-secure-store` — JWT in Android Keystore | ❌ |
| 3.3.2 | Auto-refresh token | ❌ |
| 3.3.3 | Logout = sterge tokens + invalidate session | ❌ |
| 3.3.4 | "Sterge cont" → DELETE user + date | ❌ |
| 3.3.5 | Rate limiting Supabase | ❌ |

### 3.4 Migrare licente vechi

| # | Task | Status |
|---|------|--------|
| 3.4.1 | La first login, licenta hardcoded → migreaza in DB | ❌ |
| 3.4.2 | `DPR-ROOT-ANDR-2026` → PRO lifetime in DB | ❌ |

---

## FAZA 4 — GOOGLE PLAY STORE (Saptamana 5-7)
**Prioritate: MARE**

### 4.1 Cont developer

| # | Task | Cost | Status |
|---|------|------|--------|
| 4.1.1 | Google Play Console — cont developer | $25 | ❌ |
| 4.1.2 | Verificare identitate firma GO PAMPA S.R.L. | 0 | ❌ |
| 4.1.3 | DUNS Number (daca Google cere) | 0, 5-7 zile | ❌ |

### 4.2 Assets listing

| # | Asset | Spec | Status |
|---|-------|------|--------|
| 4.2.1 | App icon | 512x512 PNG, fara transparenta | ❌ |
| 4.2.2 | Feature graphic | 1024x500 PNG | ❌ |
| 4.2.3 | Screenshots | min 2, max 8, 16:9 sau 9:16 | ❌ |
| 4.2.4 | Descriere scurta | max 80 chars | ❌ |
| 4.2.5 | Descriere lunga | max 4000 chars | ❌ |
| 4.2.6 | Categoria | Finance sau Tools | ❌ |

### 4.3 Compliance

| # | Task | Status |
|---|------|--------|
| 4.3.1 | Privacy Policy URL → vetron site `/gdpr.html` | ❌ |
| 4.3.2 | Data Safety form | ❌ |
| 4.3.3 | Accessibility Service disclosure — justificare scrisa | ❌ |
| 4.3.4 | Target API 34+ (Android 14) | ❌ |

### 4.4 Release tracks

| # | Track | Durata | Status |
|---|-------|--------|--------|
| 4.4.1 | Internal testing (5-10 gmail) | 2-3 zile | ❌ |
| 4.4.2 | Closed testing (20-100 soferi Bolt) | 7 zile | ❌ |
| 4.4.3 | Production release | — | ❌ |

---

## FAZA 5 — SISTEM PLATI (Saptamana 7-9)
**Prioritate: CRITICA** — monetizare

### 5.1 Stripe (plati web directe)

| # | Task | Status |
|---|------|--------|
| 5.1.1 | Cont Stripe cu GO PAMPA S.R.L. | ❌ |
| 5.1.2 | Produse: Simplu 15 RON/luna, PRO 25 RON/luna | ❌ |
| 5.1.3 | Stripe Checkout session | ❌ |
| 5.1.4 | Webhook → Supabase Edge Function: update plan | ❌ |
| 5.1.5 | Customer Portal (manage subscription) | ❌ |
| 5.1.6 | Stripe Coupons (coduri promo early adopters) | ❌ |

### 5.2 Google Play Billing (in-app purchases)

| # | Task | Status |
|---|------|--------|
| 5.2.1 | `react-native-iap` sau `expo-in-app-purchases` | ❌ |
| 5.2.2 | Subscriptions in Play Console: Simplu + PRO | ❌ |
| 5.2.3 | Flow cumparare in-app | ❌ |
| 5.2.4 | RTDN → Supabase Edge Function: sync plan | ❌ |
| 5.2.5 | Restore purchases la reinstalare | ❌ |

### 5.3 Comisioane

| Canal | Comision | Net din 25 RON PRO |
|-------|----------|---------------------|
| Stripe (web) | 1.5% + 0.25 EUR | ~23.40 RON |
| Google Play | 15% (sub $1M/an) | ~21.25 RON |
| Transfer bancar | 0% | 25.00 RON |

---

## FAZA 6 — LEGAL & COMPLIANCE (paralel cu fazele 3-5)
**Prioritate: OBLIGATORIU inainte de lansare publica**

### 6.1 CAEN GO PAMPA S.R.L.

| # | Task | Cost | Status |
|---|------|------|--------|
| 6.1.1 | Adauga CAEN 6201 (principal) — software la comanda | ~107 RON total | ❌ |
| 6.1.2 | Adauga CAEN 5829 (secundar) — editare software | inclus | ❌ |
| 6.1.3 | Adauga CAEN 4791 (secundar) — comert online | inclus | ❌ |
| 6.1.4 | Decizia Asociatului Unic + Act aditional | ❌ |
| 6.1.5 | Depunere portal.onrc.ro | ❌ |
| 6.1.6 | Aprobare 3-5 zile lucratoare | ❌ |

### 6.2 GDPR

| # | Task | Status |
|---|------|--------|
| 6.2.1 | Privacy Policy pe site (gdpr.html) | ❌ de completat |
| 6.2.2 | In-app Privacy Policy link | ❌ |
| 6.2.3 | Consimtamant explicit la Register | ❌ |
| 6.2.4 | Drept la stergere — buton functional | ❌ |
| 6.2.5 | Drept la export — JSON/PDF | ❌ |

### 6.3 ANSPDCP

| # | Task | Status |
|---|------|--------|
| 6.3.1 | Notificare prelucrare date | ❌ |
| 6.3.2 | Registru prelucrari (document intern) | ❌ |

### 6.4 OSIM — Marca VETRON

| # | Task | Cost | Status |
|---|------|------|--------|
| 6.4.1 | Verificare "VETRON" pe osim.ro | gratuit | ❌ |
| 6.4.2 | Verificare EUIPO (marca UE) | gratuit | ❌ |
| 6.4.3 | Depunere cerere OSIM — clasa 9 + 42 | ~450 RON | ❌ |
| 6.4.4 | Examinare: 6-12 luni | ❌ |

### 6.5 Fiscal

| # | Task | Status |
|---|------|--------|
| 6.5.1 | Facturare: SmartBill/FGO + Stripe webhook | ❌ |
| 6.5.2 | TVA: verifica daca GO PAMPA e platitor | ❌ |

---

## FAZA 7 — FEATURES NOI APK (Saptamana 8-10)
**Prioritate: MEDIE** — imbunatatiri post-lansare

| # | Feature | Prioritate | Status |
|---|---------|-----------|--------|
| 7.1 | Daily Goal + progress bar HomeScreen | MARE | ❌ |
| 7.2 | Export PDF raport lunar | MARE | ❌ |
| 7.3 | Notificare sumar seara (21:00) | MEDIE | ❌ |
| 7.4 | Widget Android 4x2 (stats pe home screen) | MEDIE | ❌ |
| 7.5 | Tracker cheltuieli (service, parcare, spalatorie) | MEDIE | ❌ |
| 7.6 | Grafice bar chart saptamanal/lunar | MEDIE | ❌ |
| 7.7 | Dark/Light mode toggle | MICA | ❌ |

---

## FAZA 8 — MARKETING & LANSARE (paralel cu Faza 4+)
**Prioritate: CRESTE dupa lansare**

### Pre-lansare
| # | Task | Status |
|---|------|--------|
| 8.1.1 | Pagina "Coming Soon" cu email signup | ❌ |
| 8.1.2 | Grupuri Facebook soferi Bolt Romania | ❌ |
| 8.1.3 | 10-20 beta testeri din Baia Mare | ❌ |
| 8.1.4 | Video demo TikTok/Reels — 30s in masina | ❌ |

### Lansare
| # | Task | Status |
|---|------|--------|
| 8.2.1 | Post in grupuri FB Bolt (Cluj, Bucuresti, Timisoara, Iasi, BM) | ❌ |
| 8.2.2 | Cod promo "BOLT50" — 50% prima luna | ❌ |
| 8.2.3 | Referral: invita prieten → 1 luna gratis ambii | ❌ |

### Post-lansare
| # | Task | Status |
|---|------|--------|
| 8.3.1 | Colecteaza review-uri Play Store (min 10) | ❌ |
| 8.3.2 | Blog SEO pe site | ❌ |
| 8.3.3 | Support WhatsApp Business | ❌ |

---

## FAZA 9 — SCALARE (3-6 luni post-lansare)

| # | Feature |
|---|---------|
| 9.1 | Suport Uber Romania (parser #2) |
| 9.2 | Suport FreeNow (parser #3) |
| 9.3 | Heat map zone profitabile |
| 9.4 | Notificari push zilnice |
| 9.5 | Export raport PDF lunar |
| 9.6 | Widget Android |
| 9.7 | iOS (daca cererea exista) |
| 9.8 | Dashboard web |
| 9.9 | AI Insights |
| 9.10 | Traducere engleza + extindere: BG, HU, PL |

---

## TIMELINE ESTIMATA

```
MAI 2026 — Saptamana 1-2
├── FAZA 1: Site complet + deploy GitHub Pages
├── FAZA 6.1: Start procedura CAEN (paralel)
└── FAZA 6.4: Depunere marca OSIM (paralel)

IUNIE 2026 — Saptamana 3-6
├── FAZA 2: Rebrand APK → VETRON
├── FAZA 3: Auth Supabase (login/register)
└── FAZA 6.2-6.3: GDPR + ANSPDCP

IULIE 2026 — Saptamana 7-10
├── FAZA 4: Google Play Store (internal + closed testing)
├── FAZA 5: Stripe + Google Play Billing
├── FAZA 7: Features noi APK
└── FAZA 8.1: Pre-lansare marketing

AUGUST 2026 — Saptamana 11-13
├── FAZA 4.4.3: Production release Play Store
├── FAZA 8.2: Lansare publica + promo
└── FAZA 6.5: Facturare automata

SEPTEMBRIE+ 2026
└── FAZA 9: Scalare + features noi
```

---

## COSTURI ESTIMATE

| Item | Cost | Recurent |
|------|------|----------|
| GitHub Pages hosting | GRATUIT | — |
| Supabase (free tier) | GRATUIT | lunar |
| Google Play Console | $25 (~115 RON) | one-time |
| Domeniu vetron.ro (optional) | ~50 RON/an | anual |
| CAEN schimbare ONRC | ~107 RON | one-time |
| OSIM marca nationala | ~450 RON | one-time (10 ani) |
| Stripe | 1.5% + 0.25 EUR/tranzactie | per plata |
| Google Play | 15% din subscriptions | per plata |
| Google Routes API | $5/1000 req (free $200/luna) | lunar |
| SmartBill facturare (optional) | ~25 RON/luna | lunar |
| **TOTAL START** | **~750 RON** | — |
| **TOTAL LUNAR (dupa lansare)** | **~25-50 RON** (pana la profit) | — |

---

## RISCURI SI SOLUTII

| Risc | Impact | Solutie |
|------|--------|---------|
| Google respinge app pt AccessibilityService | CRITIC | Justificare scrisa clara + apel. Alternativa: sideload APK |
| Bolt schimba UI → parser stricat | MARE | Monitorizare zilnica, update rapid. Accessibility text e stabil |
| "VETRON" deja inregistrat la OSIM | MEDIU | Verifica OSIM+EUIPO inainte. Backup: VELTRON, DRIVTRON |
| Putini useri platitori | MEDIU | Trial generos, pret mic (15 RON), marketing nisa |
| GDPR complaint | MIC | Zero date server (momentan). Dupa Supabase: RLS + sterge cont |

---

*ROADMAP generat 12 Mai 2026 — VETRON by GO PAMPA S.R.L.*
*Ultima actualizare: 12 Mai 2026*
