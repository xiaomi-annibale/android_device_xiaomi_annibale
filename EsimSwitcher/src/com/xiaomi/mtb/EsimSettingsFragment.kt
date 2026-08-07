/*
 * SPDX-FileCopyrightText: 2023-2025 Paranoid Android
 * SPDX-FileCopyrightText: 2026 The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 *
 */

package com.xiaomi.mtb

import android.os.Bundle
import androidx.appcompat.app.AlertDialog
import androidx.preference.Preference
import com.android.settingslib.widget.FooterPreference
import com.android.settingslib.widget.MainSwitchPreference
import com.android.settingslib.widget.SettingsBasePreferenceFragment

class EsimSettingsFragment :
    SettingsBasePreferenceFragment(), Preference.OnPreferenceChangeListener {

    private val esimController by lazy { EsimController.getInstance(requireContext()) }

    private val switchBar by lazy { findPreference<MainSwitchPreference>("esim_enable")!! }
    private val footerPref by lazy { findPreference<FooterPreference>("esim_footer")!! }

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.settings_esim, rootKey)

        switchBar.onPreferenceChangeListener = this
        switchBar.isEnabled = true
        footerPref.title = getString(R.string.esim_footer_note)
    }

    override fun onResume() {
        super.onResume()
        refreshState()
    }

    private fun refreshState() {
        switchBar.isChecked = esimController.getEsimEnabled()
    }

    override fun onPreferenceChange(preference: Preference, newValue: Any?): Boolean {
        if (preference != switchBar) return true
        val enable = newValue as Boolean
        if (enable) {
            if (esimController.isSim2Active()) {
                showEsimInUseWarning()
                return false
            }
        } else {
            if (esimController.isEsimProfileActive()) {
                showEsimInUseWarning()
                return false
            }
        }

        if (!esimController.setEsimEnabled(enable)) {
            refreshState()
            return false
        }
        return true
    }

    private fun showEsimInUseWarning() {
        AlertDialog.Builder(requireContext())
            .setTitle(R.string.esim_warning_title)
            .setMessage(R.string.esim_warning_message)
            .setPositiveButton(android.R.string.ok, null)
            .show()
    }
}
