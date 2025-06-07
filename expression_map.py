import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import argparse

ARTICULATION_CATEGORY = {
    # Long
    "Legato": "Long", "Sustain": "Long", "Bisbigliando": "Long", "Pres De La Table": "Long",
    "Harmonics": "Long", "Vibrato": "Long",

    # Short
    "Staccato": "Short", "Staccatissimo": "Short", "Hit": "Short", "Hit Open": "Short", "Single Hits": "Short",
    "Palm": "Short", "Palm Finger": "Short", "Palm Bass": "Short", "Finger Tap": "Short", "Finger": "Short",
    "Muted": "Short", "Open": "Short", "Slap": "Short", "Soft Mallet": "Short", "Medium Mallet": "Short",

    # Accent
    "Marcato": "Accent", "Accent": "Accent", "Fortepiano": "Accent", 
    "Crescendo Long": "Accent", "Crescendo Short": "Accent",
    "Roll Crescendo Long": "Accent", "Roll Crescendo Short": "Accent",
    "Roll Diminuendo": "Accent", "Roll Decrescendo": "Accent",
    "Decrescendo": "Accent", "Swell Long": "Accent", "Swell Short": "Accent",
    "Crescendo": "Accent", "Crescendo Short Mute": "Accent", "Crescendo Long Mute": "Accent",
    "Crescendo Short Choke": "Accent", "Crescendo Long Choke": "Accent",

    # Ornament
    "Trills ST": "Ornament", "Trills WT": "Ornament", "Trills HT": "Ornament", "Glissando": "Ornament",
    "Gliss Major": "Ornament", "Gliss Minor": "Ornament", "Gliss Pentatonic": "Ornament",
    "Gliss Whole Tone C": "Ornament", "Gliss Whole Tone C#": "Ornament",
    "Roll Hit": "Ornament", "Roll Open": "Ornament", "Roll Open Hit": "Ornament",
    "Roll": "Ornament", "Tremolo": "Ornament",

    # FX
    "Rip": "FX", "Cluster": "FX", "FX": "FX", "Fall": "FX", "Scratch": "FX",
    "Choke": "FX", "Choke Slow": "FX", "Roll Choke": "FX", "Mute": "FX", "Damped": "FX"
}

# Compile a reusable regex pattern for all articulation starters
ARTICULATION_REGEX = re.compile(
    r"(.+?)\s+(" + "|".join(key.split(" ")[0] for key in ARTICULATION_CATEGORY.keys()) + r")", re.IGNORECASE
)

print(ARTICULATION_REGEX)

CATEGORY_COLORS = {
    "Long": "0,0,255",       # Blue
    "Short": "0,128,0",      # Green
    "Ornament": "255,165,0", # Orange
    "Accent": "128,0,128",   # Purple
    "FX": "255,0,0",         # Red
    "Unknown": "128,128,128" # Gray
}


def build_categorized_articulation_dict(folder_path, category_map):
    instrument_dict = {}

    for file in os.listdir(folder_path):
        if not file.endswith(".vstsound"):
            continue
        match = re.search(r"_Iconica_SP_(.+)\.vstsound$", file)
        if not match:
            continue

        name_part = match.group(1).replace("_", " ").strip()
        match2 = ARTIC_REGEX.match(name_part)
        if match2:
            instrument = match2.group(1).strip()
            articulation = match2.group(2).strip()
        else:
            parts = name_part.split()
            instrument = " ".join(parts[:-1])
            articulation = parts[-1]

        category = category_map.get(articulation, "Unknown")

        if instrument not in instrument_dict:
            instrument_dict[instrument] = {}
        instrument_dict[instrument][articulation] = category

    return instrument_dict


def generate_expression_map(instrument, entries, instrument_map, map_type="directional", base_note=0):
    root = ET.Element("expressionmap")
    ET.SubElement(root, "name").text = f"{instrument} Expression Map ({map_type.capitalize()})"

    entries.sort(key=lambda x: articulation_sort_key(x[0], instrument_map[instrument]))

    for idx, (artic, filename) in enumerate(entries):
        slot = ET.SubElement(root, "slot")
        ET.SubElement(slot, "name").text = artic
        ET.SubElement(slot, "status").text = "1"
        ET.SubElement(slot, "type").text = "2" if map_type == "directional" else "1"
        ET.SubElement(slot, "data1").text = str(base_note + idx)
        ET.SubElement(slot, "data2").text = "127"
        ET.SubElement(slot, "channel").text = "1"

        category = ARTICULATION_CATEGORY.get(artic, "Unknown")
        color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["Unknown"])

        ET.SubElement(slot, "technique").text = category
        ET.SubElement(slot, "color").text = color

    return ET.tostring(root, encoding="unicode", method="xml")

def main():
    parser = argparse.ArgumentParser(description="Generate Cubase expression maps from Iconica SP .vstsound files")
    parser.add_argument("-i", "--input", required=True, help="Input folder containing .vstsound files")
    parser.add_argument("-o", "--output", default="output", help="Output folder")
    args = parser.parse_args()


    for file in os.listdir(args.input):
        if file.endswith(".vstsound"):
            instrument, artic = match_instrument_and_articulation(file, instrument_map)
            if instrument and artic:
                instruments[instrument].append((artic, file))
            else:
                print(f"⚠️ Could not match: {file}")

    os.makedirs(args.output, exist_ok=True)

    for instrument, entries in instruments.items():
        expr_map_dir = generate_expression_map(instrument, entries, instrument_map, map_type="directional")
        expr_map_attr = generate_expression_map(instrument, entries, instrument_map, map_type="attribute")

        with open(os.path.join(args.output, f"{instrument}_directional.expressionmap"), "w", encoding="utf-8") as f:
            f.write(expr_map_dir)

        with open(os.path.join(args.output, f"{instrument}_attribute.expressionmap"), "w", encoding="utf-8") as f:
            f.write(expr_map_attr)

    print(f"✅ Expression maps generated in: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
