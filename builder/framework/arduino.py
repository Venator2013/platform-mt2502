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


def gen_vpx_file(target, source, env):
    cmd = ["$OBJCOPY"]
    (target_firm, ) = target
    (target_elf, ) = source

    suffix = b'\x04\x00\x00\x00\n\x00\x00\x00D\x00e\x00m\x00o\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\xff\xff\xff\xff\x03\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x04\x00\x00\x00\x00\x00\x01\x00\x16\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x00\x18\x00\x00\x00\xde\x07\x00\x00\x03\x00\x00\x00\x1c\x00\x00\x00\x0f\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x18\x00\x00\x00\xde\x07\x00\x00\x05\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x04\x00\x00\x00\x00\x04\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x04\x00\x00\x00\x00\x00\xc4\t!\x00\x00\x00\x04\x00\x00\x00\x06\x00\x00\x00#\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00"\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x002\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00/\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x001\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00)\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00*\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00-\x00\x00\x00\x04\x00\x00\x00\xff\xff\xff\xff.\x00\x00\x00\x02\x00\x00\x00\x00\x00\x01\x00\x00\x00\x1c\x00\x00\x00M\x00e\x00d\x00i\x00a\x00T\x00e\x00k\x00 \x00I\x00n\x00c\x00.\x00\x00\x00%\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x003\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\n\x00\x00\x001234567890\x17\x00\x00\x00\x10\x00\x00\x00c\x00o\x00n\x00t\x00e\x00n\x00t\x00\x00\x00\x19\x00\x00\x00>\x00\x00\x00\x01\x00\x00\x00\n\x00\x00\x00D\x00e\x00m\x00o\x00\x00\x00\x02\x00\x00\x00\n\x00\x00\x00D\x00e\x00m\x00o\x00\x00\x00\x03\x00\x00\x00\n\x00\x00\x00D\x00e\x00m\x00o\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xd0\x00\x00\x00\x88\x13\x00\x00\x01\x00\x00\x00\x89\x13\x00\x00\x01\x00\x00\x00\x8a\x13\x00\x00\x01\x00\x00\x00\x8b\x13\x00\x00\x01\x00\x00\x00\x8c\x13\x00\x00\x01\x00\x00\x00\x8d\x13\x00\x00\x01\x00\x00\x00\x8e\x13\x00\x00\x01\x00\x00\x00\x8f\x13\x00\x00\x01\x00\x00\x00\x90\x13\x00\x00\x01\x00\x00\x00\x91\x13\x00\x00\x01\x00\x00\x00\x92\x13\x00\x00\x01\x00\x00\x00\x93\x13\x00\x00\x01\x00\x00\x00\x94\x13\x00\x00\x01\x00\x00\x00\x95\x13\x00\x00\x01\x00\x00\x00\x96\x13\x00\x00\x01\x00\x00\x00\x97\x13\x00\x00\x01\x00\x00\x00\x98\x13\x00\x00\x01\x00\x00\x00\x99\x13\x00\x00\x01\x00\x00\x00\x9a\x13\x00\x00\x01\x00\x00\x00\x9b\x13\x00\x00\x01\x00\x00\x00\x9c\x13\x00\x00\x01\x00\x00\x00\x9d\x13\x00\x00\x01\x00\x00\x00\x9e\x13\x00\x00\x01\x00\x00\x00\x9f\x13\x00\x00\x01\x00\x00\x00\xa0\x13\x00\x00\x01\x00\x00\x00\xa1\x13\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb4VDE10\x01\x00\x00\x00LV)\xfb\xed\xfe\xb6\xd0\x9e\xa6\xe0\xcb\xb3\x122\xa6\xff8\xdd\xf5\xfc\xb2i2X\xe1\x10\x9dw}\x19\xdd;0V*\x92\x9bo\xf8\x0f\xf0\xa0 "\xd9\x12$\x01f\xe3\x0f\xc1\n\xff\xa5\xae\x9a\xeb\xae4\x81\xed\xbb'

    # copy object file
    temp_firm = dirname(target_firm.get_abspath()) + "/temp.bin"
    cmd.extend(["-O", "binary"])
    cmd.append(target_elf.get_abspath())
    cmd.append(temp_firm)
    env.Execute(env.VerboseAction(" ".join(cmd), " "))

    with open(target_firm.get_abspath(), "wb") as out_firm:
        with open(temp_firm, "rb") as in_firm:
            buf = in_firm.read()
            out_firm.write(buf)
            in_firm.close()
            out_firm.write(b'\xff')
        out_firm.close()
        # remove(temp_firm)


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
            action=env.VerboseAction(gen_vpx_file, "Generating $TARGET"),
            suffix=".vpx"
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


if board.get("build.newlib") == "nano":
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

variants_dir = join(FRAMEWORK_DIR, "variants")

if "build.variants_dir" in env.BoardConfig():
    variants_dir = join(
        "$PROJECT_DIR", env.BoardConfig().get("build.variants_dir"))

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(variants_dir, env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(variants_dir, env.BoardConfig().get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", board.get("build.core"))
))

env.Prepend(LIBS=libs)
