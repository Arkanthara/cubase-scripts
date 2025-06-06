import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
import argparse


INSTRUMENTS = [
    "Violins I", "Violins II", "Violas", "Celli", "Basses",
    "Piccolo", "Flute 1", "Flute 2", "Oboe 1", "Oboe 2",
    "English Horn", "Clarinet 1", "Clarinet 2", "Bass Clarinet",
    "Bassoon 1", "Bassoon 2", "Contra Bassoon", "Horn", "Horns",
    "Trumpet", "Trumpets", "Trombone", "Trombones", "Euphonium", "Tuba",
    "Bell Tree", "Castanets", "Celesta", "Chimes", "Cowbells", "Crotales",
    "Cymbal 18 Inch", "Cymbal 20 Inch", "Glockenspiel", "Harp", "Harp Pres De",
    "Marimba", "Piatti", "Snare 1", "Snare 2", "Snare 3", "Snare 4", "Tam Tam",
    "Tambourine 1", "Tambourine 2", "Timpani", "Toms", "Toms Timpani", "Triangle", "Vibraphone",
    "Vibraslap", "Gran Cassa", "Temple Blocks", "Wood Blocks", "Xylophone", "Congas", "Bongos",
]
def create_instrument_pattern():
    list_instruments = []
    for i in INSTRUMENTS:
        instrument = ""
        parts = i.split(" ")
        if len(parts) > 1:
            match parts[-1]:
                case "I":
                    instrument = parts[0] + "1"
                case "II":
                    instrument = parts[0] + "2"
                case digit if digit.isdigit():
                    instrument = parts[0] + digit
                case _:
                    instrument = "_".join(parts)
        else:
            instrument = parts[0]
        list_instruments.append(instrument)
    return list_instruments


def get_instrument(folder_path):
    instrument_dict = {}
    for file in os.listdir(folder_path):
        if not file.endswith(".vstsound"):
            continue
        search = re.search(r"_Iconica_SP_(.+)\.vstsound", file)
        if search:
            match = re.match(r"^(" + "|".join(sorted(create_instrument_pattern(), key=len, reverse=True)) + r")_(.+)$", search.group(1))
            if match:
                if match.group(1) not in instrument_dict.keys():
                    instrument_dict[match.group(1)] = []
                instrument_dict[match.group(1)].append(match.group(2))
    return instrument_dict




# def generate_expression_map(instrument, folder_path, map_type="directional"):
#     instrument_dict = get_instrument(folder_path)
#
#     if instrument not in instrument_dict:
#         raise ValueError(f"Instrument '{instrument}' not found in folder '{folder_path}'.")
#
#     sorted_artics = sorted(instrument_dict[instrument], key=lambda x: x.lower())
#
#     root = ET.Element("expressionmap")
#
#     ET.SubElement(root, "name").text = f"{instrument} Expression Map ({map_type.capitalize()})"
#     ET.SubElement(root, "description").text = f"Auto-generated expression map for {instrument}"
#     ET.SubElement(root, "uuid").text = "{" + str(uuid.uuid4()).upper() + "}"
#
#     # Articulations section
#     articulations = ET.SubElement(root, "articulations")
#
#     for i in range(len(sorted_artics)):
#         artic = sorted_artics[i]
#         keyswitch_note = i  # Start from MIDI note 0 (C-2)
#
#         slot = ET.SubElement(articulations, "slot")
#         ET.SubElement(slot, "name").text = artic
#         ET.SubElement(slot, "type").text = "2" if map_type == "directional" else "1"
#         ET.SubElement(slot, "status").text = "1"
#
#         trigger = ET.SubElement(slot, "trigger")
#         ET.SubElement(trigger, "type").text = "note"
#         ET.SubElement(trigger, "data1").text = str(keyswitch_note)  # MIDI note number
#         ET.SubElement(trigger, "data2").text = "127"
#         ET.SubElement(trigger, "channel").text = "1"
#
#     # Remote keyswitch mapping (optional but recommended)
#     remote = ET.SubElement(root, "remote")
#     ET.SubElement(remote, "triggerController").text = "-1"
#     ET.SubElement(remote, "triggerChannel").text = "1"
#     ET.SubElement(remote, "triggerNote").text = "0"
#
#     return ET.tostring(root, encoding="unicode", method="xml")


