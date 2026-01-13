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
    # parse csv to dataframe
    df = pd.read_csv(io.StringIO(csv_text))
    if df.empty:
        print("No data returned from query.")
        return

    df.columns = [c.strip() for c in df.columns]

    df['year'] = df['year'].astype(int)

    df['languageCategory'] = df['languageCategory'].astype(str).str.strip()
    df['languageCategory'] = df['languageCategory'].replace({'non-English': 'Other', 'unknown': 'Unknown'})

    df['source'] = df['source'].astype(str).str.strip().str.lower()

    years = np.arange(df['year'].min(), df['year'].max() + 1, dtype=int)

    pivot_src = df.pivot_table(index='year', columns='source', values='article', aggfunc='count').reindex(index=years, fill_value=0)
    wikidata_counts = pivot_src.get('wikidata', pd.Series(0, index=years)).to_numpy()
    external_counts = pivot_src.get('external', pd.Series(0, index=years)).to_numpy()
    unknown_src_counts = pivot_src.get('unknown', pd.Series(0, index=years)).to_numpy()

    pivot_lang = df.pivot_table(index='year', columns='languageCategory', values='article', aggfunc='count').reindex(index=years, fill_value=0)
    english_counts = pivot_lang.get('English', pd.Series(0, index=years)).to_numpy()
    other_counts = pivot_lang.get('Other', pd.Series(0, index=years)).to_numpy()
    unknown_lang_counts = pivot_lang.get('Unknown', pd.Series(0, index=years)).to_numpy()

    # Use absolute values instead of percentages
    data_sources_abs = {
        "Source: Wikidata": wikidata_counts,
        "Source: External": external_counts,
    }
    unknown_abs_source = unknown_src_counts

    data_lang_abs = {
        "English": english_counts,
        "Other": other_counts,
    }
    unknown_abs_lang = unknown_lang_counts

    patterns_source = ['xxxxx', '//']
    fig, ax = plt.subplots(figsize=(5, 4))
    colors_sources = ['#c53a32', '#ef8636', "#939393"]
    colors_lang = ['#8d69b8', '#3b75af', '#939393']
    x = np.arange(len(years))
    width = 0.35

    bottom_source = np.zeros(len(years))
    i = 0
    for attribute, measurement in data_sources_abs.items():
        ax.bar(x - width/2, measurement, width, label=attribute, bottom=bottom_source,
               edgecolor='black', facecolor='white', hatch=patterns_source[i], linewidth=0.5)
        bottom_source += measurement
        i += 1
    ax.bar(x - width/2, unknown_abs_source, width, bottom=bottom_source, color='#939393')

    bottom_lang = np.zeros(len(years))
    colors_lang = ["#3d80c4", "#9662d6"]
    i = 0
    for attribute, measurement in data_lang_abs.items():
        ax.bar(x + width/2, measurement, width, label=attribute, bottom=bottom_lang, color=colors_lang[i])
        bottom_lang += measurement
        i += 1
    ax.bar(x + width/2, unknown_abs_lang, width, label="Unknown", bottom=bottom_lang, color='#939393')

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Articles", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    
    # Calculate appropriate y-limit based on absolute values
    max_val = max(np.max(bottom_source + unknown_abs_source), np.max(bottom_lang + unknown_abs_lang))
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


def create_figure_perc(csv_text):
    # parse csv to dataframe
    df = pd.read_csv(io.StringIO(csv_text))
    if df.empty:
        print("No data returned from query.")
        return

    df.columns = [c.strip() for c in df.columns]

    df['year'] = df['year'].astype(int)

    df['languageCategory'] = df['languageCategory'].astype(str).str.strip()
    df['languageCategory'] = df['languageCategory'].replace({'non-English': 'Other', 'unknown': 'Unknown'})

    df['source'] = df['source'].astype(str).str.strip().str.lower()

    years = np.arange(df['year'].min(), df['year'].max() + 1, dtype=int)

    pivot_src = df.pivot_table(index='year', columns='source', values='article', aggfunc='count').reindex(index=years, fill_value=0)
    wikidata_counts = pivot_src.get('wikidata', pd.Series(0, index=years)).to_numpy()
    external_counts = pivot_src.get('external', pd.Series(0, index=years)).to_numpy()
    unknown_src_counts = pivot_src.get('unknown', pd.Series(0, index=years)).to_numpy()

    pivot_lang = df.pivot_table(index='year', columns='languageCategory', values='article', aggfunc='count').reindex(index=years, fill_value=0)
    english_counts = pivot_lang.get('English', pd.Series(0, index=years)).to_numpy()
    other_counts = pivot_lang.get('Other', pd.Series(0, index=years)).to_numpy()
    unknown_lang_counts = pivot_lang.get('Unknown', pd.Series(0, index=years)).to_numpy()

    totals_sources = wikidata_counts + external_counts + unknown_src_counts

    totals_sources_safe = np.where(totals_sources == 0, 1, totals_sources)
    data_sources_perc = {
        "Source: Wikidata": (wikidata_counts / totals_sources_safe) * 100,
        "Source: External": (external_counts / totals_sources_safe) * 100,
    }
    unknown_perc_source = (unknown_src_counts / totals_sources_safe) * 100

    zero_mask_src = totals_sources == 0
    for k in data_sources_perc:
        data_sources_perc[k][zero_mask_src] = 0
    unknown_perc_source[zero_mask_src] = 0

    totals_lang = english_counts + other_counts + unknown_lang_counts
    totals_lang_safe = np.where(totals_lang == 0, 1, totals_lang)
    data_lang_perc = {
        "English": (english_counts / totals_lang_safe) * 100,
        "Other": (other_counts / totals_lang_safe) * 100,
    }
    unknown_perc_lang = (unknown_lang_counts / totals_lang_safe) * 100
    zero_mask_lang = totals_lang == 0
    for k in data_lang_perc:
        data_lang_perc[k][zero_mask_lang] = 0
    unknown_perc_lang[zero_mask_lang] = 0

    patterns_source = ['xxxxx', '//']
    fig, ax = plt.subplots(figsize=(5, 4))
    colors_sources = ['#c53a32', '#ef8636', "#939393"]
    colors_lang = ['#8d69b8', '#3b75af', '#939393']
    x = np.arange(len(years))
    width = 0.35

    bottom_source = np.zeros(len(years))
    i = 0
    for attribute, measurement in data_sources_perc.items():
        ax.bar(x - width/2, measurement, width, label=attribute, bottom=bottom_source,
               edgecolor='black', facecolor='white', hatch=patterns_source[i], linewidth=0.5)
        bottom_source += measurement
        i += 1
    ax.bar(x - width/2, unknown_perc_source, width, bottom=bottom_source, color='#939393')

    bottom_lang = np.zeros(len(years))
    colors_lang = ["#3d80c4", "#9662d6"]
    i = 0
    for attribute, measurement in data_lang_perc.items():
        ax.bar(x + width/2, measurement, width, label=attribute, bottom=bottom_lang, color=colors_lang[i])
        bottom_lang += measurement
        i += 1
    ax.bar(x + width/2, unknown_perc_lang, width, label="Unknown", bottom=bottom_lang, color='#939393')

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Articles", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))
    ax.legend(bbox_to_anchor=(0.5, 1.25), loc='upper center', fontsize=10, ncol=3, borderaxespad=0.)

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=600)


