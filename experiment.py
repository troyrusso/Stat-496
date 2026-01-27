import os
import pandas as pd
from openai import OpenAI
import constants  # This imports the file you created in the previous step

# --- CONFIGURATION ---
API_KEY = "sk-..." # PASTE YOUR OPENAI API KEY HERE
TEST_MODE = True   # Set to True to run only 1 trial per name (for debugging)
                   # Set to False to run the full 5 trials per name (for real data)

# Initialize OpenAI
client = OpenAI(api_key=API_KEY)

def run_experiment():
    results = []
    
    # Calculate total runs for progress bar
    total_trials = 1 if TEST_MODE else 5
    print(f"Starting Experiment... (Test Mode: {TEST_MODE})")

    # --- THE BIG LOOP ---
    # 1. Loop through every Name
    for group, name in constants.ALL_NAMES:
        
        # 2. Loop through every Background (Neutral vs Struggling)
        for bg_label, bg_text in constants.BACKGROUNDS:
            
            # 3. Loop through every Scenario (Wallet vs Team)
            for scen_label, scen_text in constants.SCENARIOS:
                
                # 4. Loop for N Trials (Replication)
                for i in range(total_trials):
                    
                    # --- CONSTRUCT THE PROMPT ---
                    # We combine the name, background, and scenario into one string.
                    # Example: "Write a short story about Connor. Connor is unemployed. While walking..."
                    
                    # Replace [NAME] in the scenario text if it exists
                    scenario_filled = scen_text.replace("[NAME]", name)
                    
                    # Full Prompt Assembly
                    user_prompt = f"Write a short story about {name}. {name} {bg_text}. {scenario_filled}"
                    
                    print(f"Generating: {group} | {name} | {bg_label} | {scen_label} | Trial {i+1}")

                    try:
                        # --- API CALL ---
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant. Write a short, realistic story based on the prompt provided. Do not add moralizing commentary at the end."},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.7,
                            max_tokens=350 
                        )
                        
                        story_text = response.choices[0].message.content
                        
                        # --- SAVE DATA ---
                        results.append({
                            "Demographic_Group": group,
                            "Name": name,
                            "SES_Background": bg_label,
                            "Scenario_Type": scen_label,
                            "Trial_Number": i + 1,
                            "Prompt_Used": user_prompt,
                            "Story_Output": story_text
                        })
                        
                    except Exception as e:
                        print(f"❌ ERROR on {name}: {e}")

    # --- EXPORT TO CSV ---
    # Convert list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(results)
    
    # Save file
    filename = "experiment_results_TEST.csv" if TEST_MODE else "experiment_results_FINAL.csv"
    df.to_csv(filename, index=False)
    
    print(f"\n✅ Success! collected {len(df)} stories.")
    print(f"Results saved to: {filename}")

if __name__ == "__main__":
    run_experiment()
    