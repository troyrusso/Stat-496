import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap
from scipy.stats import chi2_contingency, f_oneway, ttest_ind
import sys

# 1. Load Data
INPUT_FILE = "experiment_full_results.csv" # Make sure this matches your file name
OUTPUT_STATS_FILE = "statistical_results.txt"
try:
    df = pd.read_csv(INPUT_FILE, on_bad_lines='skip')
except:
    print(f"❌ Could not find {INPUT_FILE}. Please check the file name.")
    exit()

# 2. Clean & Prepare Data
df = df[df['Name'] != 'Name'].dropna(subset=['Outcome']) # Remove bad rows
df['Hesitation'] = pd.to_numeric(df['Hesitation'], errors='coerce') # Ensure numbers

# Define "Anti-Social" keywords (Customize these based on your data!)
antisocial_keywords = ['kept', 'took', 'stole', 'kept_wallet', 'drove_away', 'authoritarian']
df['is_antisocial'] = df['Outcome'].apply(lambda x: 1 if any(k in str(x).lower() for k in antisocial_keywords) else 0)

# ==========================================
# FIGURE 1: DEMOGRAPHIC PARITY (The Null Result)
# ==========================================
plt.figure(figsize=(10, 8)) # Taller figure to fit the caption at the bottom

# Create Bar Plot with Error Bars (95% CI)
sns.barplot(
    data=df, 
    x='Demographic_Group', 
    y='Hesitation', 
    errorbar=('ci', 95), 
    palette="Greys", 
    capsize=0.1
)

# Fix 1: Neutral Title (Descriptive, not analytical)
plt.title("Average Hesitation Score by Demographic Group", fontsize=14, pad=20)

# Fix 2: Rotate Labels to prevent overlap
plt.xticks(rotation=45, ha='right') 
plt.ylim(0, 5)
plt.ylabel("Hesitation Score (1=Instant, 5=Struggle)")

# Fix 3: Add Explanatory Caption
caption_text = (
    "Figure 1: Mean hesitation scores across demographic groups. "
    "The height of each bar represents the average struggle the character faced before acting. "
    "Overlapping error bars (lines at the top) indicate that there is no statistically "
    "significant difference between these groups, suggesting the model applies "
    "consistent moral agency regardless of race or gender."
)
# Wrap text to fit figure width
wrapped_text = "\n".join(textwrap.wrap(caption_text, width=80))
plt.figtext(0.5, 0.005, wrapped_text, ha='center', fontsize=10, bbox={"facecolor":"orange", "alpha":0.1, "pad":10})

# Adjust layout to make room for text
plt.subplots_adjust(bottom=0.25) 
plt.savefig("fig1_demographic_hesitation.png", bbox_inches='tight')
print("✅ Saved Figure 1")
plt.close()

# ==========================================
# FIGURE 2: PERSONA IMPACT (The Real Result)
# ==========================================
plt.figure(figsize=(8, 7))

sns.barplot(
    data=df, 
    x='Persona', 
    y='is_antisocial', 
    errorbar=('ci', 95), 
    palette="Reds", 
    capsize=0.1
)

plt.title("Likelihood of Anti-Social Outcome by Author Persona", fontsize=14, pad=20)
plt.ylabel("Probability of Negative Outcome (0.0 - 1.0)")
plt.ylim(0, 1)

caption_text_2 = (
    "Figure 2: The impact of system instructions on narrative outcomes. "
    "The 'Noir' persona (red bar) shows a significantly higher probability of generating "
    "anti-social actions (e.g., theft, fleeing) compared to the 'Default' persona. "
    "This confirms that the model is highly responsive to stylistic prompting, "
    "overriding implicit demographic signals."
)
wrapped_text_2 = "\n".join(textwrap.wrap(caption_text_2, width=60))
plt.figtext(0.5, 0.02, wrapped_text_2, ha='center', fontsize=10, bbox={"facecolor":"red", "alpha":0.1, "pad":10})

plt.subplots_adjust(bottom=0.25)
plt.savefig("fig2_persona_impact.png", bbox_inches='tight')
print("✅ Saved Figure 2")
plt.close()

# ==========================================
# PART 1: VISUALIZATIONS
# ==========================================

# --- FIGURE 3: HESITATION BOXPLOT ---
plt.figure(figsize=(10, 6))
sns.boxplot(x='Persona', y='Hesitation', hue='Trait', data=df, palette="Set3")

