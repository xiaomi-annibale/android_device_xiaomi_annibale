/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-FileCopyrightText: Paranoid Android
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "UdfpsHandler.annibale"

#include <aidl/android/hardware/biometrics/fingerprint/BnFingerprint.h>
#include <android-base/logging.h>
#include <android-base/unique_fd.h>

#include <fstream>

#include "UdfpsHandler.h"

#define COMMAND_NIT 10
#define PARAM_NIT_FOD 1
#define PARAM_NIT_NONE 0

#define COMMAND_FOD_PRESS_STATUS 1
#define PARAM_FOD_PRESSED 1
#define PARAM_FOD_RELEASED 0

using ::aidl::android::hardware::biometrics::fingerprint::AcquiredInfo;

namespace {

template <typename T>
static void set(const std::string& path, const T& value) {
    std::ofstream file(path);
    file << value;
}

}  // anonymous namespace

class AnnibaleUdfpsHandler : public UdfpsHandler {
  public:
    void init(fingerprint_device_t* device) {
        mDevice = device;
    }

    void onFingerDown(uint32_t /*x*/, uint32_t /*y*/, float /*minor*/, float /*major*/) {
        LOG(DEBUG) << __func__;
        setFingerDown(true);
    }

    void onFingerUp() {
        LOG(DEBUG) << __func__;
        setFingerDown(false);
    }

    void onAcquired(int32_t result, int32_t vendorCode) {
        LOG(DEBUG) << __func__ << " result: " << result << " vendorCode: " << vendorCode;
        if (static_cast<AcquiredInfo>(result) == AcquiredInfo::VENDOR && vendorCode == 201) {
            onFingerUp();
        }
    }

    void cancel() {
        LOG(INFO) << __func__;
    }

  private:
    fingerprint_device_t* mDevice;

    void setFingerDown(bool pressed) {
        if (mDevice) {
            mDevice->extCmd(mDevice, COMMAND_NIT, pressed ? PARAM_NIT_FOD : PARAM_NIT_NONE);
            mDevice->extCmd(mDevice, COMMAND_FOD_PRESS_STATUS, pressed ? PARAM_FOD_PRESSED : PARAM_FOD_RELEASED);
        }
    }
};

static UdfpsHandler* create() {
    return new AnnibaleUdfpsHandler();
}

static void destroy(UdfpsHandler* handler) {
    delete handler;
}

extern "C" UdfpsHandlerFactory UDFPS_HANDLER_FACTORY = {
        .create = create,
        .destroy = destroy,
};
