/*
 * SPDX-FileCopyrightText: 2023-2025 Paranoid Android
 * SPDX-FileCopyrightText: 2026 The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 *
 */

package com.xiaomi.mtb

import android.content.Context
import android.telephony.SubscriptionManager
import android.util.Log
import com.qti.extphone.Client
import com.qti.extphone.ExtPhoneCallbackListener
import com.qti.extphone.ExtTelephonyManager
import com.qti.extphone.QtiSimType
import com.qti.extphone.ServiceCallback

class EsimController private constructor(private val context: Context) {
    private var extTelephonyManager: ExtTelephonyManager? = null
    private var client: Client? = null
    private var isConnected = false

    private val serviceCallback = object : ServiceCallback {
        override fun onConnected() {
            Log.d(TAG, "ExtTelephonyService connected")
            isConnected = true

            extTelephonyManager?.let {
                client = it.registerCallbackWithEvents(
                    context.packageName,
                    phoneCallbackListener,
                    intArrayOf(
                        ExtPhoneCallbackListener.EVENT_ON_SIM_TYPE_CHANGED
                    )
                )
            }
        }

        override fun onDisconnected() {
            Log.d(TAG, "ExtTelephonyService disconnected")
            isConnected = false
            client = null
        }
    }

    private val phoneCallbackListener = object : ExtPhoneCallbackListener() {
        override fun onSimTypeChanged(simTypes: Array<QtiSimType>?) {
            if (simTypes?.size != 2) return
            Log.d(TAG, "onSimTypeChanged: SIM2 is now ${simTypes[1].get()}")
        }
    }

    fun onBootCompleted() {
        Log.d(TAG, "onBootCompleted: Binding ExtTelephony")
        extTelephonyManager = ExtTelephonyManager.getInstance(context)
        extTelephonyManager?.connectService(serviceCallback)
    }

    fun isEsimProfileActive(): Boolean {
        val sm = context.getSystemService(SubscriptionManager::class.java)
        return sm?.activeSubscriptionInfoList ?.any { it.isEmbedded } == true
    }

    fun isSim2Active(): Boolean {
        val sm = context.getSystemService(SubscriptionManager::class.java)
        return sm?.activeSubscriptionInfoList ?.any { it.simSlotIndex == SIM2_SLOT && !it.isEmbedded } == true
    }

    fun getEsimEnabled(): Boolean {
        val simTypes = extTelephonyManager?.currentSimType
        return simTypes?.size == 2 &&
            simTypes[1].get() == QtiSimType.SIM_TYPE_ESIM
    }

    fun setEsimEnabled(isEnabled: Boolean): Boolean {
        Log.d(TAG, "setEsimEnabled: $isEnabled")
        if (!isConnected || client == null) {
            Log.e(TAG, "Cannot set eSIM: service disconnected")
            return false
        }

        if (isEnabled && isSim2Active()) {
            Log.w(TAG, "Cannot enable eSIM: SIM 2 is still active")
            return false
        }

        if (!isEnabled && isEsimProfileActive()) {
            Log.w(TAG, "Cannot disable eSIM: eSIM profile is still active")
            return false
        }

        val targetType = if (isEnabled) {
            QtiSimType.SIM_TYPE_ESIM
        } else {
            QtiSimType.SIM_TYPE_PHYSICAL
        }

        val config = arrayOf(
            QtiSimType(QtiSimType.SIM_TYPE_PHYSICAL),
            QtiSimType(targetType)
        )

        return try {
            extTelephonyManager?.setSimType(client, config)
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to call setSimType", e)
            false
        }
    }

    companion object {
        private const val TAG = "EsimController"
        private const val SIM2_SLOT = 1

        @Volatile
        private var instance: EsimController? = null

        fun getInstance(context: Context): EsimController {
            return instance ?: synchronized(this) {
                instance ?: EsimController(context.applicationContext).also {
                    instance = it
                }
            }
        }
    }
}
