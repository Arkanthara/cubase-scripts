import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import argparse
# from gooey import Gooey, GooeyParser  # GUI option (commented out)

PREFERRED_ORDER = [
    "Legato", "Sustain", "Marcato", "Accent",
    "Tremolo", "Trill", "Flutter",
    "Pizzicato", "Staccato", "Spiccato", "Tenuto", "Portato",
    "Sfz", "Sffz",
    "Rip", "Cluster", "FX", "Glissando", "Fall"
]

ARTICULATION_CATEGORY = {
    "Legato": "Long", "Sustain": "Long", "Marcato": "Long", "Accent": "Long",
    "Tremolo": "Long", "Trill": "Ornament", "Flutter": "Ornament",
    "Pizzicato": "Short", "Staccato": "Short", "Spiccato": "Short", "Tenuto": "Short", "Portato": "Short",
    "Sfz": "Accent", "Sffz": "Accent",
    "Rip": "FX", "Cluster": "FX", "FX": "FX", "Glissando": "FX", "Fall": "FX"
}

CATEGORY_COLORS = {
    "Long": "0,0,255",       # Blue
    "Short": "0,128,0",      # Green
    "Ornament": "255,165,0", # Orange
    "Accent": "128,0,128",   # Purple
    "FX": "255,0,0",         # Red
    "Unknown": "128,128,128" # Gray
}

def articulation_sort_key(artic_name):
    try:
        return (0, PREFERRED_ORDER.index(artic_name))
    except ValueError:
        return (1, artic_name.lower())  # Unlisted articulations go last

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

    entries.sort(key=lambda x: articulation_sort_key(x[0]))

    for idx, (artic, filename) in enumerate(entries):
        slot = ET.SubElement(root, "slot")
        ET.SubElement(slot, "name").text = artic
        ET.SubElement(slot, "status").text = "1"
        ET.SubElement(slot, "type").text = "2" if map_type == "directional" else "1"
        ET.SubElement(slot, "data1").text = str(base_note + idx)
        ET.SubElement(slot, "data2").text = "127"
        ET.SubElement(slot, "channel").text = "1"

        # Technique and Color
        category = ARTICULATION_CATEGORY.get(artic, "Unknown")
        color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["Unknown"])

        ET.SubElement(slot, "technique").text = category
        ET.SubElement(slot, "color").text = color  # RGB color tag

    return ET.tostring(root, encoding="unicode", method="xml")


# @Gooey(program_name="Iconica SP Script Generator")  # Uncomment for GUI
def main():
    parser = argparse.ArgumentParser(description="Generate HALion Lua scripts and Cubase expression maps from Iconica SP VSTSound files.")
    
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        required=True, 
        help="Path to folder containing Iconica SP .vstsound files"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        default="output", 
        help="Output folder to save generated Lua and expression map files"
    )
    
    args = parser.parse_args()
    input_folder = args.input
    output_folder = args.output

    if not os.path.isdir(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)

    instruments = defaultdict(list)

    # Parse and group valid Iconica SP files
    for fname in os.listdir(input_folder):
        if fname.endswith(".vstsound"):
            inst, artic = extract_info(fname)
            if inst and artic:
                instruments[inst].append((artic, fname))

    if not instruments:
        print("⚠️ No valid Iconica SP VSTSound files found.")
        return

    for instrument, entries in instruments.items():
        entries.sort(key=lambda x: x[0])

        # Generate Lua script
        lua_script = generate_lua_script(instrument, entries)
        with open(os.path.join(output_folder, f"{instrument}.lua"), "w") as f:
            f.write(lua_script)

        # Expression maps
        expr_map_dir = generate_expression_map(instrument, entries, map_type="directional")
        expr_map_attr = generate_expression_map(instrument, entries, map_type="attribute")

        with open(os.path.join(output_folder, f"{instrument}_directional.expressionmap"), "w", encoding="utf-8") as f:
            f.write(expr_map_dir)

        with open(os.path.join(output_folder, f"{instrument}_attribute.expressionmap"), "w", encoding="utf-8") as f:
            f.write(expr_map_attr)

    print(f"✅ Done! Files saved to: {os.path.abspath(output_folder)}")

if __name__ == "__main__":
    main()
