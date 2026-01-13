import requests
import argparse
import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='SPARQL endpoint URL')

    return parser


def create_figure_abs(csv_text):
    # Parse CSV text produced by the SPARQL endpoint
    if not csv_text or not str(csv_text).strip():
        print("No CSV data provided to create_figure()")
        return

    df = pd.read_csv(io.StringIO(csv_text))

    # Map columns (be tolerant to variations in header names)
    colmap = {}
    for c in df.columns:
        lc = c.lower()
        if 'year' in lc:
            colmap['year'] = c
        elif 'source' in lc:
            colmap['source'] = c
        elif 'gender' in lc:
            # prefer exact gender_category name if present
            colmap['gender'] = c
        elif 'author' in lc:
            colmap['author'] = c

    if 'year' not in colmap or 'gender' not in colmap:
        print('CSV missing required columns (year and/or gender).')
        return

    # Ensure year is integer and restrict to 2010-2024
    df = df[df[colmap['year']].notnull()]
    df[colmap['year']] = df[colmap['year']].astype(int)
    years = np.arange(2010, 2025)

    # Initialize counts
    data_source = {
        "Source: Wikidata": np.zeros(len(years), dtype=int),
        "Source: Genderize": np.zeros(len(years), dtype=int),
    }
    data_gender = {
        "Female": np.zeros(len(years), dtype=int),
        "Male": np.zeros(len(years), dtype=int),
        "Other": np.zeros(len(years), dtype=int),
    }
    unknown = np.zeros(len(years), dtype=int)

    for i, y in enumerate(years):
        dfy = df[df[colmap['year']] == int(y)]
        if dfy.empty:
            continue

        for _, row in dfy.iterrows():
            # Gender classification
            g = row[colmap['gender']]
            try:
                g = '' if pd.isna(g) else str(g).strip().lower()
            except Exception:
                g = str(g).strip().lower()

            if not g or g == 'unknown':
                unknown[i] += 1
            elif g == 'female':
                data_gender['Female'][i] += 1
            elif g == 'male':
                data_gender['Male'][i] += 1
            else:
                data_gender['Other'][i] += 1

            # Source classification (be permissive)
            s = ''
            if 'source' in colmap:
                s = row[colmap['source']]
                try:
                    s = '' if pd.isna(s) else str(s).strip().lower()
                except Exception:
                    s = str(s).strip().lower()

            if 'wikidata' in s:
                data_source['Source: Wikidata'][i] += 1
            elif 'genderize' in s:
                data_source['Source: Genderize'][i] += 1
            else:
                # leave uncounted in source arrays; unknowns are tracked in `unknown`
                pass

    # Use absolute values instead of percentages
    data_source_abs = data_source
    data_gender_abs = data_gender
    unknown_abs = unknown

    # Plot formatting to match provided example exactly
    patterns_source = ['xxxxx', '//']

    fig, ax = plt.subplots(figsize=(5, 4))
    x = np.arange(len(years))
    width = 0.35

    # Left: data source stacked (with hatches)
    bottom_source = np.zeros(len(years))
    i = 0
    for attribute, measurement in data_source_abs.items():
        ax.bar(x - width/2, measurement, width, label=attribute, bottom=bottom_source,
               edgecolor='black', facecolor='white', hatch=patterns_source[i], linewidth=0.5)
        bottom_source += measurement
        i += 1

    ax.bar(x - width/2, unknown_abs, width, bottom=bottom_source, color='#939393')

    # Right: gender stacked (with colors)
    bottom_gender = np.zeros(len(years))
    colors_gender = ["#f5a05a", "#eb6847", "#e02525"]
    i = 0
    for attribute, measurement in data_gender_abs.items():
        ax.bar(x + width/2, measurement, width, label=attribute, bottom=bottom_gender, color=colors_gender[i])
        bottom_gender += measurement
        i += 1

    ax.bar(x + width/2, unknown_abs, width, label="Unknown", bottom=bottom_gender, color='#939393')

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Authors", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    
    # Calculate appropriate y-limit based on absolute values
    max_val = max(np.max(bottom_source + unknown_abs), np.max(bottom_gender + unknown_abs))
    y_limit = max_val * 1.05  # Add 5% padding
    ax.set_ylim(0, y_limit)
    
    # Remove percentage formatter
    # ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))
    
    # Add horizontal grid lines
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, color='gray', linewidth=0.5)
    ax.set_axisbelow(True)
    
    ax.legend(bbox_to_anchor=(0.5, 1.25), loc='upper center', fontsize=10, ncol=3, borderaxespad=0.)

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)

    plt.tight_layout()
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=600)
    plt.close(fig)


