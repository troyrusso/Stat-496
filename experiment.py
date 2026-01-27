# experiment.py
import constants

for group, name in constants.ALL_NAMES:
    for bg_label, bg_text in constants.BACKGROUNDS:
        for scen_label, scen_text in constants.SCENARIOS:
            
            # Construct the prompt dynamically
            prompt = f"Write a short story about {name}. {name} {bg_text}. {scen_text.replace('[NAME]', name)}"
            
            print(f"Testing: {group} | {name} | {bg_label} | {scen_label}")
            # ... run API call here ...