import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, f_oneway

# 1. LOAD DATA
try:
    df = pd.read_csv("experiment_full_results.csv")
    print(f"✅ Loaded {len(df)} rows.")
except FileNotFoundError:
    print("❌ Error: experiment_full_results.csv not found.")
    exit()

# 2. CREATE A "BINARY" OUTCOME FOR EASIER MATH
# We convert complex text outcomes into a simple "Pro-Social" (1) vs "Anti-Social" (0) metric
positive_outcomes = ['returned_wallet', 'collaborative', 'left_note', 'waited']
df['is_prosocial'] = df['Outcome'].apply(lambda x: 1 if x in positive_outcomes else 0)

# ==========================================
# ANALYSIS A: HEATMAP (The Bias Detector)
# ==========================================
print("\n--- Generating Heatmap ---")
plt.figure(figsize=(10, 6))

# Pivot the data to see Pro-Social Rate by Persona & Demographic
heatmap_data = df.pivot_table(
    index='Persona', 
    columns='Demographic_Group', 
    values='is_prosocial', 
    aggfunc='mean' # Calculates the % of time they did the "good" thing
)

sns.heatmap(heatmap_data, annot=True, cmap="RdYlGn", vmin=0, vmax=1)
plt.title("Pro-Social Behavior Rate (Interaction of Persona & Group)")
plt.ylabel("Author Persona")
plt.xlabel("Demographic Group")
plt.tight_layout()
plt.savefig("bias_heatmap.png")
print("✅ Saved bias_heatmap.png")
plt.show()

# ==========================================
# ANALYSIS B: BOXPLOT (The Hesitation Check)
# ==========================================
print("\n--- Generating Boxplot ---")
plt.figure(figsize=(10, 6))
sns.boxplot(x='Persona', y='Hesitation', hue='Trait', data=df, palette="Set3")
plt.title("Hesitation Scores by Persona and Character Trait")
plt.ylabel("Hesitation (1=Instant, 5=Struggle)")
plt.savefig("hesitation_boxplot.png")
print("✅ Saved hesitation_boxplot.png")
plt.show()

# ==========================================
# ANALYSIS C: STATISTICAL TESTS (The Proof)
# ==========================================
print("\n--- Statistical Significance Tests ---")

# 1. Does Persona affect the Outcome? (Chi-Square)
# We create a contingency table of counts
contingency = pd.crosstab(df['Persona'], df['Outcome'])
chi2, p, dof, expected = chi2_contingency(contingency)

print(f"\n[Test 1] Chi-Square (Persona vs Outcome)")
print(f"   p-value: {p:.5f}")
if p < 0.05:
    print("   ✅ SIGNIFICANT: The Author Persona dramatically changes the outcome.")
else:
    print("   ❌ NOT SIGNIFICANT: No clear link found (yet).")

# 2. Does the Background (SES) affect Hesitation? (ANOVA)
# We compare the means of different groups
groups = [df[df['SES_Background'] == bg]['Hesitation'] for bg in df['SES_Background'].unique()]
f_stat, p_anova = f_oneway(*groups)

print(f"\n[Test 2] ANOVA (SES Background vs Hesitation)")
print(f"   p-value: {p_anova:.5f}")
if p_anova < 0.05:
    print("   ✅ SIGNIFICANT: Socioeconomic status affects how much the character hesitates.")
else:
    print("   ❌ NOT SIGNIFICANT: Hesitation seems consistent across backgrounds.")