import matplotlib

matplotlib.use("Agg")


def test_pandas_polars_duckdb_agree():
    import duckdb
    import pandas as pd
    import polars as pl
    rows = {"ville": ["Tunis", "Paris", "Tunis", "Lyon"], "ventes": [10, 20, 5, 7]}
    pdf = pd.DataFrame(rows)
    a = pdf.groupby("ville")["ventes"].sum().to_dict()
    b = dict(pl.DataFrame(rows).group_by("ville").agg(pl.col("ventes").sum()).iter_rows())
    c = dict(duckdb.sql("select ville, sum(ventes) from pdf group by ville").fetchall())
    assert a == b == c == {"Tunis": 15, "Paris": 20, "Lyon": 7}


def test_parquet_and_excel_roundtrip(tmp_path):
    import pandas as pd
    df = pd.DataFrame({"x": [1, 2, 3], "nom": ["é", "ب", "z"]})
    df.to_parquet(tmp_path / "d.parquet")
    df.to_excel(tmp_path / "d.xlsx", index=False)
    assert pd.read_parquet(tmp_path / "d.parquet").equals(df)
    assert pd.read_excel(tmp_path / "d.xlsx").equals(df)


def test_charts(tmp_path):
    import matplotlib.pyplot as plt
    import plotly.express as px
    import seaborn as sns
    ax = sns.barplot(x=["a", "b"], y=[1, 2])
    ax.figure.savefig(tmp_path / "s.png")
    plt.close("all")
    px.line(x=[1, 2, 3], y=[1, 4, 9]).write_html(tmp_path / "p.html")
    assert (tmp_path / "s.png").stat().st_size > 1000 and (tmp_path / "p.html").stat().st_size > 1000
