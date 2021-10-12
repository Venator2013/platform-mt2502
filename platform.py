# Copyright 2021 WAYBYTE Solutions
#
# SPDX-License-Identifier: MIT
#

from platform import system
from platformio.managers.platform import PlatformBase

class Mt2502Platform(PlatformBase):
    def configure_default_packages(self, variables, target):
        
        # configure script based on MCU type
        board_config = self.board_config(variables.get("board"))
        mcu = variables.get("board_build.mcu",
                            board_config.get("build.mcu", "MT2502"))
        
        frameworks = variables.get("pioframework", [])
        if "arduino" in frameworks:
            self.frameworks["arduino"]["package"] = "framework-arduinoststm32l0"
            self.packages["framework-mt2502arduino"]["optional"] = False
            self.packages["framework-mt2502arduino"]["optional"] = True

        return PlatformBase.configure_default_packages(self, variables,
                                                       target)
