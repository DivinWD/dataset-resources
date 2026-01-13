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


def create_figure_abs(continents, sources, authors):

    df_continents = pd.read_csv(io.StringIO(continents))
    df_sources = pd.read_csv(io.StringIO(sources))
    df_authors = pd.read_csv(io.StringIO(authors))

    df_continents['continent_label'] = df_continents['continent_label'].fillna('Unknown').astype(str)

    df_authors.set_index('year', inplace=True)
    
    years = sorted(df_authors.index.unique())

    pivot_continents = df_continents.pivot(index='year', columns='continent_label', values='author_count').fillna(0)
    
    pivot_sources = df_sources.pivot(index='year', columns='source', values='author_count').fillna(0)

    pivot_continents = pivot_continents.reindex(years, fill_value=0)
    pivot_sources = pivot_sources.reindex(years, fill_value=0)

    # Use absolute values instead of percentages
    abs_continents = pivot_continents
    abs_sources = pivot_sources

    # Match the figure size from the second plot
    fig, ax = plt.subplots(figsize=(5, 4.5))
    
    width = 0.35
    x = np.arange(len(years))

    light_gray = "#8F8F8F"
    dark_gray = "#666666"

    source_mapping = {
        'wikidata': {'hatch': 'xxxxx', 'label': 'Source: Wikidata', 'facecolor': 'white'},
        'genderize': {'hatch': '//', 'label': 'Source: Genderize', 'facecolor': 'white'},
        'unknown': {'hatch': '', 'label': 'Source: Unknown', 'facecolor': dark_gray}
    }
    
    bottom_source = np.zeros(len(years))
    
    source_order = ['wikidata', 'genderize', 'unknown']
    
    for src in source_order:
        if src in abs_sources.columns:
            values = abs_sources[src].values
            style = source_mapping.get(src, {'hatch': '', 'label': src, 'facecolor': 'gray'})
            
            if src == 'unknown':
                ax.bar(x - width/2, values, width, bottom=bottom_source,
                       label='_nolegend_', color=style['facecolor'])
            else:
                ax.bar(x - width/2, values, width, bottom=bottom_source,
                       label=style['label'], edgecolor='black', 
                       facecolor=style['facecolor'], hatch=style['hatch'], linewidth=0.5)
            
            bottom_source += values

    colors_continents = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7']
    bottom_continents = np.zeros(len(years))

    # Sort continents by total count (descending), but keep Unknown for last
    continent_cols = list(abs_continents.columns)
    continent_totals = abs_continents.sum()
    
    # Separate Unknown from others
    other_continents = [c for c in continent_cols if c != 'Unknown']
    # Sort by total count descending
    other_continents_sorted = sorted(other_continents, key=lambda c: continent_totals[c], reverse=True)
    
    # Build final order: sorted continents + Unknown at the end (top)
    continent_order = other_continents_sorted
    if 'Unknown' in continent_cols:
        continent_order.append('Unknown')
    
    # Create a mapping from continent to color index based on alphabetical order (for legend)
    continent_cols_alpha = sorted(abs_continents.columns)
    color_map = {}
    col_idx = 0
    for continent in continent_cols_alpha:
        if continent == 'Unknown':
            color_map[continent] = light_gray
        else:
            color_map[continent] = colors_continents[col_idx % len(colors_continents)]
            col_idx += 1
    
    # Draw bars in the sorted order
    for continent in continent_order:
        values = abs_continents[continent].values
        color = color_map[continent]

        if continent == 'Unknown':
            ax.bar(x + width/2, values, width, bottom=bottom_continents,
                   label='_nolegend_', color=color)
        else:
            ax.bar(x + width/2, values, width, bottom=bottom_continents,
                   label=continent, color=color)

        bottom_continents += values

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Authors", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    
    # Calculate appropriate y-limit based on absolute values
    max_val = max(np.max(bottom_source), np.max(bottom_continents)) if len(years) > 0 else 0
    y_limit = max_val * 1.05
    ax.set_ylim(0, y_limit)
    
    # Format y-axis with comma separators
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Add horizontal gridlines at y-axis ticks
    ax.yaxis.grid(True, linestyle='-', alpha=0.3, linewidth=0.5, color='gray')
    ax.set_axisbelow(True)
    
    from matplotlib.patches import Patch, Rectangle
    from matplotlib.legend_handler import HandlerBase

    class SplitHandle:
        def __init__(self, colors):
            self.colors = colors

    class HandlerSplitRect(HandlerBase):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            left = Rectangle((xdescent, ydescent), width/2, height, facecolor=orig_handle.colors[0], transform=trans)
            right = Rectangle((xdescent + width/2, ydescent), width/2, height, facecolor=orig_handle.colors[1], transform=trans)
            for a in (left, right):
                a.set_transform(trans)
            return [left, right]

    # Build legend handles in alphabetical order
    legend_handles = []
    legend_labels = []

    # 1. Source handles (exclude unknown)
    legend_handles.append(Patch(facecolor='white', edgecolor='black', hatch='xxxxx'))
    legend_labels.append('Source: Wikidata')
    legend_handles.append(Patch(facecolor='white', edgecolor='black', hatch='//'))
    legend_labels.append('Source: Genderize')

    # 2. Combined Unknown handle
    combined_unknown = SplitHandle([light_gray, dark_gray])
    legend_handles.append(combined_unknown)
    legend_labels.append('Unknown')

    # 3. Continent handles in alphabetical order (exclude Unknown)
    for continent in continent_cols_alpha:
        if continent == 'Unknown':
            continue
        legend_handles.append(Patch(facecolor=color_map[continent]))
        legend_labels.append(continent)

    handler_map = {SplitHandle: HandlerSplitRect()}

    # Match legend position and font size from the second plot
    ax.legend(legend_handles, legend_labels, bbox_to_anchor=(0.45, 1.3), loc='upper center', 
              fontsize=10, ncol=3, borderaxespad=0., handler_map=handler_map)

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=300)
def create_figure_perc(continents, sources, authors):

    df_continents = pd.read_csv(io.StringIO(continents))
    df_sources = pd.read_csv(io.StringIO(sources))
    df_authors = pd.read_csv(io.StringIO(authors))

    df_continents['continent_label'] = df_continents['continent_label'].fillna('Unknown').astype(str)

    df_authors.set_index('year', inplace=True)
    
    years = sorted(df_authors.index.unique())

    pivot_continents = df_continents.pivot(index='year', columns='continent_label', values='author_count').fillna(0)
    
    pivot_sources = df_sources.pivot(index='year', columns='source', values='author_count').fillna(0)

    pivot_continents = pivot_continents.reindex(years, fill_value=0)
    pivot_sources = pivot_sources.reindex(years, fill_value=0)

    total_authors = df_authors['author_count'].reindex(years, fill_value=1)
    
    pct_continents = pivot_continents.div(total_authors, axis=0) * 100
    pct_sources = pivot_sources.div(total_authors, axis=0) * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    
    width = 0.35
    x = np.arange(len(years))

    light_gray = "#8F8F8F"
    dark_gray = "#666666"

    source_mapping = {
        'wikidata': {'hatch': 'xxxxx', 'label': 'Source: Wikidata', 'facecolor': 'white'},
        'genderize': {'hatch': '//', 'label': 'Source: Genderize', 'facecolor': 'white'},
        'unknown': {'hatch': '', 'label': 'Source: Unknown', 'facecolor': dark_gray}
    }
    
    bottom_source = np.zeros(len(years))
    
    source_order = ['wikidata', 'genderize', 'unknown']
    
    for src in source_order:
        if src in pct_sources.columns:
            values = pct_sources[src].values
            style = source_mapping.get(src, {'hatch': '', 'label': src, 'facecolor': 'gray'})
            
            if src == 'unknown':
                ax.bar(x - width/2, values, width, bottom=bottom_source,
                       label='_nolegend_', color=style['facecolor'])
            else:
                ax.bar(x - width/2, values, width, bottom=bottom_source,
                       label=style['label'], edgecolor='black', 
                       facecolor=style['facecolor'], hatch=style['hatch'], linewidth=0.5)
            
            bottom_source += values

    colors_continents = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#b07aa1', '#ff9da7']
    bottom_continents = np.zeros(len(years))

    # Sort continents by total count (descending), but keep Unknown for last
    continent_cols = list(pct_continents.columns)
    continent_totals = pct_continents.sum()
    
    # Separate Unknown from others
    other_continents = [c for c in continent_cols if c != 'Unknown']
    # Sort by total count descending
    other_continents_sorted = sorted(other_continents, key=lambda c: continent_totals[c], reverse=True)
    
    # Build final order: sorted continents + Unknown at the end (top)
    continent_order = other_continents_sorted
    if 'Unknown' in continent_cols:
        continent_order.append('Unknown')
    
    # Create a mapping from continent to color index based on alphabetical order (for legend)
    continent_cols_alpha = sorted(pct_continents.columns)
    color_map = {}
    col_idx = 0
    for continent in continent_cols_alpha:
        if continent == 'Unknown':
            color_map[continent] = light_gray
        else:
            color_map[continent] = colors_continents[col_idx % len(colors_continents)]
            col_idx += 1
    
    # Draw bars in the sorted order
    for continent in continent_order:
        values = pct_continents[continent].values
        color = color_map[continent]

        if continent == 'Unknown':
            ax.bar(x + width/2, values, width, bottom=bottom_continents,
                   label='_nolegend_', color=color)
        else:
            ax.bar(x + width/2, values, width, bottom=bottom_continents,
                   label=continent, color=color)

        bottom_continents += values

    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Authors (%)", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right")
    
    max_val = max(np.max(bottom_source), np.max(bottom_continents)) if len(years) > 0 else 100
    y_limit = 100 if max_val <= 100 else max_val + 5
    ax.set_ylim(0, y_limit)
    
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100))
    
    from matplotlib.patches import Patch, Rectangle
    from matplotlib.legend_handler import HandlerBase

    class SplitHandle:
        def __init__(self, colors):
            self.colors = colors

    class HandlerSplitRect(HandlerBase):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            left = Rectangle((xdescent, ydescent), width/2, height, facecolor=orig_handle.colors[0], transform=trans)
            right = Rectangle((xdescent + width/2, ydescent), width/2, height, facecolor=orig_handle.colors[1], transform=trans)
            for a in (left, right):
                a.set_transform(trans)
            return [left, right]

    # Build legend handles in alphabetical order
    legend_handles = []
    legend_labels = []

    # 1. Source handles (exclude unknown)
    legend_handles.append(Patch(facecolor='white', edgecolor='black', hatch='xxxxx'))
    legend_labels.append('Source: Wikidata')
    legend_handles.append(Patch(facecolor='white', edgecolor='black', hatch='//'))
    legend_labels.append('Source: Genderize')

    # 2. Combined Unknown handle
    combined_unknown = SplitHandle([light_gray, dark_gray])
    legend_handles.append(combined_unknown)
    legend_labels.append('Unknown')

    # 3. Continent handles in alphabetical order (exclude Unknown)
    for continent in continent_cols_alpha:
        if continent == 'Unknown':
            continue
        legend_handles.append(Patch(facecolor=color_map[continent]))
        legend_labels.append(continent)

    handler_map = {SplitHandle: HandlerSplitRect()}

    ax.legend(legend_handles, legend_labels, bbox_to_anchor=(0.5, 1.18), loc='upper center', 
              fontsize=9, ncol=4, borderaxespad=0., handler_map=handler_map)

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=300)


