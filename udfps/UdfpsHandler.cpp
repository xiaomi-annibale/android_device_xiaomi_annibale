/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-FileCopyrightText: Paranoid Android
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "UdfpsHandler.annibale"

#include <aidl/android/hardware/biometrics/fingerprint/BnFingerprint.h>
#include <android-base/logging.h>
#include <android-base/unique_fd.h>

#include <fcntl.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include <fstream>
#include <thread>

#include "UdfpsHandler.h"

#define CMD_DATA_BUF_SIZE 256

#define COMMON_DATA_CMD 0
#define SELECT_TOUCH_ID 3
#define SET_CUR_VALUE 0

#define Touch_Fod_Enable 10
#define THP_FOD_DOWNUP_CTL 1001

#define COMMAND_NIT 10
#define PARAM_NIT_FOD 1
#define PARAM_NIT_NONE 0

#define COMMAND_FOD_PRESS_STATUS 1
#define PARAM_FOD_PRESSED 1
#define PARAM_FOD_RELEASED 0

#define FOD_STATUS_OFF 0
#define FOD_STATUS_ON 1

#define TOUCH_DEV_PATH "/dev/xiaomi-touch"
#define TOUCH_MAGIC 0x54
#define TOUCH_ID 0

typedef struct {
    int8_t touch_id;
    uint8_t cmd;
    uint16_t mode;
    uint16_t data_len;
    int32_t data_buf[CMD_DATA_BUF_SIZE];
} touch_base;

#define TOUCH_IOC_SELECT_TOUCH_ID _IOW(TOUCH_MAGIC, SELECT_TOUCH_ID, int)
#define TOUCH_IOC_COMMON_DATA _IOW(TOUCH_MAGIC, COMMON_DATA_CMD, touch_base)

using ::aidl::android::hardware::biometrics::fingerprint::AcquiredInfo;

namespace {

template <typename T>
static void set(const std::string& path, const T& value) {
    std::ofstream file(path);
    file << value;
}

touch_base touchDataPrimary = {
        .touch_id = TOUCH_ID,
        .cmd = SET_CUR_VALUE,
        .mode = 0,
        .data_len = 1,
        .data_buf = {},
};

}  // anonymous namespace

class AnnibaleUdfpsHandler : public UdfpsHandler {
  public:
    void init(fingerprint_device_t* device) {
        mDevice = device;
        touch_fd_ = android::base::unique_fd(open(TOUCH_DEV_PATH, O_RDWR));
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
            setFodStatus(FOD_STATUS_ON);
        }
    }

    void cancel() {
        LOG(INFO) << __func__;
    }

  private:
    fingerprint_device_t* mDevice;
    android::base::unique_fd touch_fd_;

    void setFodStatus(int value) {
        ioctl(touch_fd_.get(), TOUCH_IOC_SELECT_TOUCH_ID, TOUCH_ID);
        touch_base data = {
            .mode = Touch_Fod_Enable,
            .data_buf = {value},
        };
        ioctl(touch_fd_.get(), TOUCH_IOC_COMMON_DATA, &data);
    }

    void setFingerDown(bool pressed) {
        ioctl(touch_fd_.get(), TOUCH_IOC_SELECT_TOUCH_ID, TOUCH_ID);
        touch_base data = {
            .mode = THP_FOD_DOWNUP_CTL,
            .data_buf = {pressed ? 1 : 0},
        };
        ioctl(touch_fd_.get(), TOUCH_IOC_COMMON_DATA, &data);

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
