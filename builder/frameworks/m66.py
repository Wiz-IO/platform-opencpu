# WizIO 2018 Georgi Angelov
# http://www.wizio.eu/
# https://github.com/Wiz-IO

import sys
import os
import struct
from os import listdir
from os.path import isdir, isfile, join
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder
from platformio import util

env = DefaultEnvironment()
PLATFORM = env.PioPlatform()
TOOL_DIR = PLATFORM.get_package_dir("tool-opencpu")
CORE=env.BoardConfig().get("build.core")
FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-opencpu")
assert isdir(FRAMEWORK_DIR)
CORE_DIR = join(FRAMEWORK_DIR, "cores", CORE) 

env.Append(
    CPPDEFINES=[ "CORE_"+CORE.upper() ], # -D
    CPPPATH=[ # -I
        CORE_DIR,
        join(CORE_DIR, "include"),
        join(CORE_DIR, "ril", "inc"),
        join(CORE_DIR, "fota", "inc"),        
    ],
    CFLAGS=[
        "-march=armv5te",
        "-mfloat-abi=soft",
        "-mfpu=vfp",
        "-fsingle-precision-constant",        
        "-mthumb",
        "-mthumb-interwork",        
        "-std=c99",
        "-O0",  
        "-Wall",
        "-fno-builtin",
        "-Wstrict-prototypes",
        "-Wp,-w",           
    ],

    LINKFLAGS=[        
        "-march=armv5te",
        "-mfloat-abi=soft",
        "-mfpu=vfp",
        "-mthumb",
        "-mthumb-interwork",   
        "-nostartfiles",     
        "-Rbuild",        
        "-Wl,--gc-sections,--relax", 
    ],
    LIBPATH=[CORE_DIR],
    LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"),    
    LIBS=[ "gcc", "m", "app_start" ], 

    UPLOADER=join(".", TOOL_DIR, "QFlash_V4.0", "QFlash_V4.0"), # We are waithing Quectel for console uploader
    UPLOADERFLAGS=[], # https://ss64.com/nt/start.html
    UPLOADCMD='START /D ' + TOOL_DIR + '\\QFlash_V4.0 /W QFlash_V4.0.exe', 

    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O", 
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".dat"
        ),     
        GFH=Builder( # Add Mediatek Header
            action=env.VerboseAction(" ".join([
                '"$PYTHONEXE"',
                '"$HEADERTOOL"',
                "$SOURCES",
                "$TARGET"
            ]), "Adding Header"),
            suffix=".bin"
        )        
    )#dict
)    

libs = []
libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "framework"),
        join( CORE_DIR )
))
libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "framework", "ril"),
        join(CORE_DIR, "ril", "src")
))
libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "framework", "fota"),
        join(CORE_DIR, "fota", "src")
))
env.Append( LIBS=libs )

env.Replace( HEADERTOOL = join( "$PIOHOME_DIR", "platforms", "opencpu", "builder", "frameworks", "GFH_"+CORE+".py") )

