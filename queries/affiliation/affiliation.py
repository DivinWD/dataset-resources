import requests
import argparse
import sys
import io
import pandas as pd
import matplotlib.pyplot as plt


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='SPARQL endpoint URL')

    return parser


def create_figure(res):
    # Parse the CSV response
    df = pd.read_csv(io.StringIO(res))
    
    # Pivot the data: rows = rorType, columns = year, values = author_count
    df_pivot = df.pivot(index='rorType', columns='year', values='author_count')
    
    # Fill NaN values with 0 (for years where a type had no authors)
    df_pivot = df_pivot.fillna(0)
    
    # Sort columns (years) to ensure proper ordering
    df_pivot = df_pivot.sort_index(axis=1)
    
    # Extract years from column names
    years = df_pivot.columns.tolist()
    
    # Mapping from raw rorType to display labels
    label_map = {
        'https://divinwd.dev/ror/type/archive': 'Archive',
        'http://www.ror.org/type/company': 'Company',
        'http://www.ror.org/type/education': 'Education',
        'http://www.ror.org/type/facility': 'Facility',
        'http://www.ror.org/type/funder': 'Funder',
        'http://www.ror.org/type/government': 'Government',
        'http://www.ror.org/type/healthcare': 'Healthcare',
        'http://www.ror.org/type/nonprofit': 'Nonprofit',
        'http://www.ror.org/type/other': 'Other'
    }
    
    # Plotting styles (markers and colors)
    markers = ['o', 's', '^', 'd', 'v', '<', '>', 'p', '*', 'h']
    colors = ['#B22222', '#D73027', '#E76F51', '#E9C46A', '#66BB6A', '#20B2AA', '#1E88E5', '#7E57C2', '#BA68C8']
    
    # Create the plot
    plt.figure(figsize=(6, 4))
    
    # Plot each organization type (each row)
    for idx, org_type in enumerate(df_pivot.index):
        marker = markers[idx % len(markers)]
        color = colors[idx % len(colors)]
        
        # Get clean label from mapping, fallback to original if not found
        display_label = label_map.get(org_type.lower(), org_type)
        
        plt.plot(years, df_pivot.loc[org_type], 
                 f'{marker}-', 
                 color=color,
                 label=display_label, 
                 linewidth=1,
                 markersize=5)
    
    plt.ylim(1, 60000)
    
    # Formatting
    plt.ylabel('Authors')
    plt.xlabel('Year')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=10, ncol=2)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig('figure.png', format='png', bbox_inches='tight', dpi=600)


QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX ror: <https://divinwd.dev/ror/>

SELECT ?year ?rorType (COUNT(DISTINCT ?author) AS ?author_count) WHERE {
    {
        SELECT ?article (MIN(?publicationDate) AS ?articlePublicationDate) WHERE {
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
        HAVING (COUNT(DISTINCT YEAR(?publicationDate)) = 1 && 2010 <= YEAR(?articlePublicationDate) && YEAR(?articlePublicationDate) <= 2024)
    }
    BIND (YEAR(?articlePublicationDate) AS ?year)


    ?article wdt:P50 ?author .
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
    # Select only organizations with a unique ror id (entities have exactly one id that is not shared with other organizations)
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
    ?rorOrganization ror:type ?rorType .
}
GROUP BY ?year ?rorType
"""


def query_endpoint(url, query):
    headers = {"Accept": "text/csv"}
    params = {"query": query, "format": "text/csv"}

    print("Waiting for response...")
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
    res = query_endpoint(arguments.url, QUERY)
    create_figure(res)


if __name__ == '__main__':
    main()