
import argparse
import os

INSTRUMENTS = [
    "Violins I", "Violins II", "Violas", "Celli", "Basses",
    "Piccolo", "Flute 1", "Flute 2", "Oboe 1", "Oboe 2",
    "English Horn", "Clarinet 1", "Clarinet 2", "Bass Clarinet",
    "Bassoon 1", "Bassoon 2", "Contra Bassoon", "Horn", "Horns",
    "Trumpet", "Trumpets", "Trombone", "Trombones", "Euphonium", "Tuba",
    "Bell Tree", "Castanets", "Celesta", "Chimes", "Cowbells", "Crotales",
    "Cymbal 18", "Cymbal 20", "Glockenspiel", "Harp", "Harp Pres De",
    "Marimba", "Piatti", "Snare 1", "Snare 2", "Snare 3", "Snare 4", "Tam Tam",
    "Tambourine 1", "Tambourine 2", "Timpani", "Toms", "Toms Timpani", "Triangle", "Vibraphone",
    "Vibraslap", "Gran Cassa", "Temple Blocks", "Wood Blocks", "Xylophone", "Congas", "Bongos",
]

AHK_TEMPLATE = """
; Auto-generated AHK v2 script to load {instrument} in HALion

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

Send("Init{{Enter}}")
Sleep(200)

Click(100, 310) ; double click
Sleep(200)

Send("{{Enter}}")
Sleep(200)

; Focus search bar
Click(2800, 183)
Sleep(200)

; Type instrument name
Send("{instrument}{{Enter}}")
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
Send("{{Shift down}}")
Sleep(200)
Click(2500, 383)
Sleep(200)
Send("{{Shift up}}")
Sleep(200)


MouseMove(2500, 383)
Sleep(200)

DllCall("user32.dll\\mouse_event", "UInt", 0x0002, "UInt", 0, "UInt", 0, "UInt", 0, "UPtr", 0)  ; left down
Sleep(200)

MouseMove(100, 250, 20)
Sleep(200)

DllCall("user32.dll\\mouse_event", "UInt", 0x0004, "UInt", 0, "UInt", 0, "UInt", 0, "UPtr", 0)  ; left up
Sleep(1000)

; Save Multi preset
Click(274, 154)
Sleep(200)
Send("{instrument}_Multi")
Sleep(200)
Send("{{Enter}}")
Sleep(200)
Send("{{Enter}}")
MouseMove(2530, 250)
Sleep(200)
Click(2530, 250)
Sleep(200)
"""


    # ; Drag and drop to multi slot
    # MouseMove(2500, 383)
    # Sleep(100)
    # MouseDown("L")
    # Sleep(100)
    # MouseMove(100, 250, 20)
    # Sleep(100)
    # MouseUp("L")
    # Sleep(500)
#
# Click(3050, 270)
# Sleep(1000)
# MouseMove(2500, 383)
# Sleep(200)
# Click(2500, 383)
# Sleep(200)
# Send("{{Blind}}{{Ctrl down}}a{{Ctrl up}}")

def generate_ahk_files(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for instrument in INSTRUMENTS:
        filename = f"load_{instrument.replace(' ', '_').lower()}.ahk"
        content = AHK_TEMPLATE.format(instrument=instrument)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Generate AHK scripts for Iconica instrument loading in HALion.")
    parser.add_argument("output_dir", type=str, help="Folder to store generated .ahk scripts.")
    args = parser.parse_args()

    generate_ahk_files(args.output_dir)

if __name__ == "__main__":
    main()

