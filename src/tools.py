import os
import io
import contextlib
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Nem interaktív backend, hogy ne nyisson ablakokat háttérben
import matplotlib.pyplot as plt
from langchain.tools import tool

# Az adatfájl alapértelmezett útvonala
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ugyfelszolgalat_logok.csv")

@tool
def run_python_analysis(python_code: str) -> str:
    """
    Futtat egy tetszőleges Python kódot Pandas és Matplotlib használatával az ügyfélszolgálati adatkészleten.
    A CSV fájl elérhető a 'data/ugyfelszolgalat_logok.csv' útvonalon, vagy a globális 'df' DataFrame-ben (ha már be lett töltve).
    Használd ezt az eszközt adatok szűrésére, aggregálására, statisztikák készítésére és grafikonok generálására.
    Ha grafikont rajzolsz, mentsd el 'chart.png' néven.
    Visszaadja a kód által kiírt (printelt) eredményeket vagy a hibaüzenetet.
    """
    # Ellenőrizzük, létezik-e az adatfájl
    if not os.path.exists(DATA_PATH):
        return f"HIBA: Az adatfájl nem található itt: {DATA_PATH}"

    # Előkészítjük a globális környezetet, hogy a kódban kényelmesen lehessen használni a csomagokat és a df-et
    global_env = {
        "pd": pd,
        "plt": plt,
        "DATA_PATH": DATA_PATH
    }

    # Betöltjük a DataFrame-et előre, hogy a generált kód azonnal használhassa a 'df'-et
    try:
        df = pd.read_csv(DATA_PATH)
        global_env["df"] = df
    except Exception as e:
        return f"HIBA a DataFrame betöltése közben: {str(e)}"

    # Elfecsegjük a standard outputot (stdout), hogy elkapjuk a print() kimeneteket
    output_buffer = io.StringIO()
    
    try:
        # Biztonságosabb futtatási környezet biztosítása context managerrel
        with contextlib.redirect_stdout(output_buffer):
            # A generált kód végrehajtása
            exec(python_code, global_env)
        
        # Ha a kód lefutott, visszaküldjük a printelt eredményt
        result = output_buffer.getvalue()
        if not result.strip():
            result = "A kód sikeresen lefutott, de nem történt kiíratás (print). Ha grafikont készítettél, az elmentődött."
        return result

    except Exception as e:
        # Ha hiba történik (pl. KeyError, SyntaxError), visszaküldjük a hibát, hogy az agent kijavíthassa
        return f"FUTTATÁSI HIBA: {type(e).__name__}: {str(e)}"