def create_expression_maps(instrument_name, folder_path):
    instrument_dict = get_instrument(folder_path)
    articulations = instrument_dict[instrument_name]
    def create_xml_root():
        root = ET.Element('InstrumentMap')
        ET.SubElement(root, 'string', name='name', value=instrument_name, wide='true')
        return root

    def create_slot_visuals_section():
        member = ET.Element('member', name='slotvisuals')
        ET.SubElement(member, 'int', name='ownership', value='1')
        visuals_list = ET.SubElement(member, 'list', name='obj', type='obj')
        return member, visuals_list

    def create_slots_section(articulations, articulation_type):
        member = ET.Element('member', name='slots')
        ET.SubElement(member, 'int', name='ownership', value='1')
        slots_list = ET.SubElement(member, 'list', name='obj', type='obj')
        channel = 0
        port = 0

        for i, name in enumerate(articulations):
            channel = i % 16
            port = i // 16  # Cubase doesn't officially expose ports this way, but placeholder
            status = 0x90  # Note On
            
            # PSoundSlot
            slot = ET.SubElement(slots_list, 'obj', attrib={'class': 'PSoundSlot', 'ID': str(1500000000 + i)})

            
            # Remote trigger
            remote = ET.SubElement(slot, 'obj', attrib={'class': 'PSlotThruTrigger', 'name': 'remote', 'ID': str(1300000000 + i)})
            # ET.SubElement(remote, 'int', name='status', value=str(status))
            ET.SubElement(remote, 'int', name='status', value="144")
            ET.SubElement(remote, 'int', name='data1', value=str(i))  # MIDI note 0 = C-2

            # Action
            action = ET.SubElement(slot, 'obj', attrib={'class': 'PSlotMidiAction', 'name': 'action', 'ID': str(1400000000 + i)})
            ET.SubElement(action, 'int', name='version', value='600')

            # NoteChanger
            noteChanger = ET.SubElement(action, 'member', name='noteChanger')
            ET.SubElement(noteChanger, 'int', name='ownership', value='1')
            nc_list = ET.SubElement(noteChanger, 'list', name='obj', type='obj')
            changer = ET.SubElement(nc_list, 'obj', attrib={'class': 'PSlotNoteChanger', 'ID': str(1401136000 + i)})
            ET.SubElement(changer, 'int', name='channel', value=str(channel))
            ET.SubElement(changer, 'float', name='velocityFact', value='1')
            ET.SubElement(changer, 'float', name='lengthFact', value='1')
            ET.SubElement(changer, 'int', name='minVelocity', value='0')
            ET.SubElement(changer, 'int', name='maxVelocity', value='127')
            ET.SubElement(changer, 'int', name='transpose', value='0')
            ET.SubElement(changer, 'int', name='minPitch', value='0')
            ET.SubElement(changer, 'int', name='maxPitch', value='127')

            ET.SubElement(action, 'member', name='midiMessages').append(ET.Element('int', name='ownership', value='1'))
            ET.SubElement(action, 'int', name='channel', value=str(channel))
            ET.SubElement(action, 'float', name='velocityFact', value='1')
            ET.SubElement(action, 'float', name='lengthFact', value='1')
            ET.SubElement(action, 'int', name='minVelocity', value='0')
            ET.SubElement(action, 'int', name='maxVelocity', value='127')
            ET.SubElement(action, 'int', name='transpose', value='0')
            ET.SubElement(action, 'int', name='maxPitch', value='127')
            ET.SubElement(action, 'int', name='minPitch', value='0')
            ET.SubElement(action, 'int', name='key', value='-1')

            # sv visuals
            sv = ET.SubElement(slot, 'member', name='sv')
            ET.SubElement(sv, 'int', name='ownership', value='2')
            sv_list = ET.SubElement(sv, 'list', name='obj', type='obj')
            vis = ET.SubElement(sv_list, 'obj', attrib={'class': 'USlotVisuals', 'ID': str(1309870000 + i)})
            ET.SubElement(vis, 'int', name='displaytype', value='1')
            ET.SubElement(vis, 'int', name='articulationtype', value=str(articulation_type))  # 0 = Attribute, 1 = Direction
            ET.SubElement(vis, 'int', name='symbol', value='73')
            ET.SubElement(vis, 'string', name='text', value=name, wide='true')
            ET.SubElement(vis, 'string', name='description', value=name, wide='true')
            ET.SubElement(vis, 'int', name='group', value='0')

            ET.SubElement(slot, 'member', name='name').append(
                ET.Element('string', name='s', value=name, wide='true')
            )
            ET.SubElement(slot, 'int', name='color', value='1')

        return member

    def add_controller_section(root):
        member = ET.SubElement(root, 'member', name='controller')
        ET.SubElement(member, 'int', name='ownership', value='1')

    def build_map(articulation_type):
        root = create_xml_root()
        visuals_member, visuals_list = create_slot_visuals_section()
        root.append(visuals_member)
        for i, name in enumerate(articulations):
            vis = ET.SubElement(visuals_list, 'obj', attrib={'class': 'USlotVisuals', 'ID': str(1309870000 + i)})
            ET.SubElement(vis, 'int', name='displaytype', value='1')
            ET.SubElement(vis, 'int', name='articulationtype', value=str(articulation_type))
            ET.SubElement(vis, 'int', name='symbol', value='73')
            ET.SubElement(vis, 'string', name='text', value=name, wide='true')
            ET.SubElement(vis, 'string', name='description', value=name, wide='true')
            ET.SubElement(vis, 'int', name='group', value='0')
        root.append(create_slots_section(articulations, articulation_type))
        add_controller_section(root)
        return ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Generate both maps
    expression_map_attribute = build_map(articulation_type=0)
    expression_map_directional = build_map(articulation_type=1)

    return expression_map_directional, expression_map_attribute

