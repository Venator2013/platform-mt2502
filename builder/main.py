# Copyright 2021 WAYBYTE Solutions
#
# SPDX-License-Identifier: MIT
#

from platformio.util import get_systype
from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild,
                          Default, DefaultEnvironment)

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
#flasher_path = platform.get_package_dir("tool-logicromflasher") or ""

def _get_board_mcu():
    return board.get("build.mcu")

env.Replace(
    __get_board_mcu=_get_board_mcu,

    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],

    SIZEPROGREGEXP=r"^(?:\.text|\.data|\.rodata|\.text.align|\.ARM.exidx|\.ARM.extab|\.ll|\.initdata|\.init_array|\.corestub)\s+(\d+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit|\.corestub)\s+(\d+).*",
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',

    PROGSUFFIX=".elf",
    TARGETSUFFIX=".bin"
)

# Setup tools based on system type
# if "windows" in get_systype() and board.get("build.mcu") in ["MT2502"]:
#     env.Replace(
#         LOGICROM_FLASHER=join(flasher_path, "logicromflasher"),
#         REFLASH_FLAGS=[
#             "-r",
#             "-b", "$UPLOAD_SPEED",
#             "-p", '"$UPLOAD_PORT"',
#         ],
#         REFLASH_CMD='"$LOGICROM_FLASHER" $REFLASH_FLAGS'
#     )
# else:
#     env.Replace(
#         LOGICROM_FLASHER='"$PYTHONEXE" ' + join(flasher_path, "logicromflasher.py"),
#         REFLASH_CMD='echo "Sorry! Reflashing is only supported on windows! :("'
#     )

# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

#
# Target: Build executable and linkable firmware
#

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = join("$BUILD_DIR", "${PROGNAME}.${TARGETSUFFIX}")
    target_upload = target_firm
else:
    target_elf = env.BuildProgram()
    target_firm = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_upload = target_firm

if board.get("build.mcu") == "RDA8910":
    target_upload = join("$BUILD_DIR", "${PROGNAME}.img")
    env.Depends(target_upload, target_firm)

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)


#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, env.VerboseAction(
    "$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Reflash core for GSM devices
#
if board.get("build.mcu") in ["MT2502"]:
    AlwaysBuild(
        env.AddCustomTarget("reflash", None, [
            env.VerboseAction("$REFLASH_CMD", "Reflashing core...")
        ], title="Reflash Core Firmware",
            description="Reflash module core firmware (Only available on windows)"))

#
# Target: Upload by default .bin file
#
env.Replace(
    UPLOADER="$LOGICROM_FLASHER",
    UPLOADERFLAGS=[
        "-b", "$UPLOAD_SPEED",
        "-p", '"$UPLOAD_PORT"',
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS $SOURCE'
)

for args in env.get("UPLOAD_EXTRA_ARGS", []):
    env.Append(UPLOADERFLAGS=[args])

upload_source = target_upload
upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

if board.get("build.mcu") not in ["MT2502"]:
    env.Prepend(
        UPLOADERFLAGS=[
            "-m", '"${__get_board_mcu()}"',
        ]
    )

if env.subst("$UPLOAD_PORT") == "":
    if "windows" in get_systype() and board.get("build.mcu") in ["MT2502"]:
        env.Prepend(
            UPLOADERFLAGS=["-u"],
            REFLASH_FLAGS=["-u"],
        )
    elif board.get("build.mcu") != "RDA8910":
        upload_actions.insert(0, env.VerboseAction(env.AutodetectUploadPort,
            "Looking for upload port..."))

AlwaysBuild(env.Alias("upload", upload_source, upload_actions))

#
# Setup default targets
#

Default([target_buildprog, target_size])
