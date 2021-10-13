"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

http://arduino.cc/en/Reference/HomePage
"""

from os.path import abspath, isdir, isfile, join, dirname, getsize
from os import remove
from shutil import copyfile
from hashlib import md5
import zlib

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-mt2502arduino")
assert isdir(FRAMEWORK_DIR)


def gen_bin_file(target, source, env):
    cmd = ["$OBJCOPY"]
    (target_firm, ) = target
    (target_elf, ) = source

    flash_addr = {
        "bc20": [0x00, 0x40, 0x2D, 0x08],
        "6261": [0x00, 0x00, 0x2E, 0x10],
    }

    temp_firm = dirname(target_firm.get_abspath()) + "/temp.bin"
    cmd.extend(["-O", "binary"])
    cmd.append(target_elf.get_abspath())
    cmd.append(temp_firm)
    env.Execute(env.VerboseAction(" ".join(cmd), " "))

    GFH_Header = bytearray([
        0x4D, 0x4D, 0x4D, 0x01, 0x40, 0x00, 0x00, 0x00,
        0x46, 0x49, 0x4C, 0x45, 0x5F, 0x49, 0x4E, 0x46,
        0x4F, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x00, 0x70, 0x07, 0x00, 0x00, 0x00, 0x2E, 0x10,
        0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])
    firm_size = (getsize(temp_firm) + 64).to_bytes(4, "little")
    GFH_Header[0x20:0x23] = firm_size[0:3]

    with open(target_firm.get_abspath(), "wb") as out_firm:
        with open(temp_firm, "rb") as in_firm:
            buf = in_firm.read()
            GFH_Header[0x1C:0x20] = flash_addr.get(env.BoardConfig().get(
                "build.variant"), flash_addr['6261'])
            crc32 = zlib.crc32(buf).to_bytes(4, "little")
            GFH_Header[0x3C:] = crc32
            out_firm.write(GFH_Header)
            out_firm.write(buf)
            in_firm.close()
        out_firm.close()
        remove(temp_firm)


# Setup ENV
env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-g",
        "-fmessage-length=0",
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-fsigned-char",
        "-Wall",
        "-mthumb",
        "-mthumb-interwork",
    ],

    CFLAGS=[
        "-std=gnu11",
        "-Wno-old-style-declaration"
    ],

    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-rtti",
        "-fno-exceptions",
        "-fno-use-cxa-atexit",
        "-fno-non-call-exceptions"
    ],

    CPPDEFINES=[
        ("__BUFSIZ__", "512"),
        ("__FILENAME_MAX__", "256"),
        ("F_CPU", "$BOARD_F_CPU"),
        ("ARDUINO", 10813),
        "ARDUINO_ARCH_ARM",
        ("ARDUINO_VARIANT", '\\"%s\\"' %
         board.get("build.variant").replace('"', "")),
        ("ARDUINO_BOARD", '\\"%s\\"' % board.get("name").replace('"', ""))
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get(
            "build.core"), "mtk", "include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "mtk"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"))
    ],

    LINKFLAGS=[
        "-mthumb",
        "-mthumb-interwork",
        "-Os",
        "-Wl,--gc-sections,--relax",
        "-nostartfiles",
        "-nostdlib",
        "-nostartfiles",
        "-nodefaultlibs",
        "-u", "main"
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core"), "mtk", "lib")
    ],

    LIBS=[
        "c",
        "gcc",
        "m",
        "stdc++"
    ],

    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(gen_bin_file, "Generating $TARGET"),
            suffix=".bin"
        )
    )
)


# Flags specific to MT2503/MT6261
env.Prepend(
    CCFLAGS=[
        "-mcpu=arm7tdmi-s",
        "-mfloat-abi=soft",
    ],

    LINKFLAGS=[
        "-mcpu=arm7tdmi-s",
        "-mfloat-abi=soft",
        "-T", "linkerscript.ld",
    ],

    LIBS=[
        "mtk",
    ],
)


if board.get("build.mcu") != "MT2625" and board.get("build.newlib") == "nano":
    env.Append(
        LINKFLAGS=[
            "--specs=nano.specs",
            "-u", "_printf_float",
            "-u", "_scanf_float",
            "--specs=nosys.specs",
        ]
    )

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", board.get("build.core"))
))

env.Prepend(LIBS=libs)
