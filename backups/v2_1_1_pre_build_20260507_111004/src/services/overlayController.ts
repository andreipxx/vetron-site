// Build 15.2 overlay controller: decoupled show from getRoute (immediate render).
//   - Overlay appears IMMEDIATELY with fallback estimate
//   - getRoute fires in background; if it returns, overlay re-renders with API data
//   - Entire handler wrapped in try-catch with structured event logging
//   - Debug events visible in AccessibilityTestScreen

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Accessibility, type AccessibilityCapture } from '../native/accessibility';
import { Overlay, type OverlayMode } from '../native/overlay';
import { parseBoltRide } from './boltParser';
import { analyzeRide } from './profitCalculator';
import { feedScreen } from './rideStateMachine';
import { getFuelSettings, getProOverrides, getDailyGoal } from './userSettings';
import { getStatsForPeriod } from './tracker';
import { getRoute } from './routesApi';
import { loadFilters } from './filterEngine';
import { addRide, updateRide, generateRideId, detectLifecycleEvent } from './tracker';
import { trackPackageSeen } from './platformDetector';
import { VERDICT_DISPLAY } from '../types';
import { logDpEvent } from './dpDebug';
import type { PlanTier, Ride, RouteSource } from '../types';

const OVERLAY_MODE_KEY = '@dp_overlay_mode_pro';
const STICKY_MS = 15000;

export async function getOverlayModePro(): Promise<OverlayMode> {
  const v = await AsyncStorage.getItem(OVERLAY_MODE_KEY);
  return v === 'full' ? 'full' : 'simple';
}
export async function setOverlayModePro(m: OverlayMode): Promise<void> {
  await AsyncStorage.setItem(OVERLAY_MODE_KEY, m);
  try {
    const { NativeModules } = require('react-native');
    if (NativeModules.DPAccessibility?.syncOverlayMode) {
      await NativeModules.DPAccessibility.syncOverlayMode(m);
    }
  } catch {}
}

let lastShownKey = '';
let lastLoggedScreen = '';
let lastOfferRideId: string | null = null;  // tracks current offer for lifecycle updates
let lastLifecycle: string = '';             // dedupes lifecycle events
let lastShownAt = 0;
let stickyTimer: ReturnType<typeof setTimeout> | null = null;
let listenerStop: (() => void) | null = null;

function modeForPlan(plan: PlanTier, proPref: OverlayMode): OverlayMode {
  if (plan === 'pro') return proPref;
  return 'simple';
}

function buildOverlayPayload(parsed: any, a: any, mode: OverlayMode, label: string,
                              tripKmFromApi?: number, tripMinFromApi?: number,
                              source: 'fallback' | 'api' | 'cache' = 'fallback') {
  return {
    mode,
    verdict: a.verdict,
    label,
    pickup: parsed.pickupKm != null ? `${parsed.pickupKm} km / ${parsed.pickupMin ?? '?'} min` : '—',
    trip: tripKmFromApi != null
      ? `${tripKmFromApi} km / ${tripMinFromApi ?? '?'} min`
      : '~' + a.tripKmEstimate + ' km',
    duration: tripMinFromApi != null ? `${tripMinFromApi} min` : '—',
    gross: parsed.grossNet != null ? parsed.grossNet.toFixed(2) + ' lei' : '—',
    profitKm: a.profitPerKm.toFixed(2) + ' RON/km',
    net: a.profit > 0 ? '+' + a.profit.toFixed(2) + ' lei' : a.profit.toFixed(2) + ' lei',
    shortRide: a.shortRideFlag,
    source,
  };
}

function buildLabel(parsed: any, a: any, overrides: any): string {
  let label = VERDICT_DISPLAY[a.verdict]?.label || a.verdict.toUpperCase();
  if (a.proOverride === 'pickup_too_far' && overrides) {
    label = `Pickup ${a.pickupKm}km > ${overrides.maxPickupKm}km — REFUZĂ`;
  } else if (a.proOverride === 'rating_too_low' && overrides) {
    label = `Rating ${parsed.passengerRating} < ${overrides.minPassengerRating} — REFUZĂ`;
  }
  return label;
}

function buildKey(parsed: any, a: any): string {
  return `${parsed.grossNet}|${Math.round((parsed.pickupKm ?? 0) * 2) / 2}|${a.verdict}|${a.proOverride ?? ''}|${parsed.paymentMethod ?? ''}`;
}

