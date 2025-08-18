@echo off
setlocal enabledelayedexpansion

rem
> _RON_kr_goals.gfx echo spriteTypes = {
> _RON_kr_goals_shine.gfx echo spriteTypes = {

set "base=%cd%"

for /r %%F in (*.png *.dds *.jpg) do (
    set "filename=%%~nF"
    set "ext=%%~xF"
    set "ext=!ext:.=!"

    set "fullpath=%%~dpF"
    set "relpath=!fullpath:%base%\=!"

    >> _RON_kr_goals.gfx echo     SpriteType = {
    >> _RON_kr_goals.gfx echo         name = "GFX_goal_!filename!"
    >> _RON_kr_goals.gfx echo         texturefile = "gfx/interface/goals/kr_import/!relpath!!filename!.!ext!"
    >> _RON_kr_goals.gfx echo     }

    >> _RON_kr_goals_shine.gfx echo     SpriteType = {
    >> _RON_kr_goals_shine.gfx echo         name = "GFX_goal_!filename!_shine"
    >> _RON_kr_goals_shine.gfx echo         texturefile = "gfx/interface/goals/kr_import/!relpath!!filename!.!ext!"
    >> _RON_kr_goals_shine.gfx echo         effectFile = "gfx/FX/buttonstate.lua"
    >> _RON_kr_goals_shine.gfx echo         animation = {
    >> _RON_kr_goals_shine.gfx echo             animationmaskfile = "gfx/interface/goals/kr_import/!relpath!!filename!.!ext!"
    >> _RON_kr_goals_shine.gfx echo             animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
    >> _RON_kr_goals_shine.gfx echo             animationrotation = -90.0
    >> _RON_kr_goals_shine.gfx echo             animationlooping = no
    >> _RON_kr_goals_shine.gfx echo             animationtime = 0.75
    >> _RON_kr_goals_shine.gfx echo             animationdelay = 0
    >> _RON_kr_goals_shine.gfx echo             animationblendmode = "add"
    >> _RON_kr_goals_shine.gfx echo             animationtype = "scrolling"
    >> _RON_kr_goals_shine.gfx echo             animationrotationoffset = { x = 0.0 y = 0.0 }
    >> _RON_kr_goals_shine.gfx echo             animationtexturescale = { x = 1.0 y = 1.0 }
    >> _RON_kr_goals_shine.gfx echo         }
    >> _RON_kr_goals_shine.gfx echo         animation = {
    >> _RON_kr_goals_shine.gfx echo             animationmaskfile = "gfx/interface/goals/kr_import/!relpath!!filename!.!ext!"
    >> _RON_kr_goals_shine.gfx echo             animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
    >> _RON_kr_goals_shine.gfx echo             animationrotation = 90.0
    >> _RON_kr_goals_shine.gfx echo             animationlooping = no
    >> _RON_kr_goals_shine.gfx echo             animationtime = 0.75
    >> _RON_kr_goals_shine.gfx echo             animationdelay = 0
    >> _RON_kr_goals_shine.gfx echo             animationblendmode = "add"
    >> _RON_kr_goals_shine.gfx echo             animationtype = "scrolling"
    >> _RON_kr_goals_shine.gfx echo             animationrotationoffset = { x = 0.0 y = 0.0 }
    >> _RON_kr_goals_shine.gfx echo             animationtexturescale = { x = 1.0 y = 1.0 }
    >> _RON_kr_goals_shine.gfx echo         }
    >> _RON_kr_goals_shine.gfx echo         legacy_lazy_load = no
    >> _RON_kr_goals_shine.gfx echo     }
)

>> _RON_kr_goals.gfx echo }
>> _RON_kr_goals_shine.gfx echo }

echo Generated _RON_kr_goals.gfx and _RON_kr_goals_shine.gfx for all files.
pause
