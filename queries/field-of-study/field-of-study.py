import requests
import argparse
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='SPARQL endpoint URL')

    return parser


def create_figure(csv_text):
    # Parse CSV text into a DataFrame
    df = pd.read_csv(io.StringIO(csv_text))

    if df.empty:
        print("No data returned by query; nothing to plot.")
        return

    # Normalize column names (remove leading ? if present)
    df.columns = [c.strip().lstrip('?') for c in df.columns]

    field_col = 'field_of_study'
    count_col = 'article_count'
    if field_col not in df.columns or count_col not in df.columns:
        print(f"Expected columns `field_of_study` and `article_count` not found. Columns: {df.columns.tolist()}", file=sys.stderr)
        return

    if count_col is None:
        print("Could not determine the article count column. Columns:", df.columns.tolist(), file=sys.stderr)
        return

    df[count_col] = pd.to_numeric(df[count_col], errors='coerce').fillna(0).astype(int)

    df = df.sort_values(by=count_col, ascending=False).reset_index(drop=True)

    labels = df[field_col].astype(str).tolist()
    counts = df[count_col].tolist()

    n = len(df)
    fig_height = max(4, n * 0.4)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    y = np.arange(n)
    ax.barh(y, counts, color='tab:blue')
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Article count')
    ax.set_title('Articles per field of study')

    max_count = max(counts) if counts else 0
    minor_spacing = 10000
    major_spacing = 50000
    if max_count <= 0:
        x_max = minor_spacing
    else:
        x_max = int(math.ceil(max_count / minor_spacing) * minor_spacing)
    ax.set_xlim(0, x_max)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(major_spacing))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_spacing))
    ax.grid(which='major', axis='x', linestyle='-', color='gray', alpha=0.8)
    ax.grid(which='minor', axis='x', linestyle='--', color='gray', alpha=0.4)
    ax.tick_params(axis='x', labelrotation=0)

    plt.tight_layout()

    fig.savefig('figure.png', dpi=600)


QUERY = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX s2fos: <https://divinwd.dev/semanticscholar/fos/>
SELECT ?field_of_study (COUNT(DISTINCT ?article) AS ?article_count) WHERE {
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

    # Fetch field of study from external data sources
    OPTIONAL {
        { ?article s2fos:value ?fos_value_1 . } # Ready-to-use label
        UNION
        { ?article s2fos:prediction ?fos_value_2 . } # Predicted field
    }

    # Prioritize labels over predicted values. Mark as unknown if neither is available
    BIND (COALESCE(?fos_value_1, ?fos_value_2, "unknown") AS ?field_of_study)
}
GROUP BY ?field_of_study
ORDER BY DESC(?article_count)
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