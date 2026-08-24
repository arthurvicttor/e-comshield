"""
02_limpeza.py — E-ComShield
Aplica as decisões de limpeza definidas na EDA (01_eda.ipynb) sobre o dataset Shopzilla
(Customer_support_data.csv) e gera as versões tratadas em data/processed/.

O dataset Bitext não entra neste script porque a EDA não encontrou valores ausentes nem
duplicatas nele — pode ser usado como está.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = DATA_DIR / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = DATA_DIR / "Customer_support_data.csv"


def carregar_dados():
    df = pd.read_csv(RAW_PATH)
    print(f"Carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
    return df


def aplicar_limpeza(df):
    df = df.copy()

    # 1. connected_handling_time: só 0,3% preenchido -> descartar
    if "connected_handling_time" in df.columns:
        df = df.drop(columns=["connected_handling_time"])
        print("Coluna 'connected_handling_time' descartada (99,7% ausente).")

    # 2. Colunas de data: lidas como texto -> converter para datetime real
    colunas_data = [
        "order_date_time",
        "Issue_reported at",
        "issue_responded",
        "Survey_response_Date",
    ]
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
    print("Colunas de data convertidas para datetime (valores inválidos viram NaT).")

    # 3. Colunas geradas via Faker (não analíticas) — mantidas no dataset, mas marcadas
    #    explicitamente aqui como não confiáveis para qualquer inferência real.
    colunas_faker = ["Agent_name", "Supervisor", "Manager", "Customer_City"]
    presentes = [c for c in colunas_faker if c in df.columns]
    print(f"Colunas geradas via Faker (não usar em inferência real): {presentes}")

    return df


def gerar_subconjunto_com_texto(df):
    """Linhas onde Customer Remarks está preenchido — usar para qualquer tarefa de NLP."""
    df_texto = df.dropna(subset=["Customer Remarks"]).copy()
    pct = len(df_texto) / len(df) * 100
    print(f"Subconjunto com texto: {len(df_texto)} linhas ({pct:.1f}% do total).")
    return df_texto


def resumo_amostra_pequena(df):
    contagem_others = (df["category"] == "Others").sum()
    print(
        f"Aviso: categoria 'Others' tem {contagem_others} registros "
        f"({contagem_others/len(df)*100:.1f}% do dataset) — amostra pequena, "
        "qualquer estatística sobre ela deve ser tratada com ressalva."
    )


def main():
    df = carregar_dados()
    df_limpo = aplicar_limpeza(df)
    df_texto = gerar_subconjunto_com_texto(df_limpo)
    resumo_amostra_pequena(df_limpo)

    caminho_limpo = OUT_DIR / "shopzilla_clean.csv"
    caminho_texto = OUT_DIR / "shopzilla_com_texto.csv"
    df_limpo.to_csv(caminho_limpo, index=False)
    df_texto.to_csv(caminho_texto, index=False)

    print(f"\nSalvo: {caminho_limpo} ({df_limpo.shape[0]} linhas, {df_limpo.shape[1]} colunas)")
    print(f"Salvo: {caminho_texto} ({df_texto.shape[0]} linhas, {df_texto.shape[1]} colunas)")


if __name__ == "__main__":
    main()