QUERY_CONTINENT = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX genz: <https://divinwd.dev/genderize/>
SELECT ?year ?continent_label (COUNT(DISTINCT ?author) AS ?author_count) WHERE {

    # Select articles of the dataset published between 2010 and 2024
    {
        SELECT ?article (MIN(?publication_date) AS ?article_publication_date) WHERE {
            ?article wdt:P31 wd:Q13442814 ; wdt:P577 ?publication_date ; wdt:P50 [ wdt:P31 wd:Q5 ] .

            FILTER (YEAR(?publication_date) <= YEAR(NOW()))
            MINUS { ?article wdt:P2093 ?author_name_string . }
            MINUS {
                ?article wdt:P50 ?x .
                FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
            }
        }
        GROUP BY ?article
        HAVING (COUNT(DISTINCT YEAR(?publication_date)) = 1 && 2010 <= YEAR(?article_publication_date) && YEAR(?article_publication_date) <= 2024)
    }

    BIND (YEAR(?article_publication_date) AS ?year)

    ?article wdt:P50 ?author .

    # Find nationality in Wikidata
    OPTIONAL {
        ?author p:P27 ?citizenship .
        ?citizenship rdf:type wikibase:BestRank .

        # Get time qualifiers
        OPTIONAL { ?citizenship pq:P580 ?citizenship_startTime . }
        OPTIONAL { ?citizenship pq:P582 ?citizenship_endTime . }
        FILTER (
            (!BOUND(?citizenship_startTime) || ?citizenship_startTime <= ?article_publication_date) &&
            (!BOUND(?citizenship_endTime) || ?citizenship_endTime > ?article_publication_date)
        )

        ?citizenship ps:P27 ?wd_country_value .

        # Exclude some special values
        FILTER (!ISBLANK(?wd_country_value) && ?wd_country_value NOT IN (
            wd:Q18097, # Korea
            wd:Q1152445, # Aerican Empire
            wd:Q1128483, # Cascadia
            wd:Q108746595, # Kaksonen
            wd:Q223050 # Statelessness
        ))

        # Filter countries that are not historically compatible with the article publication date
        OPTIONAL { ?wd_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?article_publication_date >= ?country_Inception)
        OPTIONAL { ?wd_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?article_publication_date < ?country_EndDate)
    }

    # Find nationality in Genderize
    OPTIONAL {
        ?author genz:nationality ?iso .
        # Genderize nationalities come with ISO 3166-1 alpha-2 codes (i.e., 2-characters identifiers)
        # Map them to Wikidata countries with codes (see property P297)
        ?genderize_country_value wdt:P297 ?iso .

        OPTIONAL { ?genderize_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?article_publication_date >= ?country_Inception)
        OPTIONAL { ?genderize_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?article_publication_date < ?country_EndDate)
    }

    # Bind final country
    BIND (COALESCE(?wd_country_value, ?genderize_country_value, "unknown") AS ?country_value)

    # Map some places to countries
    BIND (
        COALESCE(
            IF(?country_value = wd:Q55, wd:Q29999, 1/0), # Netherlands -> Kingdom of the Netherlands
            IF(?country_value = wd:Q756617, wd:Q35, 1/0), # Kingdom of Denmark -> Denmark
            IF(?country_value IN (wd:Q21, wd:Q22, wd:Q25, wd:Q42406), wd:Q145, 1/0), # England, Scotland, Wales, citizens of England -> UK
            IF(?country_value = wd:Q15124, wd:Q38, 1/0), # Sudtirolo -> Italia
            IF(?country_value = wd:Q188736, wd:Q225, 1/0), # Bosnia -> Bosnia and Herzegovina
            IF(?country_value IN (wd:Q29520, wd:Q14773), wd:Q148, 1/0), # Cina, Macao -> Repubblica Popolare Cinese
            IF(?country_value = wd:Q1335, wd:Q77, 1/0), # Città di Montevideo -> Uruguay
            IF(?country_value = wd:Q320015, wd:Q739, 1/0), # Città di Pasto -> Colombia
            IF(?country_value = wd:Q205784, wd:Q717, 1/0), # Stato di Portuguesa -> Venezuela
            IF(?country_value = wd:Q1018839, wd:Q30, 1/0), # Città di Española -> USA
            IF(?country_value = wd:Q47588, wd:Q29, 1/0), # Paesi baschi -> Spagna
            IF(?country_value = wd:Q5689, wd:Q33, 1/0), # Åland -> Finland
            ?country_value # Default
        ) AS ?author_country
    )

    # Bind source
    BIND (IF(BOUND(?wd_country_value), "wikidata", IF(BOUND(?genderize_country_value), "genderize", "unknown")) AS ?source)

    # Continent
    OPTIONAL {
        ?author_country wdt:P30 ?continent_value .
        FILTER (?continent_value IN (wd:Q15, wd:Q18, wd:Q46, wd:Q48, wd:Q49, wd:Q55643))
        BIND (
            COALESCE(
                IF(?author_country = wd:Q23681, wd:Q48, 1/0), # Northern Cyprus
                IF(?author_country = wd:Q804, wd:Q49, 1/0), # Suriname
                IF(?author_country = wd:Q730, wd:Q18, 1/0), # Panama
                ?continent_value
            ) AS ?continent_direct
        )
    }
    BIND (
        # Some islands in the Pacific Ocean are not linked to Oceania
        IF(BOUND(?continent_direct), ?continent_direct, COALESCE(
            IF(?author_country IN (wd:Q26988, wd:Q712, wd:Q691, wd:Q683, wd:Q678), wd:Q55643, 1/0)
        )) AS ?continent
    )
    BIND (COALESCE(?continent, "unknown") AS ?author_continent)
    
    OPTIONAL {
        ?author_continent rdfs:label ?continent_label .
        FILTER (LANG(?continent_label) = "en")
    }
}
GROUP BY ?year ?continent_label
"""


QUERY_SOURCE = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX genz: <https://divinwd.dev/genderize/>
SELECT ?year ?source (COUNT(DISTINCT ?author) AS ?author_count) WHERE {

    # Select articles of the dataset published between 2010 and 2024
    {
        SELECT ?article (MIN(?publication_date) AS ?article_publication_date) WHERE {
            ?article wdt:P31 wd:Q13442814 ; wdt:P577 ?publication_date ; wdt:P50 [ wdt:P31 wd:Q5 ] .

            FILTER (YEAR(?publication_date) <= YEAR(NOW()))
            MINUS { ?article wdt:P2093 ?author_name_string . }
            MINUS {
                ?article wdt:P50 ?x .
                FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
            }
        }
        GROUP BY ?article
        HAVING (COUNT(DISTINCT YEAR(?publication_date)) = 1 && 2010 <= YEAR(?article_publication_date) && YEAR(?article_publication_date) <= 2024)
    }

    BIND (YEAR(?article_publication_date) AS ?year)

    ?article wdt:P50 ?author .

    # Find nationality in Wikidata
    OPTIONAL {
        ?author p:P27 ?citizenship .
        ?citizenship rdf:type wikibase:BestRank .

        # Get time qualifiers
        OPTIONAL { ?citizenship pq:P580 ?citizenship_startTime . }
        OPTIONAL { ?citizenship pq:P582 ?citizenship_endTime . }
        FILTER (
            (!BOUND(?citizenship_startTime) || ?citizenship_startTime <= ?article_publication_date) &&
            (!BOUND(?citizenship_endTime) || ?citizenship_endTime > ?article_publication_date)
        )

        ?citizenship ps:P27 ?wd_country_value .

        # Exclude some special values
        FILTER (!ISBLANK(?wd_country_value) && ?wd_country_value NOT IN (
            wd:Q18097, # Korea
            wd:Q1152445, # Aerican Empire
            wd:Q1128483, # Cascadia
            wd:Q108746595, # Kaksonen
            wd:Q223050 # Statelessness
        ))

        # Filter countries that are not historically compatible with the article publication date
        OPTIONAL { ?wd_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?article_publication_date >= ?country_Inception)
        OPTIONAL { ?wd_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?article_publication_date < ?country_EndDate)
    }

    # Find nationality in Genderize
    OPTIONAL {
        ?author genz:nationality ?iso .
        # Genderize nationalities come with ISO 3166-1 alpha-2 codes (i.e., 2-characters identifiers)
        # Map them to Wikidata countries with codes (see property P297)
        ?genderize_country_value wdt:P297 ?iso .

        OPTIONAL { ?genderize_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?article_publication_date >= ?country_Inception)
        OPTIONAL { ?genderize_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?article_publication_date < ?country_EndDate)
    }

    # Bind final country
    BIND (COALESCE(?wd_country_value, ?genderize_country_value, "unknown") AS ?country_value)

    # Map some places to countries
    BIND (
        COALESCE(
            IF(?country_value = wd:Q55, wd:Q29999, 1/0), # Netherlands -> Kingdom of the Netherlands
            IF(?country_value = wd:Q756617, wd:Q35, 1/0), # Kingdom of Denmark -> Denmark
            IF(?country_value IN (wd:Q21, wd:Q22, wd:Q25, wd:Q42406), wd:Q145, 1/0), # England, Scotland, Wales, citizens of England -> UK
            IF(?country_value = wd:Q15124, wd:Q38, 1/0), # Sudtirolo -> Italia
            IF(?country_value = wd:Q188736, wd:Q225, 1/0), # Bosnia -> Bosnia and Herzegovina
            IF(?country_value IN (wd:Q29520, wd:Q14773), wd:Q148, 1/0), # Cina, Macao -> Repubblica Popolare Cinese
            IF(?country_value = wd:Q1335, wd:Q77, 1/0), # Città di Montevideo -> Uruguay
            IF(?country_value = wd:Q320015, wd:Q739, 1/0), # Città di Pasto -> Colombia
            IF(?country_value = wd:Q205784, wd:Q717, 1/0), # Stato di Portuguesa -> Venezuela
            IF(?country_value = wd:Q1018839, wd:Q30, 1/0), # Città di Española -> USA
            IF(?country_value = wd:Q47588, wd:Q29, 1/0), # Paesi baschi -> Spagna
            IF(?country_value = wd:Q5689, wd:Q33, 1/0), # Åland -> Finland
            ?country_value # Default
        ) AS ?author_country
    )

    # Bind source
    BIND (IF(BOUND(?wd_country_value), "wikidata", IF(BOUND(?genderize_country_value), "genderize", "unknown")) AS ?source)
}
GROUP BY ?year ?source
"""


QUERY_AUTHORS = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT ?year (COUNT(DISTINCT ?author) AS ?author_count) WHERE {
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
}
GROUP BY ?year
"""


def query_endpoint(url, query):
    headers = {"Accept": "text/csv"}
    params = {"query": query, "format": "text/csv"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
    except requests.ConnectionError:
        print("Error: Failed to connect to the server. Check the URL (is the server up?)", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: Request timed out. The server took too long to respond.", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Error: An error occurred while making the request: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    arguments = get_arg_parser().parse_args()

    print("Waiting for response...")
    continents = query_endpoint(arguments.url, QUERY_CONTINENT)
    sources = query_endpoint(arguments.url, QUERY_SOURCE)
    authors = query_endpoint(arguments.url, QUERY_AUTHORS)

    create_figure_abs(continents, sources, authors)


if __name__ == '__main__':
    main()