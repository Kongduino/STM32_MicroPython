# MCU settings
MCU_SERIES = h7
CMSIS_MCU = STM32H743xx
MICROPY_FLOAT_IMPL = double
AF_FILE = boards/stm32h743_af.csv
LD_FILES = boards/WEACT_H743/stm32h743.ld boards/common_basic.ld
TEXT0_ADDR = 0x08000000

# MicroPython settings
MICROPY_PY_SSL = 1
MICROPY_SSL_MBEDTLS = 1
MICROPY_PY_LWIP = 1
MICROPY_PY_USSL = 1
MICROPY_VFS_LFS2 = 1