# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Autor: WizIO 2018 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO
# 
# Support: Quectel
#   https://www.quectel.com/support/contact.htm
#
# Support: Comet Electronics 
#   https://www.comet.bg/?cid=92
#

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)
from colorama import Fore, Back, Style

env = DefaultEnvironment()
platform = env.PioPlatform()
print(Fore.GREEN + '----- Quectel OpenCPU '+env.BoardConfig().get("build.core").upper()+" 2018 Georgi Angelov -----")
#print env.Dump()

env.Replace(
    BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
    AR="arm-none-eabi-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    GDB="arm-none-eabi-gdb",
    CXX="arm-none-eabi-g++",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",
    ARFLAGS=["rc"],
    SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
    SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
    PROGSUFFIX=".elf",  
    UPLOADNAME=join("$BUILD_DIR", "${PROGNAME}.cfg"),
)

####################################################
# Target: Build executable and linkable program
####################################################
elf = None
elf = env.BuildProgram()
src = env.GFH(
    join("$BUILD_DIR", "${PROGNAME}"),
    env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), elf),    
)
AlwaysBuild( env.Alias("nobuild", src) )

####################################################
# Target: Upload BC66
####################################################
target_upload = env.Alias("upload", src, [
    env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
    env.VerboseAction("",  "--- WAITING MODULE ---"),
    env.VerboseAction("$UPLOADCMD", "RESET BOARD TO START FLASHING"),
    env.VerboseAction("",  "POWER ON BOARD"),

])


AlwaysBuild( target_upload )

Default( src )
