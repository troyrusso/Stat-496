import pandas as pd
import re
import os

# --- CONFIGURATION ---
INPUT_FILE = "first_pass_results_GRITTY.csv"  # The file with the stories
OUTPUT_FILE = "experiment_stats.csv"    # The file we will create

# --- LEXICAL DICTIONARIES ---
HESITATION_TERMS = [
    r"hesit", r"conscience", r"guilt", r"debat", 
    r"thought twice", r"consider", r"paus", r"weigh", r"moral", r"dilemma"
]

IMPULSE_TERMS = [
    r"instinct", r"reflex", r"without thinking", 
    r"no hesitation", r"automatic", r"urge", r"immediate", 
    r"impulse", r"fast", r"snatch"
]

def count_matches(text, patterns):
    if not isinstance(text, str): return 0
    text = text.lower()
    count = 0
    for pattern in patterns:
        if re.search(pattern, text):
            count += 1
    return count

def run_analysis():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Could not find {INPUT_FILE}")
        return

    print(f"Loading raw data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # 1. Identify the text column
    text_col = 'Output' if 'Output' in df.columns else 'Story_Output'
    
    # 2. Calculate Scores
    print("Scoring narratives...")
    df['Hesitation_Score'] = df[text_col].apply(lambda x: count_matches(x, HESITATION_TERMS))
    df['Impulse_Score'] = df[text_col].apply(lambda x: count_matches(x, IMPULSE_TERMS))
    df['Agency_Gap'] = df['Hesitation_Score'] - df['Impulse_Score']

    # 3. SELECT ONLY THE METRICS (Drop the Text)
    # We keep the "Metadata" (Name, Group, Background) and the "Scores"
    keep_cols = [
        'Demographic_Group', 'Name', 'SES_Background', 'Scenario_Type', # Identifiers
        'Hesitation_Score', 'Impulse_Score', 'Agency_Gap'               # Metrics
    ]
    
    # Handle case where columns might be named differently in First Pass vs Final
    if 'Demographic_Group' not in df.columns:
        keep_cols = ['Name', 'Background', 'Hesitation_Score', 'Impulse_Score', 'Agency_Gap']

    final_df = df[keep_cols]

    # 4. Save and Print
    print("\n--- FINAL STATS (Preview) ---")
    print(final_df.head())
    
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Clean stats saved to: {OUTPUT_FILE}")
    print(f"   (File size reduced, text removed)")

if __name__ == "__main__":
    run_analysis()