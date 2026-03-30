/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.xiaomi.settings.touch

import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.database.ContentObserver
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.UserHandle
import android.provider.Settings
import android.util.Log
import com.xiaomi.settings.utils.FileUtils

class TouchReportRateService : Service() {

    private val handler = Handler(Looper.getMainLooper())

    private val settingObserver =
        object : ContentObserver(handler) {
            override fun onChange(selfChange: Boolean) {
                if (DEBUG) Log.d(TAG, "SettingObserver: onChange")
                applyReportRate(this@TouchReportRateService)
            }
        }

    private val screenStateReceiver =
        object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                if (DEBUG) Log.d(TAG, "onReceive: ${intent.action}")
                if (intent.action == Intent.ACTION_SCREEN_ON) {
                    if (DEBUG) Log.d(TAG, "Screen on, restoring touch report rate")
                    applyReportRate(this@TouchReportRateService)
                }
            }
        }

    override fun onCreate() {
        super.onCreate()
        if (DEBUG) Log.d(TAG, "onCreate")
        contentResolver.registerContentObserver(
            Settings.System.getUriFor(SETTING_KEY),
            false,
            settingObserver,
            UserHandle.USER_CURRENT,
        )
        registerReceiver(screenStateReceiver, IntentFilter(Intent.ACTION_SCREEN_ON))
        applyReportRate(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (DEBUG) Log.d(TAG, "onStartCommand")
        return START_STICKY
    }

    override fun onDestroy() {
        if (DEBUG) Log.d(TAG, "onDestroy")
        contentResolver.unregisterContentObserver(settingObserver)
        unregisterReceiver(screenStateReceiver)
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val TAG = "TouchReportRateService"
        private val DEBUG = Log.isLoggable(TAG, Log.DEBUG)

        const val SETTING_KEY = "touch_high_sampling_rate"
        private const val DEFAULT_VALUE = 0
        private const val PROC_PATH = "/proc/xm_htc_report_rate"
        private const val VALUE_NORMAL = "120"
        private const val VALUE_HIGH = "240"

        fun isReportRateWritable(): Boolean = FileUtils.isFileWritable(PROC_PATH)

        fun applyReportRate(context: Context) {
            val value =
                Settings.System.getIntForUser(
                    context.contentResolver,
                    SETTING_KEY,
                    DEFAULT_VALUE,
                    UserHandle.USER_CURRENT,
                )
            if (DEBUG) Log.d(TAG, "applyReportRate: $value")
            FileUtils.writeLine(PROC_PATH, if (value == 1) VALUE_HIGH else VALUE_NORMAL)
        }

        fun startService(context: Context) {
            context.startServiceAsUser(
                Intent(context, TouchReportRateService::class.java),
                UserHandle.CURRENT,
            )
        }
    }
}
