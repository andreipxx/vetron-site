import React, { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, SafeAreaView,
  ScrollView, AppState, Platform, Alert, Share,
} from 'react-native';
import { useTheme } from '../hooks/useTheme';
import { Accessibility, type AccessibilityCapture } from '../native/accessibility';
import { parseBoltRide } from '../services/boltParser';
import { analyzeRide } from '../services/profitCalculator';
import { getLicenseState } from '../services/licenseManager';
import { getFuelSettings, getProOverrides, type FuelSettings, type ProOverrides } from '../services/userSettings';
import { VERDICT_DISPLAY } from '../types';
import { getDpEvents, clearDpEvents, getDebugStats, exportAsJsonl } from '../services/dpDebug';

interface Props { onBack: () => void; }

export default function AccessibilityTestScreen({ onBack }: Props) {
  const { colors } = useTheme();
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [capture, setCapture] = useState<AccessibilityCapture | null>(null);
  const [licInfo, setLicInfo] = useState<{ plan: string; ridesUsed: number; ridesRemaining: number | null; expiresAt: number | null } | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [debugEvents, setDebugEvents] = useState<string[]>([]);
  const [debugStats, setDebugStats] = useState<ReturnType<typeof getDebugStats> | null>(null);

  useEffect(() => {
    const refresh = () => { setDebugEvents(getDpEvents()); setDebugStats(getDebugStats()); };
    refresh();
    const i = setInterval(refresh, 1000);
    return () => clearInterval(i);
  }, []);

  const refreshStatus = useCallback(async () => {
    setEnabled(await Accessibility.isEnabled());
    const st = await getLicenseState();
    if (st.license) {
      setLicInfo({ plan: st.license.plan, ridesUsed: st.ridesUsed, ridesRemaining: st.ridesRemaining, expiresAt: st.license.expiresAt });
    }
  }, []);

  const refreshCapture = useCallback(async () => {
    const c = await Accessibility.getLastCapture();
    if (c && c.timestamp > 0) setCapture(c);
  }, []);

  useEffect(() => {
    refreshStatus(); refreshCapture();
    pollingRef.current = setInterval(refreshCapture, 2000);
    const unsub = Accessibility.addCaptureListener(setCapture);
    const sub = AppState.addEventListener('change', (s) => { if (s === 'active') { refreshStatus(); refreshCapture(); } });
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      unsub();
      sub.remove();
    };
  }, [refreshStatus, refreshCapture]);

  const [fuel, setFuel] = useState<FuelSettings | null>(null);
  const [overrides, setOverrides] = useState<ProOverrides | null>(null);

  useEffect(() => {
    getFuelSettings().then(setFuel);
    getProOverrides().then(setOverrides);
  }, []);

  const parsed = useMemo(() => capture?.text ? parseBoltRide(capture.text) : null, [capture]);
  const analysis = useMemo(() => {
    if (!parsed || !fuel || !licInfo) return null;
    const plan = (licInfo.plan as any) || 'trial';
    return analyzeRide(parsed, { fuel, plan, proOverrides: plan === 'pro' ? overrides ?? undefined : undefined });
  }, [parsed, fuel, overrides, licInfo]);

  const handleOpenSettings = async () => { await Accessibility.openSettings(); };

  const handleCopyCapture = async () => {
    try { const len = await Accessibility.copyLastCapture(); Alert.alert('Copiat', `${len} caractere în clipboard.`); }
    catch (e: any) { Alert.alert('Eroare', e?.message || 'Niciun capture.'); }
  };
  const handleExportLog = async () => {
    try {
      const r = await Accessibility.copyLogToDownloads();
      const mb = (r.sizeBytes / (1024 * 1024)).toFixed(2);
      Alert.alert('Export reușit', `Salvat în Downloads:\n${r.path.split('/').pop()}\n\nMărime: ${mb} MB`);
    } catch (e: any) { Alert.alert('Eroare', e?.message || 'Export a eșuat'); }
  };
  const handleStatsLog = async () => {
    try {
      const s = await Accessibility.getLogStats();
      const mb = (s.sizeBytes / (1024 * 1024)).toFixed(2);
      Alert.alert('Log Stats', [
        s.exists ? 'Existent: DA' : 'Existent: NU',
        `Captures: ${s.captures}`,
        `Mărime: ${mb} MB`,
      ].join('\n'));
    } catch (e: any) { Alert.alert('Eroare', e?.message); }
  };
  const handleClearLog = () => {
    Alert.alert('Șterge log', 'Sigur?', [
      { text: 'Anulează', style: 'cancel' },
      { text: 'Șterge', style: 'destructive', onPress: async () => {
        try { await Accessibility.clearLog(); Alert.alert('Gata', 'Log golit.'); }
        catch (e: any) { Alert.alert('Eroare', e?.message); }
      }}
    ]);
  };

  const available = Accessibility.isAvailable();

  return (
    <SafeAreaView style={[s.container, { backgroundColor: colors.bg }]}>
      <TouchableOpacity onPress={onBack} style={s.backBtn} activeOpacity={0.6}>
        <Text style={[s.backText, { color: colors.accent }]}>‹ Back</Text>
      </TouchableOpacity>

      <ScrollView contentContainerStyle={s.scroll}>
        <Text style={[s.title, { color: colors.text }]}>Accessibility Test</Text>

        {licInfo && (
          <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <Text style={[s.cardLabel, { color: colors.textTertiary }]}>PLAN ACTIV</Text>
            <Row label="Plan" value={licInfo.plan.toUpperCase()} colors={colors} valueColor={colors.accent} />
            {licInfo.ridesRemaining != null && (
              <Row label="Curse rămase" value={`${licInfo.ridesRemaining} (folosite ${licInfo.ridesUsed})`} colors={colors} />
            )}
            {licInfo.expiresAt != null && (
              <Row label="Expiră" value={new Date(licInfo.expiresAt).toLocaleString('ro-RO')} colors={colors} />
            )}
          </View>
        )}

        <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Text style={[s.cardLabel, { color: colors.textTertiary }]}>STATUS</Text>
          <Row label="Platform" value={Platform.OS} colors={colors} />
          <Row label="Native module" value={available ? 'detected ✓' : 'missing ✗'} colors={colors} valueColor={available ? colors.bun : colors.critic} />
          <Row label="Service enabled" value={enabled === null ? '...' : enabled ? 'YES ✓' : 'NO'} colors={colors} valueColor={enabled ? colors.bun : colors.critic} />
        </View>

        {!enabled && available && (
          <TouchableOpacity onPress={handleOpenSettings} style={[s.btn, { backgroundColor: colors.accent }]} activeOpacity={0.7}>
            <Text style={s.btnText}>Deschide Settings Accessibility</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity onPress={() => { refreshStatus(); refreshCapture(); }} style={[s.btnSecondary, { borderColor: colors.border }]} activeOpacity={0.7}>
          <Text style={[s.btnSecondaryText, { color: colors.text }]}>Reîmprospătează</Text>
        </TouchableOpacity>

        <View style={s.debugRow}>
          <DebugBtn onPress={handleCopyCapture}    text="📋"        colors={colors} />
          <DebugBtn onPress={handleStatsLog}       text="📊 Stats"  colors={colors} />
          <DebugBtn onPress={handleExportLog}      text="📤 Export" colors={colors} />
          <DebugBtn onPress={handleClearLog}       text="🗑"        colors={colors} danger />
        </View>

        {analysis && parsed?.screen === 'ride_offer' && (
          <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors[analysis.verdict], borderWidth: 2, marginTop: 20 }]}>
            <Text style={[s.cardLabel, { color: colors.textTertiary }]}>ANALIZĂ PROFIT (preview)</Text>
            <Text style={[s.verdictBig, { color: colors[analysis.verdict] }]}>
              {VERDICT_DISPLAY[analysis.verdict].emoji} {VERDICT_DISPLAY[analysis.verdict].label}
            </Text>
            <Row label="Profit/km" value={`${analysis.profitPerKm.toFixed(2)} RON/km`} colors={colors} valueColor={colors[analysis.verdict]} />
            <Row label="Profit total" value={`${analysis.profit.toFixed(2)} RON`} colors={colors} />
            <Row label="Net după taxe" value={`${analysis.netAfterTax.toFixed(2)} RON`} colors={colors} />
            <Row label="Cost mașină" value={`${analysis.vehicleCost.toFixed(2)} RON`} colors={colors} />
            <Row label="Total km est." value={`${analysis.totalKm.toFixed(1)} km`} colors={colors} />
            {analysis.isExternalRide && <Row label="Tip cursă" value="EXTERNĂ (+25%)" colors={colors} valueColor={colors.accent} />}
            {analysis.confidence === 'low' && (
              <Text style={[s.warn, { color: colors.decide }]}>⚠ Date parțiale — pickup km lipsesc, am estimat 1.0 km</Text>
            )}
          </View>
        )}

        {parsed && (
          <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.border, marginTop: 20 }]}>
            <Text style={[s.cardLabel, { color: colors.textTertiary }]}>DATE PARSATE</Text>
            <Row label="Ecran detectat" value={parsed.screen} colors={colors} valueColor={colors.accent} />
            <Row label="Preț NET" value={parsed.grossNet != null ? `${parsed.grossNet} lei` : '—'} colors={colors} />
            <Row label="Pickup km" value={parsed.pickupKm != null ? `${parsed.pickupKm} km` : '—'} colors={colors} />
            <Row label="Pickup min" value={parsed.pickupMin != null ? `${parsed.pickupMin} min` : '—'} colors={colors} />
            <Row label="Pasager" value={parsed.passengerName ?? '—'} colors={colors} />
            <Row label="Rating pasager" value={parsed.passengerRating != null ? `${parsed.passengerRating} ★` : '—'} colors={colors} />
            <Row label="Surge" value={parsed.surgeMultiplier != null ? `${parsed.surgeMultiplier}x` : '—'} colors={colors} />
            <Row label="Plata" value={parsed.paymentMethod ?? '—'} colors={colors} />
            <Row label="În afara razei" value={parsed.outsideRange ? 'DA' : 'NU'} colors={colors} />
            {parsed.pickupAddress && <Row label="Pickup" value={parsed.pickupAddress} colors={colors} />}
            {parsed.destinationAddress && <Row label="Destinație" value={parsed.destinationAddress} colors={colors} />}
          </View>
        )}

        <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.border, marginTop: 20 }]}>
          <Text style={[s.cardLabel, { color: colors.textTertiary }]}>ULTIMA CAPTURĂ (polling 2s)</Text>
          {capture && capture.timestamp > 0 ? (
            <>
              <Row label="Package" value={capture.package} colors={colors} />
              <Row label="Timestamp" value={new Date(capture.timestamp).toLocaleTimeString()} colors={colors} />
              <View style={[s.captureBox, { borderColor: colors.border }]}>
                <Text style={[s.captureText, { color: colors.text }]} selectable>{capture.text}</Text>
              </View>
            </>
          ) : (
            <Text style={[s.hint, { color: colors.textTertiary }]}>Deschide Bolt Driver / Waze. Polling activ la 2s.</Text>
          )}
        </View>

        <View style={[s.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={[s.cardLabel, { color: colors.textTertiary }]}>
              {'DEBUG OVERLAY (' + (debugStats?.total ?? debugEvents.length) + ')\nsesiune curentă: ' + (debugStats?.curSession ?? 0) + ' / ' + (debugStats?.maxPerSes ?? 5000)}
            </Text>
            <View style={{ flexDirection: 'row', gap: 12 }}>
              <TouchableOpacity onPress={async () => {
                const jsonl = exportAsJsonl();
                if (!jsonl) { Alert.alert('Gol', 'Nu sunt evenimente.'); return; }
                try { await Share.share({ message: jsonl, title: 'DP Debug JSONL' }); }
                catch (e: any) { Alert.alert('Eroare', e?.message || 'Share eșuat'); }
              }}>
                <Text style={[s.btnDebugText, { color: colors.accent }]}>📤 JSONL</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => { clearDpEvents(); setDebugEvents([]); }}>
                <Text style={[s.btnDebugText, { color: colors.critic }]}>șterge</Text>
              </TouchableOpacity>
            </View>
          </View>
          {debugEvents.length === 0 ? (
            <Text style={[s.hint, { color: colors.textTertiary }]}>Nicio activitate. Stă pe Bolt și așteaptă o ofertă — evenimentele apar aici live.</Text>
          ) : (
            debugEvents.slice(0, 25).map((e, i) => (
              <Text key={i} style={[s.captureText, { color: colors.text, fontSize: 11, paddingVertical: 1 }]}>{e}</Text>
            ))
          )}
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

function Row({ label, value, colors, valueColor }: any) {
  return (
    <View style={s.row}>
      <Text style={[s.rowLabel, { color: colors.textSecondary }]}>{label}</Text>
      <Text style={[s.rowValue, { color: valueColor || colors.text }]} numberOfLines={2}>{value}</Text>
    </View>
  );
}
function DebugBtn({ onPress, text, colors, danger }: any) {
  return (
    <TouchableOpacity onPress={onPress} style={[s.btnDebug, { borderColor: colors.border, backgroundColor: colors.surface }]} activeOpacity={0.7}>
      <Text style={[s.btnDebugText, { color: danger ? colors.critic : colors.text }]}>{text}</Text>
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  container:        { flex: 1 },
  backBtn:          { paddingTop: 50, paddingHorizontal: 16, paddingBottom: 8 },
  backText:         { fontSize: 17 },
  scroll:           { padding: 16, paddingBottom: 60 },
  title:            { fontSize: 28, fontWeight: '700', marginBottom: 20 },
  card:             { borderWidth: StyleSheet.hairlineWidth, borderRadius: 12, padding: 16, marginTop: 12 },
  cardLabel:        { fontSize: 12, letterSpacing: 0.5, marginBottom: 8 },
  row:              { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, gap: 12 },
  rowLabel:         { fontSize: 14, flexShrink: 0 },
  rowValue:         { fontSize: 14, fontWeight: '600', flex: 1, textAlign: 'right' },
  verdictBig:       { fontSize: 22, fontWeight: '800', textAlign: 'center', paddingVertical: 12 },
  warn:             { fontSize: 12, marginTop: 8, fontStyle: 'italic' },
  btn:              { marginTop: 20, paddingVertical: 16, borderRadius: 10, alignItems: 'center' },
  btnText:          { color: '#fff', fontSize: 16, fontWeight: '700' },
  btnSecondary:     { marginTop: 10, paddingVertical: 14, borderRadius: 10, alignItems: 'center', borderWidth: StyleSheet.hairlineWidth },
  btnSecondaryText: { fontSize: 15, fontWeight: '500' },
  debugRow:         { flexDirection: 'row', gap: 6, marginTop: 10 },
  btnDebug:         { flex: 1, paddingVertical: 12, borderRadius: 10, alignItems: 'center', borderWidth: StyleSheet.hairlineWidth },
  btnDebugText:     { fontSize: 12, fontWeight: '600' },
  captureBox:       { marginTop: 10, padding: 12, borderWidth: StyleSheet.hairlineWidth, borderRadius: 8, maxHeight: 250 },
  captureText:      { fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 12, lineHeight: 18 },
  hint:             { fontSize: 13, lineHeight: 20, marginTop: 8, fontStyle: 'italic' },
});
