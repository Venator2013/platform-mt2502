
from platformio.util import get_systype
from os.path import join

from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild,
                          Default, DefaultEnvironment)

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()


flasher_path = platform.get_package_dir("framework-mt2502arduino") or ""


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
    TARGETSUFFIX=".vxp"
)

# Setup tools based on system type
env.Replace(
    MTK_FLASHER='"$PYTHONEXE" ' +
    join(flasher_path, 'tools', "uploader.py")
)

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

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)


#
# Target: Print binary size
#

target_size = env.Alias("size", target_elf, env.VerboseAction(
    "$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)


#
# Target: Upload by default .bin file
#
env.Replace(
    UPLOADER="$MTK_FLASHER",
    UPLOADERFLAGS=[
        "-port", '"$UPLOAD_PORT"',
        "-verbose", '2'
        "-app", '$SOURCE'
    ],
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS'
)

for args in env.get("UPLOAD_EXTRA_ARGS", []):
    env.Append(UPLOADERFLAGS=[args])

upload_source = target_upload
upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

if env.subst("$UPLOAD_PORT") == "":
    upload_actions.insert(0, env.VerboseAction(env.AutodetectUploadPort,
                                               "Looking for upload port..."))

AlwaysBuild(env.Alias("upload", upload_source, upload_actions))

#
# Setup default targets
#

Default([target_buildprog, target_size])
