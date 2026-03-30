/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.xiaomi.settings.touch

import android.os.Bundle
import android.os.UserHandle
import android.provider.Settings
import android.util.Log
import androidx.preference.Preference
import com.android.settingslib.widget.MainSwitchPreference
import com.android.settingslib.widget.SettingsBasePreferenceFragment
import com.xiaomi.settings.R

class TouchSettingsFragment :
    SettingsBasePreferenceFragment(), Preference.OnPreferenceChangeListener {

    companion object {
        private const val TAG = "TouchSettingsFragment"
        private val DEBUG = Log.isLoggable(TAG, Log.DEBUG)
    }

    private val switchBar by lazy {
        findPreference<MainSwitchPreference>(TouchReportRateService.SETTING_KEY)!!
    }

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        if (DEBUG) Log.d(TAG, "onCreatePreferences")
        setPreferencesFromResource(R.xml.settings_touch, rootKey)

        val isEnabled =
            Settings.System.getIntForUser(
                requireContext().contentResolver,
                TouchReportRateService.SETTING_KEY,
                0,
                UserHandle.USER_CURRENT,
            ) == 1

        switchBar.isChecked = isEnabled
        switchBar.isEnabled = TouchReportRateService.isReportRateWritable()
        switchBar.onPreferenceChangeListener = this
    }

    override fun onPreferenceChange(preference: Preference, newValue: Any?): Boolean {
        if (preference == switchBar) {
            val isChecked = newValue as Boolean
            if (DEBUG) Log.d(TAG, "onPreferenceChange: $isChecked")
            Settings.System.putIntForUser(
                requireContext().contentResolver,
                TouchReportRateService.SETTING_KEY,
                if (isChecked) 1 else 0,
                UserHandle.USER_CURRENT,
            )
        }
        return true
    }
}