def create_figure_perc(csv_text):
    # Parse CSV text produced by the SPARQL endpoint
    if not csv_text or not str(csv_text).strip():
        print("No CSV data provided to create_figure()")
        return

    df = pd.read_csv(io.StringIO(csv_text))

    # Map columns (be tolerant to variations in header names)
    colmap = {}
    for c in df.columns:
        lc = c.lower()
        if 'year' in lc:
            colmap['year'] = c
        elif 'source' in lc:
            colmap['source'] = c
        elif 'gender' in lc:
            # prefer exact gender_category name if present
            colmap['gender'] = c
        elif 'author' in lc:
            colmap['author'] = c

    if 'year' not in colmap or 'gender' not in colmap:
        print('CSV missing required columns (year and/or gender).')
        return

    # Ensure year is integer and restrict to 2010-2024
    df = df[df[colmap['year']].notnull()]
    df[colmap['year']] = df[colmap['year']].astype(int)
    years = np.arange(2010, 2025)

    # Initialize counts
    data_source = {
        "Source: Wikidata": np.zeros(len(years), dtype=int),
        "Source: Genderize": np.zeros(len(years), dtype=int),
    }
    data_gender = {
        "Female": np.zeros(len(years), dtype=int),
        "Male": np.zeros(len(years), dtype=int),
        "Other": np.zeros(len(years), dtype=int),
    }
    unknown = np.zeros(len(years), dtype=int)

    for i, y in enumerate(years):
        dfy = df[df[colmap['year']] == int(y)]
        if dfy.empty:
            continue

        for _, row in dfy.iterrows():
            # Gender classification
            g = row[colmap['gender']]
            try:
                g = '' if pd.isna(g) else str(g).strip().lower()
            except Exception:
                g = str(g).strip().lower()

            if not g or g == 'unknown':
                unknown[i] += 1
            elif g == 'female':
                data_gender['Female'][i] += 1
            elif g == 'male':
                data_gender['Male'][i] += 1
            else:
                data_gender['Other'][i] += 1

            # Source classification (be permissive)
            s = ''
            if 'source' in colmap:
                s = row[colmap['source']]
                try:
                    s = '' if pd.isna(s) else str(s).strip().lower()
                except Exception:
                    s = str(s).strip().lower()

            if 'wikidata' in s:
                data_source['Source: Wikidata'][i] += 1
            elif 'genderize' in s:
                data_source['Source: Genderize'][i] += 1
            else:
                # leave uncounted in source arrays; unknowns are tracked in `unknown`
                pass

    # Compute percentages, avoiding division by zero
    totals_source = np.sum(list(data_source.values()), axis=0) + unknown
    totals_source_safe = np.where(totals_source == 0, 1, totals_source)
    data_source_perc = {k: (v / totals_source_safe) * 100 for k, v in data_source.items()}
    unknown_perc_source = (unknown / totals_source_safe) * 100

    totals_gender = np.sum(list(data_gender.values()), axis=0) + unknown
    totals_gender_safe = np.where(totals_gender == 0, 1, totals_gender)
    data_gender_perc = {k: (v / totals_gender_safe) * 100 for k, v in data_gender.items()}
    unknown_perc_gender = (unknown / totals_gender_safe) * 100

    # Plot formatting to match provided example exactly
    patterns_source = ['xxxxx', '//']

    fig, ax = plt.subplots(figsize=(5, 4))
    x = np.arange(len(years))
    width = 0.35

    # Left: data source stacked (with hatches)
    bottom_source = np.zeros(len(years))
    i = 0
    for attribute, measurement in data_source_perc.items():
        ax.bar(x - width/2, measurement, width, label=attribute, bottom=bottom_source,
               edgecolor='black', facecolor='white', hatch=patterns_source[i], linewidth=0.5)
        bottom_source += measurement
        i += 1

    ax.bar(x - width/2, unknown_perc_source, width, bottom=bottom_source, color='#939393')

    # Right: gender stacked (with colors)
    bottom_gender = np.zeros(len(years))
    colors_gender = ["#f5a05a", "#eb6847", "#e02525"]
    i = 0
    for attribute, measurement in data_gender_perc.items():
        ax.bar(x + width/2, measurement, width, label=attribute, bottom=bottom_gender, color=colors_gender[i])
        bottom_gender += measurement
        i += 1

    ax.bar(x + width/2, unknown_perc_gender, width, label="Unknown", bottom=bottom_gender, color='#939393')

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Authors", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))
    ax.legend(bbox_to_anchor=(0.5, 1.25), loc='upper center', fontsize=10, ncol=3, borderaxespad=0.)

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)

    plt.tight_layout()
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=600)
    plt.close(fig)


QUERY = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX genz: <https://divinwd.dev/genderize/>

SELECT DISTINCT ?author ?year ?gender_category ?source WHERE {
    {
        SELECT ?author ?year (SAMPLE(?gender) AS ?author_gender_category) (COUNT(DISTINCT ?gender) AS ?gender_count) WHERE {
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
                HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && 2010 <= ?year && ?year <= 2024)
            }

            ?article wdt:P50 ?author .

            OPTIONAL {
                ?author wdt:P21 ?genderValue .
            }

            BIND (
                COALESCE(
                    IF(!BOUND(?genderValue) || ISBLANK(?genderValue) || ?genderValue = wd:Q113124952, "unknown", 1/0),
                    IF(?genderValue = wd:Q6581072, "female", 1/0),
                    IF(?genderValue = wd:Q6581097, "male", 1/0),
                    "other"
                ) AS ?gender
            )
        }
        GROUP BY ?author ?year
    }

    BIND (IF(?gender_count = 1, ?author_gender_category, "other") AS ?wd_gender)

    OPTIONAL { ?author genz:gender ?genderize_gender . }

    # Bind source of gender values
    BIND (IF(?wd_gender != "unknown", "wikidata", IF(BOUND(?genderize_gender), "genderize.io", "unknown")) AS ?source)

    # Bind final category
    BIND (IF(?wd_gender != "unknown", ?wd_gender, COALESCE(?genderize_gender, "unknown")) AS ?gender_category)
}
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

    create_figure_perc(csv_text)


if __name__ == '__main__':
    main()