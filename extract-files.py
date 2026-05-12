#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os
from extract_utils.file import File
from extract_utils.fixups_blob import (
    BlobFixupCtx,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)
from extract_utils.utils import (
    Color,
    color_print,
)

namespace_imports = [
    'hardware/qcom-caf/sm8750',
    'hardware/qcom-caf/wlan',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/dataservices',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'vendor.qti.diaghal-V1-ndk',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.wifidisplaysession_aidl-V1-ndk',
        'vendor.qti.ims.uceaidlservice-V1-ndk',
        'vendor.qti.ImsRtpService-V1-ndk',
        'vendor.qti.qccsyshal_aidl-V1-ndk',
        'vendor.qti.qccvndhal_aidl-V1-ndk',
    ): lib_fixup_vendor_suffix,
}

def blob_fixup_split_file(
    ctx: 'BlobFixupCtx',
    file: 'File',
    file_path: str,
    *args,
    **kwargs,
):
    # Split the file into parts
    part_size = 51380224 # 49 MiB
    part_number = 0
    with open(file_path, 'rb') as f:
        while chunk := f.read(part_size):
            part_file_name = f"{file_path}.part{part_number:02d}"
            with open(part_file_name, 'wb') as part_file:
                part_file.write(chunk)
            part_number += 1
    color_print(f'{file.dst}: split into {part_number} parts', color=Color.GREEN)

    # Add the file to .gitignore
    gitignore_path = os.path.join(module.vendor_path, '.gitignore')
    with open(gitignore_path, 'a+') as gitignore_file:
        gitignore_file.seek(0)  # Move to the start of the file
        existing_entries = gitignore_file.read().splitlines()
        if f'proprietary/{file.dst}' not in existing_entries:
            gitignore_file.write(f'proprietary/{file.dst}\n')
            color_print(f'{file.dst}: added to .gitignore', color=Color.GREEN)