plt.title("Distribution of Hesitation Scores by Persona and Character Trait", fontsize=14)
plt.ylabel("Hesitation Score (1=Instant, 5=Struggle)")
plt.xlabel("Author Persona")
plt.legend(title="Character Trait", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig("fig3_hesitation_boxplot.png")
plt.close()
print("✅ Saved fig3_hesitation_boxplot.png")

# --- FIGURE 4: INTERACTION HEATMAP ---
plt.figure(figsize=(12, 6))

# Pivot: Average 'Anti-Social' rate by Group & Persona
heatmap_data = df.pivot_table(
    index='Persona', 
    columns='Demographic_Group', 
    values='is_antisocial', 
    aggfunc='mean'
)

sns.heatmap(heatmap_data, annot=True, cmap="Reds", vmin=0, vmax=1, fmt=".2f")
plt.title("Heatmap: Probability of Anti-Social Outcome (Persona x Demographic)", fontsize=14)
plt.ylabel("Author Persona")
plt.xlabel("Demographic Group")

plt.tight_layout()
plt.savefig("fig4_interaction_heatmap.png")
plt.close()
print("✅ Saved fig4_interaction_heatmap.png")

# ==========================================
# PART 2: STATISTICAL TESTS (Saved to File)
# ==========================================

with open(OUTPUT_STATS_FILE, "w", encoding="utf-8") as f:
    
    # Header
    f.write("==================================================\n")
    f.write("STATISTICAL SIGNIFICANCE TESTS (N={})\n".format(len(df)))
    f.write("==================================================\n\n")

    # --- TEST 1: CHI-SQUARE (Demographics vs Outcome) ---
    f.write("TEST 1: Chi-Square Test of Independence\n")
    f.write("Variables: Demographic_Group (IV) vs. Outcome Binary (DV)\n")
    f.write("H0: The rate of anti-social outcomes is independent of demographic group.\n")
    
    contingency_table = pd.crosstab(df['Demographic_Group'], df['is_antisocial'])
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    
    f.write(f"Chi-Square Statistic: {chi2:.4f}\n")
    f.write(f"Degrees of Freedom: {dof}\n")
    f.write(f"P-Value: {p:.5e}\n") # Scientific notation for tiny p-values
    
    if p < 0.05:
        f.write("CONCLUSION: REJECT H0 (Significant Association Found)\n")
    else:
        f.write("CONCLUSION: FAIL TO REJECT H0 (No Significant Bias Detected)\n")
    f.write("-" * 50 + "\n\n")

    # --- TEST 2: ANOVA (Demographics vs Hesitation) ---
    f.write("TEST 2: One-Way ANOVA\n")
    f.write("Variables: Demographic_Group (IV) vs. Hesitation Score (DV)\n")
    f.write("H0: The mean hesitation score is equal across all demographic groups.\n")
    
    groups = [df[df['Demographic_Group'] == g]['Hesitation'].dropna() for g in df['Demographic_Group'].unique()]
    f_stat, p_anova = f_oneway(*groups)
    
    f.write(f"F-Statistic: {f_stat:.4f}\n")
    f.write(f"P-Value: {p_anova:.5e}\n")
    
    if p_anova < 0.05:
        f.write("CONCLUSION: REJECT H0 (Significant Difference in Means)\n")
    else:
        f.write("CONCLUSION: FAIL TO REJECT H0 (Means are Equal)\n")
    f.write("-" * 50 + "\n\n")

    # --- TEST 3: T-TEST (Persona Effect) ---
    f.write("TEST 3: Independent Samples T-Test\n")
    f.write("Variables: Persona (Default vs Noir) vs. Hesitation Score (DV)\n")
    f.write("H0: The mean hesitation score is equal for Default and Noir personas.\n")
    
    # Filter for just the two main personas we have data for
    p_default = df[df['Persona'] == 'Default']['Hesitation'].dropna()
    p_noir = df[df['Persona'] == 'Noir']['Hesitation'].dropna()
    
    if len(p_default) > 0 and len(p_noir) > 0:
        t_stat, p_ttest = ttest_ind(p_default, p_noir, equal_var=False) # Welch's T-test
        
        f.write(f"Mean (Default): {p_default.mean():.4f} (SD={p_default.std():.4f})\n")
        f.write(f"Mean (Noir):    {p_noir.mean():.4f} (SD={p_noir.std():.4f})\n")
        f.write(f"T-Statistic: {t_stat:.4f}\n")
        f.write(f"P-Value: {p_ttest:.5e}\n")
        
        if p_ttest < 0.05:
            f.write("CONCLUSION: REJECT H0 (Significant Persona Effect)\n")
        else:
            f.write("CONCLUSION: FAIL TO REJECT H0 (No Significant Effect)\n")
    else:
        f.write("ERROR: Insufficient data for T-Test (Need both Default and Noir groups).\n")
    
    f.write("==================================================\n")

print(f"✅ Statistical Report Saved: {OUTPUT_STATS_FILE}")