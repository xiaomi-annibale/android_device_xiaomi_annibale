/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

package com.xiaomi.settings.touch

import android.os.IBinder
import android.os.ServiceManager
import android.util.Log
import vendor.xiaomi.hw.touchfeature.ITouchFeature

object TouchFeatureWrapper {

    private const val TAG = "TouchFeatureWrapper"
    private val DEBUG = Log.isLoggable(TAG, Log.DEBUG)

    @Volatile private var touchFeature: ITouchFeature? = null

    private val deathRecipient =
        IBinder.DeathRecipient {
            if (DEBUG) Log.d(TAG, "serviceDied")
            touchFeature = null
        }

    @Synchronized
    private fun getTouchFeature(): ITouchFeature? =
        touchFeature
            ?: runCatching {
                val fqName = "${ITouchFeature.DESCRIPTOR}/default"
                val binder =
                    android.os.Binder.allowBlocking(
                        ServiceManager.waitForDeclaredService(fqName)
                    )
                ITouchFeature.Stub.asInterface(binder).apply {
                    asBinder().linkToDeath(deathRecipient, 0)
                }
            }
            .onSuccess { touchFeature = it }
            .onFailure { e -> Log.e(TAG, "getTouchFeature failed!", e) }
            .getOrNull()

    fun isServiceAvailable(): Boolean =
        ServiceManager.isDeclared("${ITouchFeature.DESCRIPTOR}/default")

    fun setModeValue(type: Int, mode: Int, value: Int) {
        val tf =
            getTouchFeature()
                ?: run {
                    Log.e(TAG, "touchFeature is null!")
                    return
                }
        if (DEBUG) Log.d(TAG, "setModeValue: type=$type, mode=$mode, value=$value")
        runCatching { tf.setModeValue(type, mode, value) }
            .onFailure { e -> Log.e(TAG, "setModeValue failed!", e) }
    }
}
