import os
import re
import xml.etree.ElementTree as ET

def extract_info(filename):
    match = re.search(r'_iconica_SP_([^_]+)_(\w+)\.vstsound', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def generate_lua_script(entries):
    lua_lines = [
        '-- HALion 7 Multi-layer Instrument Auto-Generated Script',
        'defineInstrument = function()',
        '  local instrument = this.program',
    ]
    
    for idx, (inst, artic, filename) in enumerate(entries):
        midi_channel = idx + 1
        keyswitch_note = idx  # Starting from C-2 which is MIDI note 0
        lua_lines.extend([
            f'  local layer_{idx} = loadLayer("{filename}")',
            f'  layer_{idx}.name = "{artic}"',
            f'  layer_{idx}.midiChannel = {midi_channel}',
            f'  layer_{idx}.keySwitch = {keyswitch_note} -- C-2 + {keyswitch_note}',
            f'  instrument:appendLayer(layer_{idx})',
        ])
    lua_lines.append('end')

    return "\n".join(lua_lines)

def midi_note_name(note_number):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_number // 12) - 2
    return f"{notes[note_number % 12]}{octave}"

def generate_expression_map(entries, base_note=0):
    root = ET.Element("expressionmap")
    ET.SubElement(root, "name").text = f"{entries[0][0]} Expression Map"

    for idx, (inst, artic, filename) in enumerate(entries):
        slot = ET.SubElement(root, "slot")
        ET.SubElement(slot, "name").text = artic
        ET.SubElement(slot, "status").text = "1"
        ET.SubElement(slot, "type").text = "noteon"
        ET.SubElement(slot, "data1").text = str(base_note + idx)
        ET.SubElement(slot, "data2").text = "127"
        ET.SubElement(slot, "channel").text = "1"

    return ET.tostring(root, encoding="unicode", method="xml")

def main(vstsound_folder):
    entries = []
    for fname in os.listdir(vstsound_folder):
        if fname.endswith(".vstsound"):
            inst, artic = extract_info(fname)
            if inst and artic:
                entries.append((inst, artic, fname))

    if not entries:
        print("No valid files found.")
        return

    # Generate LUA script
    lua_script = generate_lua_script(entries)
    with open("generated_instrument.lua", "w") as f:
        f.write(lua_script)

    # Generate Expression Map
    expression_map = generate_expression_map(entries)
    with open("expression_map.expressionmap", "w", encoding="utf-8") as f:
        f.write(expression_map)

    print("✅ Lua script and Expression Map generated!")

# Call the script
if __name__ == "__main__":
    folder_path = "path_to_your_vstsound_folder"  # CHANGE THIS
    main(folder_path)

