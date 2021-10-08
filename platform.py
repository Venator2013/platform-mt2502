# Copyright 2021 WAYBYTE Solutions
#
# SPDX-License-Identifier: MIT
#

from platform import system
from platformio.managers.platform import PlatformBase

class MT2502Platform(PlatformBase):
    def configure_default_packages(self, variables, target):
        
        # configure script based on MCU type
        board_config = self.board_config(variables.get("board"))
        mcu = variables.get("board_build.mcu",
                            board_config.get("build.mcu", "MT2502"))
        if mcu not in ("MT2502"):
            self.frameworks["arduino"]["script"] = "builder/framework/%s/arduino.py" % (
                mcu.lower())

        return PlatformBase.configure_default_packages(self, variables,
                                                       target)
