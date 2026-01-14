import pandas as pd

# Testa com latin1
df_test = pd.read_csv(r"C:\pibic_dash\serie_SIH_final.RData.csv", encoding="latin1", sep=",")
print(df_test.head())
print(df_test.columns)
