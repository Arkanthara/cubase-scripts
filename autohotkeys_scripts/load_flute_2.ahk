
; Auto-generated AHK v2 script to load Flute 2 in HALion

;#NoEnv
SendMode("Input")
;SetWorkingDir(A_ScriptDir)


CoordMode("Mouse", "Screen") ; Coordinates relative to the whole screen
; Activate HALion window
WinActivate("HALion 7")
Sleep(200)

Click(256, 155)
Sleep(200)

Click(158, 138)
Sleep(200)

Send("Init{Enter}")
Sleep(200)

Click(100, 310) ; double click
Sleep(200)

Send("{Enter}")
Sleep(200)

; Focus search bar
Click(2800, 183)
Sleep(200)

; Type instrument name
Send("Flute 2{Enter}")
Sleep(500)

; Get only matched results
Click(2467, 250)
Sleep(200)

; Select all results
Click(2500, 358) ; Sort
Sleep(200)
Click(2500, 383) ; First element
Sleep(200)
Click(2500, 358) ; Sort
Sleep(200)

; Hold Shift and click last item
Send("{Shift down}")
Sleep(200)
Click(2500, 383)
Sleep(200)
Send("{Shift up}")
Sleep(200)


MouseMove(2500, 383)
Sleep(200)

DllCall("user32.dll\mouse_event", "UInt", 0x0002, "UInt", 0, "UInt", 0, "UInt", 0, "UPtr", 0)  ; left down
Sleep(200)

MouseMove(100, 250, 20)
Sleep(200)

DllCall("user32.dll\mouse_event", "UInt", 0x0004, "UInt", 0, "UInt", 0, "UInt", 0, "UPtr", 0)  ; left up
Sleep(1000)

; Save Multi preset
Click(274, 154)
Sleep(200)
Send("Flute 2_Multi")
Sleep(200)
Send("{Enter}")
Sleep(200)
Send("{Enter}")
MouseMove(2530, 250)
Sleep(200)
Click(2530, 250)
Sleep(200)
