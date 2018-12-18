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
CORE = env.BoardConfig().get("build.core")
FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-opencpu")
assert isdir(FRAMEWORK_DIR)
CORE_DIR = join(FRAMEWORK_DIR, "cores", CORE) 

env.Append(
    CPPDEFINES=[ "CORE_"+CORE.upper(),  "_REENT_SMALL" ], # -D
    CPPPATH=[ # -I
        CORE_DIR,
        join(CORE_DIR, "include"),
        join(CORE_DIR, "ril", "inc"),
        join(CORE_DIR, "fota", "inc"),        
    ],
    CFLAGS=[
        "-mcpu=cortex-m4",
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-fsingle-precision-constant",        
        "-mthumb",
        "-mthumb-interwork", 
        "-mlong-calls",       
        "-std=c99",
        "-c", "-g", "-Os",
        "-fno-builtin",         
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-strict-aliasing",
        "-fno-common", 
        "-Wall",
        "-Wp,-w",               
        "-Wstrict-prototypes",                  
        "-Wno-implicit-function-declaration",
    ],

    LINKFLAGS=[        
        "-mcpu=%s" % env.BoardConfig().get("build.cpu") ,
        "-mfloat-abi=hard",
        "-mfpu=fpv4-sp-d16",
        "-mthumb",
        "-mthumb-interwork",   
        "-nostartfiles",     
        "-Rbuild",        
        "-Wl,--gc-sections,--relax",
        "-Wl,-wrap=malloc",
        "-Wl,-wrap=calloc",
        "-Wl,-wrap=realloc",
        "-Wl,-wrap=free"   
    ],   
    LIBPATH=[CORE_DIR],
    LDSCRIPT_PATH=join(CORE_DIR, "linkscript.ld"), 
    LIBS=[ "gcc", "m", "app_start" ], 

    UPLOADER=join(TOOL_DIR, CORE, "$PLATFORM", "coda"), 
    UPLOADERFLAGS=[ '"$BUILD_DIR/${PROGNAME}.cfg"', "--UART", "$UPLOAD_PORT", "-d" ],
    UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS',

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
        join( CORE_DIR ),
))
libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "framework", "ril"),
        join(CORE_DIR, "ril", "src")
))
env.Append( LIBS = libs )

env.Replace( HEADERTOOL = join( "$PIOHOME_DIR", "platforms", "opencpu", "builder", "frameworks", "GFH_"+CORE+".py") )
