import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Valuation Dashboard", layout="wide")

st.title("📊 Valuation Metrics Dashboard")

tickers = ['SPY', 'GOOG', 'NVDA', 'TSLA', 'WMT']
fields = {
    'currentPrice': 'Last Price',
    'trailingPE': 'P/E',
    'forwardPE': 'Forward P/E',
    'priceToBook': 'Price/Book',
    'dividendYield': 'Dividend Yield',
    'enterpriseToEbitda': 'EV/EBITDA',
    'fiftyTwoWeekLow': '52W Low',
    'fiftyTwoWeekHigh': '52W High'
}

# Obtener datos
@st.cache_data
def get_valuation_data(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        data[ticker] = {}

        for key, label in fields.items():
            value = info.get(key, None)
            if value is None:
                value = '-'
            elif key == 'dividendYield':
                value = value * 100 if value < 1 else value
                value = round(value, 2)
            else:
                value = round(value, 2)
            data[ticker][label] = value

    df = pd.DataFrame(data).T
    return df

df = get_valuation_data(tickers)

# Mostrar tabla coloreada con ranking
st.subheader("📋 Valuation Table with Highlights")

# Reemplazar "-" con NaN y convertir a numérico
df_numeric = df.replace("-", pd.NA).apply(pd.to_numeric, errors='coerce')

# Aplicar colores estilo ranking (mejor = verde, peor = rojo)
def colorize(val, col, ascending=True):
    col_values = df_numeric[col].dropna()
    if len(col_values) == 0 or pd.isna(val):
        return ''
    rank = col_values.rank(ascending=ascending)[val]
    color_intensity = int(255 * (rank - 1) / (len(col_values) - 1)) if len(col_values) > 1 else 127
    red = color_intensity if not ascending else 255 - color_intensity
    green = 255 - color_intensity if not ascending else color_intensity
    return f'background-color: rgb({red},{green},100)'

# Columnas en las que el menor valor es mejor (inversamente)
inverse = ['P/E', 'Forward P/E', 'Price/Book', 'EV/EBITDA']

styled_df = df_numeric.style.format("{:.2f}", na_rep='-')

for col in df_numeric.columns:
    styled_df = styled_df.applymap(
        lambda val: colorize(val, col, ascending=(col in inverse)),
        subset=pd.IndexSlice[:, [col]]
    )

st.dataframe(styled_df, use_container_width=True)

# Descargar Excel
buffer = io.BytesIO()
df.to_excel(buffer, index=True, engine='openpyxl')
buffer.seek(0)

st.download_button(
    label="⬇️ Descargar Excel",
    data=buffer,
    file_name="valuation_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
