#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit from generic device
$(call inherit-product, device/xiaomi/annibale/device.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Inherit from the MiuiCamera setup
$(call inherit-product-if-exists, device/xiaomi/annibale-miuicamera/device.mk)

# Lineage stuff
TARGET_EXCLUDES_AUDIOFX := true

PRODUCT_NAME := lineage_annibale
PRODUCT_DEVICE := annibale
PRODUCT_BRAND := POCO
PRODUCT_MODEL := 2510DPC44G
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_GMS_CLIENTID_BASE := android-xiaomi

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildDesc="annibale-user 16 BP2A.250605.031.A3 OS3.0.8.0.WPKMIXM release-keys" \
    BuildFingerprint="POCO/annibale_global/annibale:16/BP2A.250605.031.A3/OS3.0.8.0.WPKMIXM:user/release-keys"