blob_fixups: blob_fixups_user_type = {
    (
        'odm/lib64/libarcsoft_raw_sr.so',
        'odm/lib64/libarcsoft_turbo_fusion_mfnr.so',
        'odm/lib64/libarcsoft_turbo_hdr_raw.so',
        'odm/lib64/libarcsoft_turbo_fusion_raw_super_night.so',
        'odm/lib64/libarcsoft_dark_vision.so'
    ): blob_fixup()
        .call(blob_fixup_split_file),
    'system_ext/lib64/libwfdmmsrc_system.so': blob_fixup()
        .add_needed('libgui_shim.so'),
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .add_needed('libbinder_shim.so')
        .add_needed('libinput_shim.so'),
    (
        'odm/etc/camera/enhance_motiontuning.xml',
        'odm/etc/camera/motiontuning.xml',
        'odm/etc/camera/snsc_bokeh_motiontuning.xml',
        'odm/etc/camera/snsc_enhance_motiontuning.xml',
        'odm/etc/camera/snsc_motiontuning.xml',
        'odm/etc/camera/snsc_noface_motiontuning.xml'
    ): blob_fixup()
        .regex_replace(
            'xml=version',
            'xml version'
        ),
    (
        'odm/lib64/libaudioroute_ext.so',
        'vendor/lib64/libagm.so',
        'vendor/lib64/libar-pal.so',
        'vendor/lib64/libmcs.so',
        'vendor/lib64/libmikaraoke.so',
        'vendor/lib64/libtiantongpal.so',
    ): blob_fixup()
        .replace_needed(
            'libaudioroute.so',
            'libaudioroute_annibale.so'
        ),
    (
        'odm/bin/hw/vendor.xiaomi.hw.touchfeature-service',
        'odm/lib64/hw/displayfeature.default.so',
        'odm/lib64/libadaptivehdr.so',
        'odm/lib64/libcolortempmode.so',
        'odm/lib64/libdither.so',
        'odm/lib64/libflatmode.so',
        'odm/lib64/libhistprocess.so',
        'odm/lib64/libmiBrightness.so',
        'odm/lib64/libmiSensorCtrl.so',
        'odm/lib64/libpaperMode.so',
        'odm/lib64/librhytheyecare.so',
        'odm/lib64/libsdr2hdr.so',
        'odm/lib64/libsre.so',
        'odm/lib64/libtruetone.so',
        'odm/lib64/libvideomode.so',
        'vendor/lib64/libgnss.so'
    ): blob_fixup()
        .replace_needed(
            'android.hardware.sensors-V2-ndk.so',
            'android.hardware.sensors-V3-ndk.so',
        ),
    'odm/bin/hw/vendor.xiaomi.sensor.citsensorservice.aidl': blob_fixup()
        .replace_needed(
            'android.hardware.graphics.common-V5-ndk.so',
            'android.hardware.graphics.common-V7-ndk.so'
        )
        .replace_needed(
            'android.hardware.sensors-V2-ndk.so',
            'android.hardware.sensors-V3-ndk.so'
        ),
    (
        'vendor/etc/media_codecs_sun.xml',
        'vendor/etc/media_codecs_sun_vendor_without_dvenc.xml',
    ): blob_fixup()
        .regex_replace('.*media_codecs_(google_audio|google_c2|google_telephony|google_video|vendor_audio).*\n', ''),
    (
        'odm/lib64/camera/components/com.qti.node.dewarp.so',
        'odm/lib64/hw/com.qti.chi.override.so',
        'odm/lib64/libcamximageformatutils.so',
        'odm/lib64/libchifeature2.so',
        'odm/lib64/vendor.qti.hardware.camera.offlinecamera-service-impl.so',
        'vendor/lib64/libqvrservice.so'
    ): blob_fixup()
        .replace_needed(
            'android.hardware.graphics.allocator-V1-ndk.so',
            'android.hardware.graphics.allocator-V2-ndk.so'
        ),
    'odm/lib64/hw/camera.qcom.so': blob_fixup()
        .replace_needed(
            'android.hardware.sensors-V2-ndk.so',
            'android.hardware.sensors-V3-ndk.so'
        ),
    'vendor/lib64/libcameraopt.so': blob_fixup()
        .add_needed('libprocessgroup_shim.so'),
    (
        'odm/lib64/libAncHumanPreviewBokeh.so',
        'odm/lib64/libMiEmojiEffect.so',
        'odm/lib64/libMiPhotoFilter.so',
        'odm/lib64/libMiVideoFilter.so',
        'odm/lib64/libTrueSight.so',
        'odm/lib64/libarcsoft_beautyshot.so',
        'odm/lib64/libwa_widelens_undistort.so'
    ): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lockPlanes')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_isSupported'),
    (
        'odm/lib64/hw/fingerprint.qcom_us.default.so',
        'odm/lib64/libqc_hal.so'
    ): blob_fixup()
        .replace_needed(
            'android.hardware.biometrics.fingerprint-V5-ndk.so',
            'android.hardware.biometrics.fingerprint-V4-ndk.so'
        ),
    'odm/etc/init/vendor.xiaomi.hw.touchfeature-service.rc': blob_fixup()
        .regex_replace(r'service touch-kmsg-init-sh\b[\s\S]*?\n(?=\S|$)', ''),
    (
        'odm/bin/hw/vendor.qti.camera.provider-service_64',
        'odm/bin/hw/vendor.xiaomi.sensor.citsensorservice.aidl',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinetintless.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.anchor.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineyuveis.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineyuvreprocess.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinei2y.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.mialgoallinone.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinehdrraw2y.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinetintlesshdr.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineb2y.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinemlawb.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineheic.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineawbideal.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinemfnr.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineformatconvertor.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlinejpeg.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.offlineyuvsplit.so',
        'odm/lib64/com.xiaomi.plugin.ecdengine.so',
        'odm/lib64/hw/displayfeature.default.so',
        'odm/lib64/libcamxods.so',
        'odm/lib64/libcamxcoreutils.so',
        'odm/lib64/libmiXmlParser.so',
        'odm/lib64/libmicamera_hal_core.so',
        'odm/lib64/libsimulation.so',
        'vendor/bin/hw/vendor.qti.hardware.display.composer-service',
        'vendor/bin/poweropt-service',
        'vendor/lib64/hw/libaudioeffecthal.qti.so',
        'vendor/lib64/libaodoptfeature.so',
        'vendor/lib64/libapengine.so',
        'vendor/lib64/libaudiocloudctrl.so',
        'vendor/lib64/liblearningmodule.so',
        'vendor/lib64/libpsmoptfeature.so',
        'vendor/lib64/libsdmclient.so',
        'vendor/lib64/libpowercore.so',
        'vendor/lib64/libstandbyfeature.so',
        'vendor/lib64/soundfx/libquasar.so',
    ): blob_fixup()
        .replace_needed(
            'libtinyxml2.so',
            'libtinyxml2-v36.so'
        ),
    (
        'odm/lib64/camera/plugins/com.xiaomi.plugin.gainmap.so',
        'odm/lib64/camera/plugins/com.xiaomi.plugin.jpegrAggr.so'
    ): blob_fixup()
        .replace_needed(
            'libultrahdr.so',
            'libultrahdr_annibale.so'
        ),
    (
        'vendor/bin/wfdhdcphalservice',
        'vendor/bin/wfdvndservice'
    ): blob_fixup()
        .replace_needed(
            'libwfdhdcpservice_proprietary.so',
            'libwfdhdcpservice_annibale.so'
        ),
    'vendor/lib64/hw/libaudiocorehal.qti.so': blob_fixup()
        .replace_needed(
            'android.hardware.audio.core.sounddose-V1-ndk.so',
            'android.hardware.audio.core.sounddose-V2-ndk.so'
        )
        .replace_needed(
            'libaudio_aidl_conversion_common_ndk.so',
            'libaudio_aidl_conversion_common_ndk_prebuilt.so'
        ),
    'vendor/lib64/libaudioserviceexampleimpl.so': blob_fixup()
        .add_needed('libaudioutils_shim.so')
        .replace_needed(
            'android.hardware.bluetooth.audio-impl.so',
            'android.hardware.bluetooth.audio-impl_prebuilt.so'
        )
        .replace_needed(
            'libbluetooth_audio_session_aidl.so',
            'libbluetooth_audio_session_aidl_prebuilt.so'
        )
        .replace_needed(
            'libaudio_aidl_conversion_common_ndk.so',
            'libaudio_aidl_conversion_common_ndk_prebuilt.so'
        ),
    'vendor/lib64/android.hardware.bluetooth.audio-impl_prebuilt.so': blob_fixup()
        .replace_needed(
            'libbluetooth_audio_session_aidl.so',
            'libbluetooth_audio_session_aidl_prebuilt.so'
        ),
    'vendor/lib64/libqcrilNrVoiceModule.so': blob_fixup()
        .sig_replace('a1 00 80 52 22', 'a1 00 80 52 02'),
    (
        'vendor/lib64/libcapiv2uvvendor.so',
        'vendor/lib64/liblistensoundmodel2vendor.so',
        'vendor/lib64/libVoiceSdk.so',
    ): blob_fixup()
        .replace_needed(
            'libtensorflowlite_c.so',
            'libtensorflowlite_c_vendor.so',
    ),
    'vendor/lib64/libqcodec2_core.so': blob_fixup()
        .replace_needed(
            'android.hardware.graphics.common-V5-ndk.so',
            'android.hardware.graphics.common-V7-ndk.so'
        ),
    'vendor/lib64/libultrahdr_annibale.so': blob_fixup()
        .replace_needed(
            'libjpegdecoder.so',
            'libjpegdecoder_annibale.so'
        )
        .replace_needed(
            'libjpegencoder.so',
            'libjpegencoder_annibale.so'
        ),
    'vendor/lib64/libwfdmmsrc_proprietary.so': blob_fixup()
        .replace_needed(
            'android.media.audio.common.types-V2-ndk.so',
            'android.media.audio.common.types-V3-ndk.so'
        ),
}  # fmt: skip

module = ExtractUtilsModule(
    'annibale',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