export async function startOverlayController(plan: PlanTier): Promise<void> {
  if (listenerStop) listenerStop();

  // mode is read fresh per offer below (so toggle changes apply immediately)
  logDpEvent('CTRL_START', { plan, mode: 'dynamic' });

  Accessibility.startListening();
  // Foreground service keeps the JS process alive while DriverPower is minimized
  // and shows the persistent "DP" badge over Bolt as a visual confirmation.
  Accessibility.startLifeService().catch(() => {});

  const handler = async (cap: AccessibilityCapture) => {
    if (!cap || !cap.text) return;
      try { trackPackageSeen(cap.package); } catch {}
    // Log non-Bolt captures briefly so we know if Uber/other is hijacking
    if (cap.package !== 'ee.mtakso.driver') {
      // Log only every 20th non-bolt capture to avoid noise
      if (Math.random() < 0.05) logDpEvent('CAP_SKIP', cap.package);
      return;
    }

    try { await feedScreen(cap.text); } catch (e: any) { logDpEvent('FEED_ERR', String(e?.message || e)); }

    const parsed = parseBoltRide(cap.text);
    if (parsed.screen !== lastLoggedScreen) {
      logDpEvent('CAP_BOLT', { screen: parsed.screen, len: cap.text.length });
      lastLoggedScreen = parsed.screen;
    }

    // === LIFECYCLE DETECTION (auto-tracker) ===
    // Updates the last shown ride based on Bolt screen markers
    try {
      const lifecycle = detectLifecycleEvent(cap.text);
      if (lifecycle !== 'unknown' && lifecycle !== lastLifecycle) {
        lastLifecycle = lifecycle;
        if (lastOfferRideId) {
          if (lifecycle === 'accepted') {
            await updateRide(lastOfferRideId, { accepted: true });
            logDpEvent('TRACKER_ACCEPT', lastOfferRideId.slice(-8));
          } else if (lifecycle === 'completed') {
            await updateRide(lastOfferRideId, { completed: true, completedAt: Date.now() });
            logDpEvent('TRACKER_DONE', lastOfferRideId.slice(-8));
            lastOfferRideId = null; // reset for next offer
          }
        }
      }
    } catch (e: any) {
      logDpEvent('LIFECYCLE_ERR', String(e?.message || e).slice(0, 60));
    }

    if (parsed.screen === 'ride_offer') {
      try {
        logDpEvent('OFFER', {
          net: parsed.grossNet, pickupKm: parsed.pickupKm,
          rating: parsed.passengerRating, payment: parsed.paymentMethod,
        });

        if (parsed.grossNet == null) { logDpEvent('SKIP', 'no_grossNet'); return; }

        let fuel: any, overrides: any, filters: any, dailyGoal: number, todayEarnings: number;
        try {
          [fuel, filters] = await Promise.all([getFuelSettings(), loadFilters()]);
          // Build 17: proOverrides moved into filterEngine as maxPickupKm + minRating filters.
          overrides = undefined;
          const [goal, todayStats] = await Promise.all([getDailyGoal(), getStatsForPeriod('today')]);
          dailyGoal = goal;
          todayEarnings = todayStats.earningsLei;
        } catch (e: any) { logDpEvent('SETTINGS_ERR', String(e?.message || e)); return; }

        // FIRST PASS: analyze with fallback estimate (no Routes API)
        const a1 = analyzeRide(parsed, { fuel, plan, proOverrides: overrides, filters });
        const dailyProgressStr = dailyGoal > 0
          ? `${Math.round(todayEarnings)}/${dailyGoal} lei`
          : undefined;
        if (!a1) { logDpEvent('SKIP', 'analyze_null'); return; }

        const label1 = buildLabel(parsed, a1, overrides);
        const key1 = buildKey(parsed, a1);

        if (key1 === lastShownKey) { logDpEvent('SKIP', 'dedupe'); return; }
        lastShownKey = key1;
        lastShownAt = Date.now();
        if (stickyTimer) { clearTimeout(stickyTimer); stickyTimer = null; }

        // Start route lookup early; reuse promise in second pass — no duplicate API call
        const canFetchRoute = plan === 'pro' && !!parsed.pickupAddress && !!parsed.destinationAddress;
        const routePromise = canFetchRoute
          ? getRoute(parsed.pickupAddress!, parsed.destinationAddress!)
          : Promise.resolve<null>(null);

        // 500ms budget: cache hit resolves instantly, fresh miss times out → fallback shown
        const preRoute = await Promise.race([
          routePromise,
          new Promise<null>(r => setTimeout(() => r(null), 500)),
        ]);

        const aFinal = preRoute
          ? (analyzeRide(parsed, { fuel, plan, proOverrides: overrides, filters,
              tripKmFromApi: preRoute.distanceKm, tripMinFromApi: preRoute.durationMin }) ?? a1)
          : a1;
        const labelFinal = preRoute ? buildLabel(parsed, aFinal, overrides) : label1;

        const proPrefNow = await getOverlayModePro();
        const mode = modeForPlan(plan, proPrefNow);
        try {
          const payload = {
            ...buildOverlayPayload(parsed, aFinal, mode, labelFinal,
              preRoute?.distanceKm, preRoute?.durationMin, preRoute?.source ?? 'fallback'),
            dailyProgress: dailyProgressStr,
          };
          await Overlay.show(payload);
          logDpEvent('SHOW_OK', { verdict: aFinal.verdict, ppkm: aFinal.profitPerKm,
            src: preRoute?.source ?? 'fallback' });

          try {
            const ts = Date.now();
            const rideId = generateRideId(ts, parsed.grossNet || 0);
            const ride: Ride = {
              id: rideId,
              timestamp: ts,
              pickupKm: aFinal.pickupKm,
              tripKm: preRoute ? preRoute.distanceKm : aFinal.tripKmEstimate,
              durationMin: preRoute ? preRoute.durationMin : aFinal.totalMinutes,
              grossEarnings: parsed.grossNet || 0,
              netEarnings: aFinal.netAfterTax,
              paymentMethod: parsed.paymentMethod || 'card',
              passengerRating: parsed.passengerRating || 5.0,
              profitPerKm: aFinal.profitPerKm,
              profitNet: aFinal.profit,
              verdict: aFinal.verdict,
              source: (preRoute?.source ?? 'fallback') as RouteSource,
              pickupAddress: parsed.pickupAddress,
              destinationAddress: parsed.destinationAddress,
              accepted: false,
              completed: false,
            };
            await addRide(ride);
            lastOfferRideId = rideId;
            logDpEvent('TRACKER_NEW', { id: rideId.slice(-8), ppkm: aFinal.profitPerKm,
              src: ride.source });
          } catch (e: any) {
            logDpEvent('TRACKER_ERR', String(e?.message || e).slice(0, 60));
          }
        } catch (e: any) {
          logDpEvent('SHOW_ERR', String(e?.message || e));
          return;
        }

        // Second pass only if first pass used fallback — reuses routePromise (no new API call)
        if (!preRoute && canFetchRoute) {
          const capturedRideId = lastOfferRideId;
          (async () => {
            try {
              const route = await routePromise;
              if (!route) { logDpEvent('API_NULL'); return; }
              const a2 = analyzeRide(parsed, {
                fuel, plan, proOverrides: overrides, filters,
                tripKmFromApi: route.distanceKm, tripMinFromApi: route.durationMin,
              });
              if (!a2) return;
              const label2 = buildLabel(parsed, a2, overrides);
              const payload2 = {
                ...buildOverlayPayload(parsed, a2, mode, label2,
                  route.distanceKm, route.durationMin, route.source),
                dailyProgress: dailyProgressStr,
              };
              await Overlay.show(payload2);
              lastShownKey = buildKey(parsed, a2);
              // Re-log SHOW_OK so the JSONL trace reflects the API-backed verdict
              // (without this, the only SHOW_OK in the log is the fallback one).
              logDpEvent('SHOW_OK', { verdict: a2.verdict, ppkm: a2.profitPerKm, src: route.source });
              logDpEvent('UPDATE_API', { verdict: a2.verdict, km: route.distanceKm });
              if (capturedRideId) {
                await updateRide(capturedRideId, {
                  tripKm: route.distanceKm,
                  durationMin: route.durationMin,
                  source: route.source,
                  profitPerKm: a2.profitPerKm,
                  profitNet: a2.profit,
                  verdict: a2.verdict,
                  netEarnings: a2.netAfterTax,
                });
                logDpEvent('TRACKER_UPD', { km: route.distanceKm, ppkm: a2.profitPerKm, src: route.source });
              }
            } catch (e: any) {
              logDpEvent('API_ERR', String(e?.message || e));
            }
          })();
        }
      } catch (e: any) {
        logDpEvent('HANDLER_ERR', String(e?.message || e));
      }
    } else {
      // ANY non-offer screen → sticky always (no instant hide)
      // Overlay stays for STICKY_MS after lastShownAt, regardless of what Bolt is showing now
      if (lastShownAt > 0 && !stickyTimer) {
        const showAge = Date.now() - lastShownAt;
        const remaining = Math.max(0, STICKY_MS - showAge);
        stickyTimer = setTimeout(() => {
          lastShownKey = '';
          lastShownAt = 0;
          try { Overlay.hide(); } catch {}
          stickyTimer = null;
        }, remaining);
      }
    }
  };

  const unsub = Accessibility.addCaptureListener(handler);
  listenerStop = () => {
    unsub();
    if (stickyTimer) { clearTimeout(stickyTimer); stickyTimer = null; }
    try { Overlay.hide(); } catch {}
    Accessibility.stopListening();
    Accessibility.stopLifeService().catch(() => {});
    listenerStop = null;
    logDpEvent('CTRL_STOP');
  };
}

export function stopOverlayController(): void {
  if (listenerStop) listenerStop();
}
