import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

def extract_info(filename):
    match = re.search(r'_iconica_SP_([^_]+)_(\w+)\.vstsound', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def generate_lua_script(instrument, entries):
    lua_lines = [
        f'-- HALion 7 Script for {instrument}',
        'defineInstrument = function()',
        '  local instrument = this.program',
    ]

    for idx, (artic, filename) in enumerate(entries):
        midi_channel = idx + 1
        keyswitch_note = idx  # Starting from MIDI 0 = C-2
        lua_lines.extend([
            f'  local layer_{idx} = loadLayer("{filename}")',
            f'  layer_{idx}.name = "{artic}"',
            f'  layer_{idx}.midiChannel = {midi_channel}',
            f'  layer_{idx}.keySwitch = {keyswitch_note} -- C-2 + {keyswitch_note}',
            f'  instrument:appendLayer(layer_{idx})',
        ])
    lua_lines.append('end')
    return "\n".join(lua_lines)

def generate_expression_map(instrument, entries, map_type="directional", base_note=0):
    root = ET.Element("expressionmap")
    ET.SubElement(root, "name").text = f"{instrument} Expression Map ({map_type.capitalize()})"

    for idx, (artic, filename) in enumerate(entries):
        slot = ET.SubElement(root, "slot")
        ET.SubElement(slot, "name").text = artic
        ET.SubElement(slot, "status").text = "1"
        ET.SubElement(slot, "type").text = "2" if map_type == "directional" else "1"
        ET.SubElement(slot, "data1").text = str(base_note + idx)
        ET.SubElement(slot, "data2").text = "127"
        ET.SubElement(slot, "channel").text = "1"

    return ET.tostring(root, encoding="unicode", method="xml")

def main(vstsound_folder):
    instruments = defaultdict(list)

    # Parse and group files
    for fname in os.listdir(vstsound_folder):
        if fname.endswith(".vstsound"):
            inst, artic = extract_info(fname)
            if inst and artic:
                instruments[inst].append((artic, fname))

    if not instruments:
        print("No valid VSTSound files found.")
        return

    for instrument, entries in instruments.items():
        # Sort articulations for consistency
        entries.sort(key=lambda x: x[0])

        # Generate Lua script
        lua_script = generate_lua_script(instrument, entries)
        with open(f"{instrument}.lua", "w") as f:
            f.write(lua_script)

        # Expression maps
        expr_map_dir = generate_expression_map(instrument, entries, map_type="directional")
        expr_map_attr = generate_expression_map(instrument, entries, map_type="attribute")

        with open(f"{instrument}_directional.expressionmap", "w", encoding="utf-8") as f:
            f.write(expr_map_dir)

        with open(f"{instrument}_attribute.expressionmap", "w", encoding="utf-8") as f:
            f.write(expr_map_attr)

    print("✅ All instrument scripts and expression maps generated!")

# Usage
if __name__ == "__main__":
    folder_path = "path_to_your_vstsound_folder"  # Replace this with your actual folder path
    main(folder_path)
