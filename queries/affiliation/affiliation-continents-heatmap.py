import requests
import argparse
import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='SPARQL endpoint URL')
    return parser

def create_figure(matrix_csv, tot_csv):
    try:
        if not matrix_csv or not matrix_csv.strip():
            raise ValueError("La query Matrix ha restituito un risultato vuoto.")
        if not tot_csv or not tot_csv.strip():
            raise ValueError("La query Totali ha restituito un risultato vuoto.")
            
        df_matrix_raw = pd.read_csv(io.StringIO(matrix_csv))
        df_tot_raw = pd.read_csv(io.StringIO(tot_csv))
    except (pd.errors.EmptyDataError, ValueError) as e:
        print(f"Errore nel processare i CSV: {e}", file=sys.stderr)
        return

    df_abs = df_matrix_raw.pivot(index='ac_label', columns='rc_label', values='count').fillna(0)

    totals = df_tot_raw.set_index('ac_label')['count']

    continents_order = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America']
    
    df_abs = df_abs.reindex(index=continents_order, columns=continents_order, fill_value=0)
    totals = totals.reindex(continents_order, fill_value=0)
    df_perc = df_abs.div(totals, axis=0).fillna(0)

    display_labels = ['Africa', 'Asia', 'Europe', 'North\nAmerica', 'Oceania', 'South\nAmerica']
    df_abs.index = display_labels
    df_abs.columns = display_labels
    df_perc.index = display_labels
    df_perc.columns = display_labels

    plt.figure(figsize=(8, 6.5), dpi=150)

    ax = sns.heatmap(
        df_perc,
        annot=df_abs,
        fmt=',.0f', 
        cmap='YlGnBu',
        linewidths=.1,
        linecolor='black',
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Affiliated authors-to-total citizens ratio'},
        annot_kws={"fontsize": 9}
    )

    num_rows = len(display_labels)
    for i in range(num_rows + 1):
        ax.hlines(i, *ax.get_xlim(), color="#393939", linewidth=1)
        ax.vlines(i, *ax.get_ylim(), color="#393939", linewidth=0)

    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')

    plt.setp(
        ax.get_xticklabels(),
        rotation=45,
        ha='left',
        rotation_mode='anchor',
        fontsize=11,
    )
    plt.setp(ax.get_yticklabels(), fontsize=11, rotation=0)

    plt.ylabel('Citizenship', fontsize=12, labelpad=10)
    plt.xlabel('Affiliation continent', fontsize=12, labelpad=15)
    plt.title('Affiliation continent', fontsize=14, y=1.15)

    plt.tight_layout()
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=300)


