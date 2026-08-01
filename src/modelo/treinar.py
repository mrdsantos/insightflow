"""Treino e materializacao da previsao. Uso: python -m src.modelo.treinar

Replica o notebooks/03_modelo.ipynb de forma reprodutivel: mesma serie mensal, mesmo
split temporal, mesmas metricas - o notebook e onde a escolha se justifica, aqui e onde
ela vira tabela. Materializa dw.previsao_mensal e dw.metricas_modelo (full refresh
idempotente: truncate + insert, rodar duas vezes da o mesmo resultado).
"""

import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

RAIZ = Path(__file__).resolve().parent.parent.parent

N_TESTE = 6      # ultimos 6 meses ficam fora do treino e viram teste
HORIZONTE = 6    # meses projetados para frente (dim_calendario tem folga ate dez/2026)

log = logging.getLogger("modelo")


def serie_mensal(conn):
    """Faturamento mensal concretizado (Entregue + Enviado), mesma serie da EDA."""
    linhas = conn.execute(
        """
        SELECT ano_mes, ROUND(SUM(valor_total), 2) AS faturamento
        FROM dw.vw_vendas
        WHERE status_pedido IN ('Entregue', 'Enviado')
        GROUP BY ano_mes ORDER BY ano_mes
        """
    ).fetchall()
    df = pd.DataFrame(linhas, columns=["ano_mes", "faturamento"])
    df["faturamento"] = df["faturamento"].astype(float)
    return df


def monta_features(df):
    """Tendencia (t) + dummies de mes, com drop_first para nao colinear com o intercepto."""
    base = df.copy()
    base["mes"] = base["ano_mes"].str[5:].astype(int)
    return pd.get_dummies(base[["t", "mes"]], columns=["mes"], prefix="m", drop_first=True)


def metricas(y_real, y_pred):
    return {
        "mae": float(mean_absolute_error(y_real, y_pred)),
        "mape": float(np.mean(np.abs((y_real - y_pred) / y_real)) * 100),
        "r2": float(r2_score(y_real, y_pred)),
    }


def executa(url=None):
    load_dotenv(RAIZ / ".env")
    url = url or os.environ["DATABASE_URL"]

    with psycopg.connect(url) as conn:
        df = serie_mensal(conn)
        df["t"] = np.arange(len(df))
        X = monta_features(df)
        y = df["faturamento"]

        X_treino, X_teste = X.iloc[:-N_TESTE], X.iloc[-N_TESTE:]
        y_treino, y_teste = y.iloc[:-N_TESTE], y.iloc[-N_TESTE:]

        # baseline: media movel dos 3 meses anteriores (shift(1) tira o proprio mes)
        pred_baseline = df["faturamento"].shift(1).rolling(3).mean().iloc[-N_TESTE:]

        reg = LinearRegression().fit(X_treino, y_treino)
        pred_reg = pd.Series(reg.predict(X_teste), index=y_teste.index)

        m_baseline = metricas(y_teste, pred_baseline)
        m_reg = metricas(y_teste, pred_reg)
        log.info("teste %s a %s: baseline mae=%.0f mape=%.1f | regressao mae=%.0f mape=%.1f",
                 df["ano_mes"].iloc[-N_TESTE], df["ano_mes"].iloc[-1],
                 m_baseline["mae"], m_baseline["mape"], m_reg["mae"], m_reg["mape"])

        # modelo final re-treinado com a serie inteira; a projecao usa a regressao
        # mesmo com o baseline ganhando no teste - justificativa no notebook 03
        reg_full = LinearRegression().fit(X, y)
        ultimo = pd.Period(df["ano_mes"].iloc[-1], freq="M")
        futuro = pd.DataFrame({
            "ano_mes": pd.period_range(ultimo + 1, periods=HORIZONTE).strftime("%Y-%m"),
        })
        futuro["t"] = np.arange(len(df), len(df) + HORIZONTE)
        X_fut = monta_features(futuro).reindex(columns=X.columns, fill_value=False)
        futuro["previsto"] = reg_full.predict(X_fut)

        # banda de +-1.96 desvios do residuo fora da amostra (teste, nao treino)
        banda = 1.96 * float((y_teste - pred_reg).std(ddof=1))

        linhas_previsao = (
            [(am, float(re), None, None, None, None, "treino")
             for am, re in zip(df["ano_mes"].iloc[:-N_TESTE], y_treino)]
            + [(am, float(re), float(aj), None, None, None, "teste")
               for am, re, aj in zip(df["ano_mes"].iloc[-N_TESTE:], y_teste, pred_reg)]
            + [(am, None, None, float(pv), float(pv - banda), float(pv + banda), "futuro")
               for am, pv in zip(futuro["ano_mes"], futuro["previsto"])]
        )
        with conn.cursor() as cur:
            cur.execute("TRUNCATE dw.previsao_mensal")
            cur.executemany(
                "INSERT INTO dw.previsao_mensal (ano_mes, realizado, ajustado, previsto, "
                "banda_inf, banda_sup, fase) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                linhas_previsao,
            )
            cur.execute("TRUNCATE dw.metricas_modelo")
            cur.executemany(
                "INSERT INTO dw.metricas_modelo (modelo, mae, mape, r2) VALUES (%s, %s, %s, %s)",
                [("media_movel", m_baseline["mae"], m_baseline["mape"], m_baseline["r2"]),
                 ("regressao", m_reg["mae"], m_reg["mape"], m_reg["r2"])],
            )
        conn.commit()
        log.info("materializado: %s linhas em previsao_mensal (%s futuro), 2 em metricas_modelo",
                 len(linhas_previsao), HORIZONTE)

    return {"previsao_mensal": len(linhas_previsao), "baseline": m_baseline, "regressao": m_reg}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    executa()
