import requests
import argparse
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='SPARQL endpoint URL')

    return parser


def create_figure(csv_text):
    # Parse CSV into a dataframe
    try:
        df = pd.read_csv(io.StringIO(csv_text))
    except Exception as e:
        print(f"Error parsing CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # The CSV results are expected to have two columns: year and article_count (or similar).
    # We'll use the first two columns regardless of their header names.
    if df.shape[1] < 2:
        print("Unexpected CSV format: expected at least two columns (year, article_count)", file=sys.stderr)
        sys.exit(1)

    # Extract x (year) and y (article_count) using the first two columns
    x_col = df.columns[0]
    y_col = df.columns[1]
    df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
    df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
    df = df.dropna(subset=[x_col, y_col])

    if df.empty:
        print("No numeric data available to plot.", file=sys.stderr)
        sys.exit(1)

    # Prepare data for plotting
    years = df[x_col].values
    articles = df[y_col].values

    years = np.array(years)
    articles = np.array(articles)

    # Exponential regression parameters
    a, b = np.polyfit(years, np.log(articles), 1)
    linear_fit = a * years + b
    r2 = r2_score(linear_fit, np.log(articles))
    exp_fit = np.exp(linear_fit)

    _, ax = plt.subplots(figsize=(5, 3))
    ax.plot(years, articles, '.', markersize=5, label='Observed articles', color='C0')
    ax.plot(years, exp_fit, '--', color='red', linewidth=1, label=f'Exponential fit ($R^2 = {r2:.4f}$)')

    ax.set_yscale('log')
    ax.set_ylim(bottom=1)
    ax.set_xlabel('Year', fontsize=9)
    ax.set_ylabel('Articles (log scale)', fontsize=9)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3, linestyle='-')

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)

    # Inset: ZOOM 2010-2024
    axins = ax.inset_axes([0.2, 0.4, 0.2, 0.3])

    mask = (years >= 2010) & (years <= 2024)
    years_inset = years[mask]
    articles_inset = articles[mask]

    axins.plot(years_inset, articles_inset, '.-', markersize=6, color='C0', linewidth=1)
    axins.set_yscale('log')
    axins.set_yticks([10000, 100000])
    axins.grid(True, alpha=0.3, linestyle='--', which='both', axis='both')
    axins.tick_params(labelsize=7)

    # Lines connecting inset to zoomed region
    ax.indicate_inset_zoom(axins, edgecolor="black", linewidth=1.5, alpha=0.1)

    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=600)


QUERY = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?year (COUNT(DISTINCT ?article) AS ?article_count) WHERE {
    {
        SELECT ?article (YEAR(MIN(?publicationDate)) AS ?year) WHERE {
            ?article wdt:P31 wd:Q13442814 ;
                    wdt:P577 ?publicationDate ;
                    wdt:P50 [ wdt:P31 wd:Q5 ] .

            FILTER (YEAR(?publicationDate) <= YEAR(NOW()))
            MINUS { ?article wdt:P2093 ?authorNameString . }
            MINUS {
                ?article wdt:P50 ?x .
                FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
            }
        }
        GROUP BY ?article
        HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && ?year <= YEAR(NOW()))
    }
    ?article wdt:P50 ?author .
}
GROUP BY ?year
ORDER BY ?year
"""


def main():
    arguments = get_arg_parser().parse_args()

    url = arguments.url
    headers = {"Accept": "text/csv"}
    params = {"query": QUERY, "format": "text/csv"}

    print("Waiting for response...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        csv_text = response.text
    except requests.ConnectionError:
        print("Error: Failed to connect to the server. Check the URL (is the server up?)", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: Request timed out. The server took too long to respond.", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Error: An error occurred while making the request: {str(e)}", file=sys.stderr)
        sys.exit(1)

    create_figure(csv_text)


if __name__ == '__main__':
    main()