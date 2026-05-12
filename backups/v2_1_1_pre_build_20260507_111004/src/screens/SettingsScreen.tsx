import React, { useEffect, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet, SafeAreaView, Alert, Switch,
} from 'react-native';
import { useTheme } from '../hooks/useTheme';
import type { ThemeMode } from '../constants/theme';
import { getLicenseState, clearLicense } from '../services/licenseManager';
import { getOverlayModePro, setOverlayModePro } from '../services/overlayController';
import { Overlay } from '../native/overlay';
import { DeviceEventEmitter } from 'react-native';

interface Props {
  onOpenFuel: () => void;
  onOpenPro: () => void;
  onOpenFilters: () => void;
  onOpenUpgrade: () => void;
  onOpenAccessibility: () => void;
}

const THEME_OPTIONS: { mode: ThemeMode; label: string; icon: string }[] = [
  { mode: 'automatic', label: 'Automatic', icon: '◐' },
  { mode: 'light',     label: 'Light',     icon: '☀' },
  { mode: 'dark',      label: 'Dark',      icon: '☾' },
];

export default function SettingsScreen({ onOpenFuel, onOpenPro, onOpenFilters, onOpenUpgrade, onOpenAccessibility }: Props) {
  const { mode, setMode, colors } = useTheme();
  const [plan, setPlan] = useState<string | null>(null);
  const [proCard, setProCard] = useState(false);
  const [overlayPerm, setOverlayPerm] = useState<boolean | null>(null);

  useEffect(() => { (async () => {
    const st = await getLicenseState();
    if (st.license) setPlan(st.license.plan);
    setProCard((await getOverlayModePro()) === 'full');
    setOverlayPerm(await Overlay.canDrawOverlays());
  })(); }, []);

  const isPro = plan === 'pro';

  const handleToggleProCard = async (val: boolean) => {
    if (!isPro) { onOpenUpgrade(); return; }
    setProCard(val);
    await setOverlayModePro(val ? 'full' : 'simple');
  };

  const handleRequestOverlay = async () => {
    await Overlay.requestPermission();
    setTimeout(async () => setOverlayPerm(await Overlay.canDrawOverlays()), 1500);
  };

  const handleResetLicense = () => {
    Alert.alert('Schimbă cod', 'Vei fi delogat și redirectat la activare. Continui?', [
      { text: 'Anulează', style: 'cancel' },
      { text: 'Continuă', style: 'destructive', onPress: async () => {
        await clearLicense();
        DeviceEventEmitter.emit('dp_license_changed');
      } },
    ]);
  };

  return (
    <SafeAreaView style={[s.container, { backgroundColor: colors.bg }]}>
      <ScrollView>
        <Text style={[s.pageTitle, { color: colors.text }]}>Settings</Text>

        {plan && (
          <>
            <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>PLAN</Text>
            <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
              <View style={s.row}>
                <Text style={[s.label, { color: colors.text }]}>Plan curent</Text>
                <Text style={[s.value, { color: colors.accent }]}>{plan.toUpperCase()}</Text>
              </View>
              {plan !== 'pro' && (
                <TouchableOpacity onPress={onOpenUpgrade} activeOpacity={0.6}
                  style={[s.row, { borderTopColor: colors.divider, borderTopWidth: StyleSheet.hairlineWidth }]}>
                  <Text style={[s.label, { color: colors.accent }]}>⭐ Upgrade plan</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity onPress={handleResetLicense} activeOpacity={0.6}
                style={[s.row, { borderTopColor: colors.divider, borderTopWidth: StyleSheet.hairlineWidth }]}>
                <Text style={[s.label, { color: colors.critic }]}>Schimbă cod / Logout</Text>
              </TouchableOpacity>
            </View>
          </>
        )}

        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>CARBURANT</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <TouchableOpacity onPress={onOpenFuel} activeOpacity={0.6} style={s.row}>
            <Text style={[s.label, { color: colors.text }]}>⛽ Tip & preț carburant</Text>
            <Text style={[s.chevron, { color: colors.textTertiary }]}>›</Text>
          </TouchableOpacity>
        </View>

        {/* === FILTRE CURSE (toate planurile, gradul de acces variaza) === */}
        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>🎯 FILTRE CURSE</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <TouchableOpacity onPress={onOpenFilters} activeOpacity={0.6} style={s.row}>
            <View style={{ flex: 1 }}>
              <Text style={[s.label, { color: colors.text }]}>Filtre profitabilitate</Text>
              <Text style={[s.subLabel, { color: colors.textTertiary }]}>
                Trial: 1 filtru · Simplu: 2 · Pro: 4
              </Text>
            </View>
            <Text style={[s.chevron, { color: colors.textTertiary }]}>›</Text>
          </TouchableOpacity>
        </View>

        {/* === ACCESSIBILITY TEST === */}
        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>🔍 DIAGNOSTIC</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <TouchableOpacity onPress={onOpenAccessibility} activeOpacity={0.6} style={s.row}>
            <View style={{ flex: 1 }}>
              <Text style={[s.label, { color: colors.text }]}>Accessibility Test</Text>
              <Text style={[s.subLabel, { color: colors.textTertiary }]}>
                Verifică că DriverPower citește Bolt corect
              </Text>
            </View>
            <Text style={[s.chevron, { color: colors.textTertiary }]}>›</Text>
          </TouchableOpacity>
        </View>

        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>PRO {!isPro && '🔒'}</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={s.row}>
            <View style={{ flex: 1 }}>
              <Text style={[s.label, { color: isPro ? colors.text : colors.textTertiary }]}>
                {!isPro && '🔒 '}Card complet (overlay detaliat)
              </Text>
              <Text style={[s.subLabel, { color: colors.textTertiary }]}>
                {isPro ? (proCard ? 'Card complet activ' : 'Bulina simplă activă') : 'Disponibil în planul Pro'}
              </Text>
            </View>
            <Switch value={isPro && proCard} onValueChange={handleToggleProCard}
              thumbColor={colors.surface} trackColor={{ true: colors.accent, false: colors.border }} />
          </View>
        </View>

        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>OVERLAY PERMISSION</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={s.row}>
            <View style={{ flex: 1 }}>
              <Text style={[s.label, { color: colors.text }]}>Display over other apps</Text>
              <Text style={[s.subLabel, { color: colors.textTertiary }]}>{overlayPerm === null ? '...' : overlayPerm ? 'Acordată ✓' : 'Lipsă — apasă pentru a acorda'}</Text>
            </View>
            {overlayPerm === false && (
              <TouchableOpacity onPress={handleRequestOverlay} activeOpacity={0.7} style={[s.smallBtn, { backgroundColor: colors.accent }]}>
                <Text style={s.smallBtnText}>Acordă</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>

        <Text style={[s.sectionLabel, { color: colors.textTertiary }]}>THEME</Text>
        <View style={[s.group, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          {THEME_OPTIONS.map((opt, i) => {
            const sel = mode === opt.mode;
            const last = i === THEME_OPTIONS.length - 1;
            return (
              <TouchableOpacity key={opt.mode} onPress={() => setMode(opt.mode)} activeOpacity={0.6}
                style={[s.row, !last && { borderBottomColor: colors.divider, borderBottomWidth: StyleSheet.hairlineWidth }]}>
                <Text style={[s.icon, { color: colors.text }]}>{opt.icon}</Text>
                <Text style={[s.label, { color: colors.text }]}>{opt.label}</Text>
                <View style={[s.radio, { borderColor: sel ? colors.accent : colors.border }, sel && { backgroundColor: colors.accent }]}>
                  {sel && <View style={s.radioDot} />}
                </View>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={[s.footnote, { color: colors.textTertiary }]}>
          DriverPower RO · Build 15 · GO PAMPA S.R.L.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1 },
  pageTitle:    { fontSize: 34, fontWeight: '700', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 24 },
  sectionLabel: { fontSize: 13, textTransform: 'uppercase', letterSpacing: 0.5, paddingHorizontal: 20, paddingBottom: 8, paddingTop: 12 },
  group:        { marginHorizontal: 16, borderRadius: 12, overflow: 'hidden', borderWidth: StyleSheet.hairlineWidth },
  row:          { flexDirection: 'row', alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16 },
  icon:         { fontSize: 22, width: 32 },
  label:        { fontSize: 16, fontWeight: '500' },
  subLabel:     { fontSize: 12, marginTop: 2 },
  value:        { fontSize: 16, fontWeight: '600', marginLeft: 'auto' },
  chevron:      { fontSize: 22, marginLeft: 'auto' },
  radio:        { width: 24, height: 24, borderRadius: 12, borderWidth: 2, alignItems: 'center', justifyContent: 'center', marginLeft: 'auto' },
  radioDot:     { width: 8, height: 8, borderRadius: 4, backgroundColor: '#FFFFFF' },
  smallBtn:     { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8 },
  smallBtnText: { color: '#fff', fontSize: 13, fontWeight: '700' },
  footnote:     { fontSize: 12, textAlign: 'center', paddingTop: 24, paddingBottom: 16 },
});