def save_expression_map(xml_string, instrument, map_type, output_dir):
    if xml_string == None:
        return
    filename = f"{instrument}_{map_type}.expressionmap"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_string)
    print(f"Saved: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Generate Cubase expression maps from Iconica folders.")
    parser.add_argument("folder", help="Path to the folder containing .vstsound files")
    parser.add_argument("-o", "--output", default="expressionmaps", help="Output directory for expression maps")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    
    instrument_dict = get_instrument(args.folder)
    
    for instrument in instrument_dict:
        directional, attribute= create_expression_maps(instrument, args.folder)
        save_expression_map(directional, instrument, "directional", args.output)
        save_expression_map(attribute, instrument, "attribute", args.output)

if __name__ == "__main__":
    main()
 
# Used to read from pdf all instruments
# import fitz  # PyMuPDF
# import re
#
# def extract_bold_instruments(pdf_path):
#     doc = fitz.open(pdf_path)
#     instruments = set()
#
#     for page in doc:
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     font = span.get("font", "").lower()
#                     text = span.get("text", "").strip()
#
#                     # Check for bold font
#                     if "bold" in font and is_valid_instrument_name(text):
#                         instruments.add(text)
#
#     return sorted(instruments)
#
# def is_valid_instrument_name(text):
#     # Must be more than 1 word and not a punctuation or numeric-only line
#     return (
#         len(text) > 1 and
#         not re.fullmatch(r"[^\w\s]+", text) and
#         not re.fullmatch(r"\d+", text)
#     )   