QUERY = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX oacr: <https://divinwd.dev/oacr/>
SELECT DISTINCT ?article ?year ?languageCategory ?source WHERE {
    {
        SELECT ?article
            (YEAR(MIN(?publicationDate)) AS ?year)
            (SAMPLE(?language) AS ?articleLanguage)
            (COUNT(DISTINCT ?language) AS ?languageCount)
        WHERE {
            ?article wdt:P31 wd:Q13442814 ;
                     wdt:P577 ?publicationDate ;
                     wdt:P50 [ wdt:P31 wd:Q5 ] .

            FILTER (YEAR(?publicationDate) <= YEAR(NOW()))
            MINUS { ?article wdt:P2093 ?authorNameString . }
            MINUS {
                ?article wdt:P50 ?x .
                FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
            }

            OPTIONAL { ?article wdt:P407 ?languageValue . }

            BIND (
                COALESCE(
                    IF(!BOUND(?languageValue) || ?languageValue IN (wd:Q66724591, wd:Q20923490), wd:Q22282914, 1/0), # map to undetermined: non-English, multiple languages
                    IF(?languageValue IN (wd:Q44679, wd:Q44676, wd:Q7979, wd:Q1348800, wd:Q21480034, wd:Q7976, wd:Q6144345, wd:Q7707309), wd:Q1860, 1/0), # English
                    IF(?languageValue IN (wd:Q24841726, wd:Q13414913, wd:Q18130932, wd:Q100148307, wd:Q64427357, wd:Q13646143, wd:Q1048980, wd:Q262828, wd:Q4380827), wd:Q7850, 1/0), # Chinese
                    IF(?languageValue = wd:Q750553, wd:Q5146, 1/0), # Portuguese
                    IF(?languageValue = wd:Q8141, wd:Q9288, 1/0), # Hebrew
                    IF(?languageValue = wd:Q1115875, wd:Q1321, 1/0), # Spanish
                    IF(?languageValue IN (wd:Q306626, wd:Q125258960, wd:Q1366643, wd:Q64427341), wd:Q188, 1/0), # German
                    ?languageValue
                ) AS ?language
            )
        }
        GROUP BY ?article
        HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && 2010 <= ?year && ?year <= 2024)
    }

    # Mark as unknown if multiple languages are found
    BIND (IF(?languageCount = 1, ?articleLanguage, wd:Q22282914) AS ?wdLang)

    # Fetch language from external data sources
    OPTIONAL {
        ?article oacr:lang ?langValue .
        BIND (COALESCE(
            IF(?langValue = wd:Q191769, wd:Q9043, 1/0),
            IF(?langValue IN (wd:Q24841726, wd:Q13414913, wd:Q18130932, wd:Q100148307, wd:Q64427357, wd:Q13646143, wd:Q1048980, wd:Q262828, wd:Q4380827), wd:Q7850, 1/0),
            ?langValue
        ) AS ?extLang)
    }

    # Bind final language
    BIND (IF(?wdLang != wd:Q22282914, ?wdLang, COALESCE(?extLang, wd:Q22282914)) AS ?language)

    # Bind source
    BIND (IF(?wdLang != wd:Q22282914, "wikidata", IF(BOUND(?extLang), "external", "unknown")) AS ?source)

    BIND (IF(?language = wd:Q22282914, "unknown", IF(?language = wd:Q1860, "English", "non-English")) AS ?languageCategory)
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