def query_endpoint(url, query):
    headers = {
        "Accept": "text/csv",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Python-Viz-Script/1.0"
    }

    data = {
        "query": query,
        "format": "text/csv"
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=300)
        response.raise_for_status()
        return response.text

    except requests.ConnectionError:
        print(f"Unable to connect to the server {url}.", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print("Error: Timeout.", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"HTTP error: {str(e)}", file=sys.stderr)
        # Se c'è una risposta del server (es. errore SPARQL), stampiamola
        if e.response is not None:
             print(f"Server details: {e.response.text}", file=sys.stderr)
        sys.exit(1)


QUERY_MATRIX = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX ror: <https://divinwd.dev/ror/>
PREFIX genz: <https://divinwd.dev/genderize/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ac_label ?rc_label (COUNT(DISTINCT ?author) AS ?count) WHERE {
    {
        SELECT DISTINCT ?author ?authorContinent ?rorContinent WHERE {
            {
                SELECT ?article (MIN(?publicationDate) AS ?articlePublicationDate) WHERE {
                    ?article wdt:P31 wd:Q13442814 ; wdt:P577 ?publicationDate ; wdt:P50 [ wdt:P31 wd:Q5 ] .

                    FILTER (YEAR(?publicationDate) <= YEAR(NOW()))
                    MINUS { ?article wdt:P2093 ?authorNameString . }
                    MINUS {
                        ?article wdt:P50 ?x .
                        FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
                    }
                }
                GROUP BY ?article
                HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && 2010 <= YEAR(?articlePublicationDate) && YEAR(?articlePublicationDate) <= 2024)
            }
            BIND (YEAR(?articlePublicationDate) AS ?year)

            ?article wdt:P50 ?author .

            # Find nationality in Wikidata
            OPTIONAL {
                ?author p:P27 ?citizenship .
                ?citizenship rdf:type wikibase:BestRank .
                OPTIONAL { ?citizenship pq:P580 ?citizenship_startTime . }
                OPTIONAL { ?citizenship pq:P582 ?citizenship_endTime . }
                FILTER (
                    (!BOUND(?citizenship_startTime) || ?citizenship_startTime <= ?articlePublicationDate) &&
                    (!BOUND(?citizenship_endTime) || ?citizenship_endTime > ?articlePublicationDate)
                )
                ?citizenship ps:P27 ?wd_country_value .
                FILTER (!ISBLANK(?wd_country_value) && ?wd_country_value NOT IN (
                    wd:Q18097, wd:Q1152445, wd:Q1128483, wd:Q108746595, wd:Q223050
                ))
                OPTIONAL { ?wd_country_value wdt:571 ?country_Inception . }
                FILTER (!BOUND(?country_Inception) || ?articlePublicationDate >= ?country_Inception)
                OPTIONAL { ?wd_country_value wdt:P576 ?country_EndDate . }
                FILTER (!BOUND(?country_EndDate) || ?articlePublicationDate < ?country_EndDate)
            }

            # Find nationality in Genderize
            OPTIONAL {
                ?author genz:nationality ?iso .
                ?genderize_country_value wdt:P297 ?iso .
                OPTIONAL { ?genderize_country_value wdt:571 ?country_Inception . }
                FILTER (!BOUND(?country_Inception) || ?articlePublicationDate >= ?country_Inception)
                OPTIONAL { ?genderize_country_value wdt:P576 ?country_EndDate . }
                FILTER (!BOUND(?country_EndDate) || ?articlePublicationDate < ?country_EndDate)
            }

            BIND (COALESCE(?wd_country_value, ?genderize_country_value, "unknown") AS ?country_value)

            BIND (
                COALESCE(
                    IF(?country_value = wd:Q55, wd:Q29999, 1/0), 
                    IF(?country_value = wd:Q756617, wd:Q35, 1/0), 
                    IF(?country_value IN (wd:Q21, wd:Q22, wd:Q25, wd:Q42406), wd:Q145, 1/0), 
                    IF(?country_value = wd:Q15124, wd:Q38, 1/0), 
                    IF(?country_value = wd:Q188736, wd:Q225, 1/0), 
                    IF(?country_value IN (wd:Q29520, wd:Q14773), wd:Q148, 1/0), 
                    IF(?country_value = wd:Q1335, wd:Q77, 1/0), 
                    IF(?country_value = wd:Q320015, wd:Q739, 1/0), 
                    IF(?country_value = wd:Q205784, wd:Q717, 1/0), 
                    IF(?country_value = wd:Q1018839, wd:Q30, 1/0), 
                    IF(?country_value = wd:Q47588, wd:Q29, 1/0), 
                    IF(?country_value = wd:Q5689, wd:Q33, 1/0), 
                    ?country_value 
                ) AS ?authorCountry
            )

            OPTIONAL {
                ?authorCountry wdt:P30 ?continent_value .
                FILTER (?continent_value IN (wd:Q15, wd:Q18, wd:Q46, wd:Q48, wd:Q49, wd:Q55643))
                BIND (
                    COALESCE(
                        IF(?authorCountry = wd:Q23681, wd:Q48, 1/0), 
                        IF(?authorCountry = wd:Q804, wd:Q49, 1/0), 
                        IF(?authorCountry = wd:Q730, wd:Q18, 1/0), 
                        ?continent_value
                    ) AS ?continentDirect
                )
            }
            BIND (
                IF(BOUND(?continentDirect), ?continentDirect, COALESCE(
                    IF(?authorCountry IN (wd:Q26988, wd:Q712, wd:Q691, wd:Q683, wd:Q678), wd:Q55643, 1/0)
                )) AS ?continent
            )
            BIND (COALESCE(?continent, "unknown") AS ?authorContinent)

            ### Affiliation ###
            ?author p:P108 ?employment .
            ?employment rdf:type wikibase:BestRank .
            OPTIONAL { ?employment pq:P580 ?employment_startTime . }
            OPTIONAL { ?employment pq:P582 ?employment_endTime . }
            FILTER (
                (BOUND(?employment_startTime) || BOUND(?employment_endTime)) &&
                (!ISBLANK(?employment_startTime) || !ISBLANK(?employment_endTime)) &&
                (!BOUND(?employment_startTime) || ?employment_startTime <= ?articlePublicationDate) &&
                (!BOUND(?employment_endTime) || ?employment_endTime > ?articlePublicationDate)
            )

            ?employment ps:P108 ?org .
            {
                SELECT (SAMPLE(?organization) AS ?org) ?rorid WHERE {
                    SELECT ?organization (SAMPLE(?roridValue) AS ?rorid) WHERE { ?organization wdt:P6782 ?roridValue . }
                    GROUP BY ?organization HAVING (COUNT(DISTINCT ?roridValue) = 1)
                }
                GROUP BY ?rorid
                HAVING (COUNT(DISTINCT ?organization) = 1)
            }
            ?org wdt:P6782 ?rorid .
            ?rorOrganization ror:id ?rorid .
            ?rorOrganization ror:location ?rorLocation .

            OPTIONAL {
                ?rorLocation wdt:P30 ?continent_value_ror .
                FILTER (?continent_value_ror IN (wd:Q15, wd:Q18, wd:Q46, wd:Q48, wd:Q49, wd:Q55643))
                BIND (
                    COALESCE(
                        IF(?rorLocation = wd:Q23681, wd:Q48, 1/0), 
                        IF(?rorLocation = wd:Q804, wd:Q49, 1/0), 
                        IF(?rorLocation = wd:Q730, wd:Q18, 1/0), 
                        ?continent_value_ror
                    ) AS ?continentDirect_ror
                )
            }
            BIND (
                IF(BOUND(?continentDirect_ror), ?continentDirect_ror, COALESCE(
                    IF(?rorLocation IN (wd:Q26988, wd:Q712, wd:Q691, wd:Q683, wd:Q678), wd:Q55643, 1/0)
                )) AS ?continent_ror
            )
            BIND (COALESCE(?continent_ror, "unknown") AS ?rorContinent)
        }
    }
    FILTER (?authorContinent != "unknown" && ?rorContinent != "unknown")

    ?authorContinent rdfs:label ?ac_label .
    FILTER (LANG(?ac_label) = "en")
    ?rorContinent rdfs:label ?rc_label .
    FILTER (LANG(?rc_label) = "en")
}
GROUP BY ?ac_label ?rc_label
ORDER BY ?ac_label ?rc_label
"""

QUERY_TOT_AFF_CITIZENS = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX ror: <https://divinwd.dev/ror/>
PREFIX genz: <https://divinwd.dev/genderize/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ac_label (COUNT(DISTINCT ?author) AS ?count) WHERE {
{
SELECT DISTINCT ?author ?authorContinent ?rorContinent WHERE {
    {
        SELECT ?article (MIN(?publicationDate) AS ?articlePublicationDate) WHERE {
            ?article wdt:P31 wd:Q13442814 ; wdt:P577 ?publicationDate ; wdt:P50 [ wdt:P31 wd:Q5 ] .

            FILTER (YEAR(?publicationDate) <= YEAR(NOW()))
            MINUS { ?article wdt:P2093 ?authorNameString . }
            MINUS {
                ?article wdt:P50 ?x .
                FILTER NOT EXISTS { ?x wdt:P31 wd:Q5 . }
            }
        }
        GROUP BY ?article
        HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && 2010 <= YEAR(?articlePublicationDate) && YEAR(?articlePublicationDate) <= 2024)
    }
    BIND (YEAR(?articlePublicationDate) AS ?year)

    ?article wdt:P50 ?author .

    # Find nationality in Wikidata
    OPTIONAL {
        ?author p:P27 ?citizenship .
        ?citizenship rdf:type wikibase:BestRank .
        OPTIONAL { ?citizenship pq:P580 ?citizenship_startTime . }
        OPTIONAL { ?citizenship pq:P582 ?citizenship_endTime . }
        FILTER (
            (!BOUND(?citizenship_startTime) || ?citizenship_startTime <= ?articlePublicationDate) &&
            (!BOUND(?citizenship_endTime) || ?citizenship_endTime > ?articlePublicationDate)
        )
        ?citizenship ps:P27 ?wd_country_value .
        FILTER (!ISBLANK(?wd_country_value) && ?wd_country_value NOT IN (
            wd:Q18097, wd:Q1152445, wd:Q1128483, wd:Q108746595, wd:Q223050
        ))
        OPTIONAL { ?wd_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?articlePublicationDate >= ?country_Inception)
        OPTIONAL { ?wd_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?articlePublicationDate < ?country_EndDate)
    }

    # Find nationality in Genderize
    OPTIONAL {
        ?author genz:nationality ?iso .
        ?genderize_country_value wdt:P297 ?iso .
        OPTIONAL { ?genderize_country_value wdt:571 ?country_Inception . }
        FILTER (!BOUND(?country_Inception) || ?articlePublicationDate >= ?country_Inception)
        OPTIONAL { ?genderize_country_value wdt:P576 ?country_EndDate . }
        FILTER (!BOUND(?country_EndDate) || ?articlePublicationDate < ?country_EndDate)
    }
    BIND (COALESCE(?wd_country_value, ?genderize_country_value, "unknown") AS ?country_value)

    BIND (
        COALESCE(
            IF(?country_value = wd:Q55, wd:Q29999, 1/0), 
            IF(?country_value = wd:Q756617, wd:Q35, 1/0), 
            IF(?country_value IN (wd:Q21, wd:Q22, wd:Q25, wd:Q42406), wd:Q145, 1/0), 
            IF(?country_value = wd:Q15124, wd:Q38, 1/0), 
            IF(?country_value = wd:Q188736, wd:Q225, 1/0), 
            IF(?country_value IN (wd:Q29520, wd:Q14773), wd:Q148, 1/0), 
            IF(?country_value = wd:Q1335, wd:Q77, 1/0), 
            IF(?country_value = wd:Q320015, wd:Q739, 1/0), 
            IF(?country_value = wd:Q205784, wd:Q717, 1/0), 
            IF(?country_value = wd:Q1018839, wd:Q30, 1/0), 
            IF(?country_value = wd:Q47588, wd:Q29, 1/0), 
            IF(?country_value = wd:Q5689, wd:Q33, 1/0), 
            ?country_value 
        ) AS ?authorCountry
    )

    OPTIONAL {
        ?authorCountry wdt:P30 ?continent_value .
        FILTER (?continent_value IN (wd:Q15, wd:Q18, wd:Q46, wd:Q48, wd:Q49, wd:Q55643))
        BIND (
            COALESCE(
                IF(?authorCountry = wd:Q23681, wd:Q48, 1/0), 
                IF(?authorCountry = wd:Q804, wd:Q49, 1/0), 
                IF(?authorCountry = wd:Q730, wd:Q18, 1/0), 
                ?continent_value
            ) AS ?continentDirect
        )
    }
    BIND (
        IF(BOUND(?continentDirect), ?continentDirect, COALESCE(
            IF(?authorCountry IN (wd:Q26988, wd:Q712, wd:Q691, wd:Q683, wd:Q678), wd:Q55643, 1/0)
        )) AS ?continent
    )
    BIND (COALESCE(?continent, "unknown") AS ?authorContinent)

    ### Affiliation ###
    ?author p:P108 ?employment .
    ?employment rdf:type wikibase:BestRank .
    OPTIONAL { ?employment pq:P580 ?employment_startTime . }
    OPTIONAL { ?employment pq:P582 ?employment_endTime . }
    FILTER (
        (BOUND(?employment_startTime) || BOUND(?employment_endTime)) &&
        (!ISBLANK(?employment_startTime) || !ISBLANK(?employment_endTime)) &&
        (!BOUND(?employment_startTime) || ?employment_startTime <= ?articlePublicationDate) &&
        (!BOUND(?employment_endTime) || ?employment_endTime > ?articlePublicationDate)
    )

    ?employment ps:P108 ?org .
    {
        SELECT (SAMPLE(?organization) AS ?org) ?rorid WHERE {
            SELECT ?organization (SAMPLE(?roridValue) AS ?rorid) WHERE { ?organization wdt:P6782 ?roridValue . }
            GROUP BY ?organization HAVING (COUNT(DISTINCT ?roridValue) = 1)
        }
        GROUP BY ?rorid
        HAVING (COUNT(DISTINCT ?organization) = 1)
    }
    ?org wdt:P6782 ?rorid .
    ?rorOrganization ror:id ?rorid .
    ?rorOrganization ror:location ?rorLocation .

    OPTIONAL {
        ?rorLocation wdt:P30 ?continent_value_ror .
        FILTER (?continent_value_ror IN (wd:Q15, wd:Q18, wd:Q46, wd:Q48, wd:Q49, wd:Q55643))
        BIND (
            COALESCE(
                IF(?rorLocation = wd:Q23681, wd:Q48, 1/0), 
                IF(?rorLocation = wd:Q804, wd:Q49, 1/0), 
                IF(?rorLocation = wd:Q730, wd:Q18, 1/0), 
                ?continent_value_ror
            ) AS ?continentDirect_ror
        )
    }
    BIND (
        IF(BOUND(?continentDirect_ror), ?continentDirect_ror, COALESCE(
            IF(?rorLocation IN (wd:Q26988, wd:Q712, wd:Q691, wd:Q683, wd:Q678), wd:Q55643, 1/0)
        )) AS ?continent_ror
    )
    BIND (COALESCE(?continent_ror, "unknown") AS ?rorContinent)
}
}
FILTER (?authorContinent != "unknown" && ?rorContinent != "unknown")
?authorContinent rdfs:label ?ac_label .
FILTER (LANG(?ac_label) = "en")
}
GROUP BY ?ac_label
ORDER BY ?ac_label
"""


def main():
    arguments = get_arg_parser().parse_args()

    print(f"Waiting for response...")
    matrix = query_endpoint(arguments.url, QUERY_MATRIX)
    tot = query_endpoint(arguments.url, QUERY_TOT_AFF_CITIZENS)

    create_figure(matrix, tot)


if __name__ == '__main__':
    main()