# DivinWD dataset

By: Zeno Saletti, Cristian Consonni, Pedro Frau, and Emilia Gómez

This datasheet accompanies the paper *“DivinWD: Exploring the Diversity of Scientific Publications in Wikidata”*, which evaluates Wikidata’s viability as a foundation for bibliometric analysis and the computation of diversity indicator in research communities. Extracted from the May 2025 [Wikidata RDF dump](https://dumps.wikimedia.org/wikidatawiki/entities/), the dataset comprises a curated subset of scholarly articles and authors, featuring metadata such as publication dates, languages, gender, nationality, and institutional affiliations. To ensure a comprehensive record, the data is augmented with records from major bibliographic databases and attributes generated via predictive models, such as field-of-study classification and name-based demographic estimates. The dataset is released under a CC0 dedication to support reproducible research and open community analysis.

## Motivation

1.  **For what purpose was the dataset created?** *(Was there a specific task in mind? Was there a specific gap that needed to be filled? Please provide a description.)*

    The DivinWD project investigates whether Wikidata, an open and community-curated knowledge graph, can serve as a reliable foundation for bibliometric analysis and for measuring diversity across the scientific record. To ensure transparency, the project provides a dedicated dataset that supports the reproducibility of its findings regarding a specifically curated subset of scholarly articles. Even if it is based on public information, the dataset is pseudonymized to avoid overexposing personal data.

2.  **Who created this dataset (e.g., which team, research group) and on behalf of which entity (e.g., company, institution, organization)?**

    The dataset was created by Zeno Saletti, Cristian Consonni, Pedro Frau and Emilia Gómez.
    Zeno Saletti is affiliated with the University of Trento, in Trento, Italy. Cristian Consonni is affilited with the Joint Research Centre, European Commission in Ispra (VA), Italy. Pedro Frau and Emilia Gómez are affiliated with the Joint Research Centre, European Commission, Seville, Spain.

3.  **Who funded the creation of the dataset?** *(If there is an associated grant, please provide the name of the grantor and the grant name and number.)*

    This project has not received any specific funding.

4.  **Any other comments?**

    None.

## Composition

1.  **What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?** *(Are there multiple types of instances (e.g., movies, users, and ratings; people and interactions between them; nodes and edges)? Please provide a description.)*

    The dataset is structured around two primary categories of instances:

    - Articles: These instances represent the core study corpus, each enriched with metadata including publication dates, languages, fields of study, and author attributions.

    - Authors: These instances represent the individuals behind the articles. For each author, the dataset captures gender, country of citizenship, and institutional affiliations.

    To provide deeper context, these primary instances are supported by granular secondary data. Geographic data includes a country’s inception and dissolution dates, continent, UN or EU membership status, and ISO 3166-1 alpha-2 codes. Similarly, employment data tracks institutional affiliations through start and end dates, affiliation type (e.g., education, company, etc.), geographic location. Employing institutions are uniquely identified via Research Organization Registry IDs where available.

    To supplement gaps in Wikidata, the dataset incorporates external metadata from Crossref, Dimensions, OpenAlex, Scopus, Semantic Scholar, and the Research Organization Registry (ROR). Crossref and OpenAlex specifically helped identify the languages of articles where missing, while all sources—excluding ROR—informed the classification of fields of study. ROR was utilized to determine the affiliation types and locations of the institutions employing the authors. Furthermore, we employed Genderize/Nationalize to infer missing gender and nationality data. Only final results are incorporated in the dataset; for example, some articles were assigned a field of study by giving abstracts available in Crossref, Dimensions, OpenAlex, and Scopus to the *Semantic Scholar Field-Of-Study* (S2FOS) classification model, but abstracts were not embedded in the dataset and only predictions were retained.

    Relationships between instances are structured as RDF triples, each comprising a subject, a predicate, and an object. This flexible format accommodates multi-valued attributes; for instance, articles may list several publication dates or languages, just as authors can be associated with multiple genders, citizenships, or institutional affiliations. A more granular technical breakdown regarding instance identification and relationship modeling is detailed further in this section (point 4).

2.  **How many instances are there in total (of each type, if appropriate)?**

    The following table provides counts of the most relevant types of instance:

    | Type of instance  | Count     |
    |:------------------|:----------|
    | Articles          | 1,400,382 |
    | Authors           | 867,392   |
    | Institutions      | 40,621    |

    Other relevant counts include:
    |                   |           |
    |:---               |:---       |
    | Languages         | 78†       |
    | Fields of study   | 23††      |
    | Gender values     | 3†††      |
    | Countries         | 441‡      |
    | Affiliation types | 9‡‡       |

    †Number of distinct language values without aggregating variants, such as Australian English and Indian English. The article aggregates and identifies 54 languages in total, considering the 2010-2024 timeframe.

    ††Fields of study as listed by [Semantic Scholar](https://www.semanticscholar.org): agricultural and food sciences, art, biology, business, chemistry, computer science, economics, education, engineering, environmental science, geography, geology, history, law, linguistics, materials science, mathematics, medicine, philosophy, physics, political science, psychology, sociology.

    †††This entry counts the dataset's three macro-categories: female, male, and other. The latter includes authors identified on Wikidata as neither exclusively male nor female. To ensure anonymity given the small sample size (roughly 360), these diverse non-binary identities were aggregated under a single pseudonymized label. The original gender values are detailed in the accompanying article.

    ‡This value refers to the amount of countries that can be observed in the dataset, including regions, domains, and sovereign states that no longer exist. Between 2010 and 2024, about 200 countries of citizenship can be observed.

    ‡‡The number of affiliation types [as defined by ROR](https://ror.readme.io/docs/ror-data-structure#types): archive, company, education, facility, funder, government, healthcare, nonprofit, other.

3.  **Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**

    The dataset is a subset of curated articles taken from the Wikidata RDF dump of May 2025. These articles were not selected at random; they comply with the following high-level constraints:

    1. Article instances are categorized as *scholarly articles* in Wikidata.
    2. Each (distinct) author of a given article must be a *human entity*, i.e., the dataset does not contain articles which list collaborations, research groups, or any other non-human entity as author.
    3. Articles must have a consistent publication *year*. Multiple publication dates that fall in the same year are allowed.

    A more formal description of the selection process is reported in the *Collection Process* section, point 3.

4.  **What data does each instance consist of?** *(“Raw’ ’ data (e.g., unprocessed text or images) or features? In either case, please provide a description.)*

    In its raw form, the dataset consists of 23 million triples, i.e., subject-predicate-object statements. The adopted format follows the RDF/N-Triples format, where each line that comprise the file resembles the following string:

    ```
    <subject> <predicate> <object> .
    ```

    We refer to each component as a *term*. Both subjects and predicates are identified by some URI, whereas the object may be either a URI or another data type (common types are strings and dates). Most of these triples are derived from the Wikidata RDF dump, and thus follow the official [Wikidata RDF dump format](https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format). Beware that this format was partially altered by pseudonymization, which affects some URIs and identifiers used in Wikidata. Furthermore, data taken from external sources are encoded using terms defined at the time of creation of the dataset.

    #### Wikidata subgraph
    Triples gathered from the Wikidata knowledge graph contain the following predicates:

    - Article-related predicates (the subject is an article's URI)
    ```
    Publication date
    <http://www.wikidata.org/prop/direct/P577>

    Language of work or name
    <http://www.wikidata.org/prop/direct/P407>

    Author
    <http://www.wikidata.org/prop/direct/P50> (the object is an author's URI)
    ```

    - Author-related predicates (the subject is an author's URI)
    ```
    Gender
    <http://www.wikidata.org/prop/direct/P21>

    Country of citizenship
    <http://www.wikidata.org/prop/P27>: it points to a statement node, which in turn uses <http://www.wikidata.org/prop/statement/P27> to link to the final object.

    Employer
    <http://www.wikidata.org/prop/P108>: it points to a statement node, which in turn uses <http://www.wikidata.org/prop/statement/P108> to link to the final object.
    ```

    - Employer-related predicates (the subject is an author's employer):
    ```
    ROR ID
    <http://www.wikidata.org/prop/direct/P6782>
    ```

    - Country-related predicates (the subject is a country):
    ```
    Inception
    <http://www.wikidata.org/prop/direct/P571>

    Dissolved
    <http://www.wikidata.org/prop/direct/P576>

    Continent
    <http://www.wikidata.org/prop/direct/P30>

    Member of
    <http://www.wikidata.org/prop/P463>: it points to a statement node, which in turn uses <http://www.wikidata.org/prop/statement/P463> to link to the final object.

    ISO 3166-1 alpha-2 code
    <http://www.wikidata.org/prop/direct/P297>
    ```

    - Other predicates:
    ```
    Instance of
    <http://www.wikidata.org/prop/direct/P31>

    Start time and end time (used as qualifiers. Their subject is a statement URI, e.g., statements related to authors' employers and nationality)
    <http://www.wikidata.org/prop/qualifier/P580>
    <http://www.wikidata.org/prop/qualifier/P582>

    Type (used to select best-ranked statements, e.g., citizenship and employer statements)
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
    ```

    #### Data enhancement
    Additional triples have been added to represent information extracted from external sources.
    
    - Crossref and OpenAlex provide article language information, encoded using the predicate ```https://divinwd.dev/oacr/lang```. The subject is an article and the object is a Wikidata entity representing a language.

    - Semantic Scholar provides information about article fields of study. We distinguish between data from Semantic Scholar labels and predictions from the S2FOS model: the predicate ```https://divinwd.dev/semanticscholar/fos/value``` is used for values available in Semantic Scholar, while ```https://divinwd.dev/semanticscholar/fos/prediction``` is used for model predictions. Both predicates are followed by a string representing one of the 23 Semantic Scholar categories, with the subject being an article.

    - Genderize/Nationalize estimates author gender and nationality. The predicate ```https://divinwd.dev/genderize/gender``` is followed by either ```"male"``` or ```"female"```, while ```https://divinwd.dev/genderize/nationality``` is followed by an ISO 3166-1 alpha-2 country code. In both cases, the subject is an author.

    - ROR organizations are mapped to terms using ```https://divinwd.dev/ror/org/``` as a prefix followed by their respective ROR IDs. The predicate ```https://divinwd.dev/ror/id``` links the organization to its corresponding ROR ID, encoded as a string literal. The predicate ```https://divinwd.dev/ror/type``` is followed by a string representing one of the 9 ROR-defined categories: ```"archive"```, ```"company"```, ```"education"```, ```"facility"```, ```"funder"```, ```"government"```, ```"healthcare"```, ```"nonprofit"```, ```"other"```. Finally, ```https://divinwd.dev/ror/location``` is followed by a country represented as a Wikidata entity.

    #### Pseudonymization

    Wikidata maps entities and statements to RDF terms, each assigned a unique identifier. We replaced these identifiers with pseudonyms consisting of a prefix—`X` for entities and `XS` for statements—followed by a randomly chosen number. Statement URIs were also pseudonymized because their identifiers contain references to subject identifiers. Related prefixes are mapped to new ones as follows:

    ```
    http://www.wikidata.org/entity/
    http://www.wikidata.org/entity/statement/

    become

    https://divinwd.dev/wd/entity/
    https://divinwd.dev/wd/entity/statement/
    ```

    For example, the Wikidata term `<http://www.wikidata.org/entity/Q42>` becomes `<http://divinwd.dev/wd/entity/X34>`, where `Q42` maps to the pseudonym `X34`, and `<http://www.wikidata.org/entity/statement/Q42-4cc>` becomes `<http://divinwd.dev/wd/entity/statement/X901>`, where `Q42-4cc` maps to `X901`.

    The following entities remain unchanged:
    * Article languages (values for `language (P407)`).
    * Values for `sex or gender (P21)`.
    * Countries (values for `country of citizenship (P27)`).
    * Useful constants: `scholarly article (Q13442814)`, `human (Q5)`, and continents (`Africa (Q15)`, `Asia (Q48)`, `Europe (Q46)`, `North America (Q49)`, `Oceania (Q55643)`, `South America (Q18)`).

    No readable labels are provided, except for country labels (predicate ```http://www.w3.org/2000/01/rdf-schema#label```). This means that neither article titles nor author names are included in the dataset.

5.  **Is there a label or target associated with each instance? If so, please provide a description.**

    There are no labels or targets.

6.  **Is any information missing from individual instances?** *(If so, please provide a description, explaining why this information is missing (e.g., because it was unavailable). This does not include intentionally removed information, but might include, e.g., redacted text.)*

    Some instances representing articles, authors, and institutions may contain gaps due to data availability. The specific missing elements and their causes are outlined below:

    - Articles: Some entries lack an associated field of study.

    - Authors: Profiles may be missing demographic or professional details, such as gender, nationality, or employment history.

    - Institutions: Certain employing organizations lack a ROR ID, preventing them from being linked to external ROR metadata (such as affiliation types or geographic locations).

    Wherever data is missing, several reasons can be provided:

    1. The data was not available in Wikidata.

    2. Information was not available in Wikidata *and* links between Wikidata instances and external ones were not found. Links are shared pieces of information used to identify records indexed by different databases: for articles, these links are DOIs (not included in the dataset), whereas ROR IDs are used for employing organizations.

    3. Even though links between Wikidata and external sources were established, the latter were not able to fill gaps.

    Details about missing data are reported (and quantified) in the article.

7.  **Are relationships between individual instances made explicit (e.g., users’ movie ratings, social network links)?** *(If so, please describe how these relationships are made explicit.)*

    Explicit relationships are expressed between articles, authors, and respective information (publication date, language, field of study, gender, country, and employers).

8.  **Are there recommended data splits (e.g., training, development/validation, testing)?** *(If so, please provide a description of these splits, explaining the rationale behind them.)*

    Sourced from the May 2025 Wikidata RDF dump, this dataset comprises articles published between 1671 and 2025 and which meet the criteria outlined in the *Collection Process* section, point 3. While we offer no specific recommendations for data partitioning, please note that the DivinWD project primarily focuses on the 2010–2024 timeframe.

9.  **Are there any errors, sources of noise, or redundancies in the dataset?** *(If so, please provide a description.)*

    Potential errors may stem from the misclassification of fields of study or inaccuracies in author demographic data (specifically gender and nationality). For further details on inference processes, please refer to point 1 of the *Collection Process* section.

    While the dataset does not contain inherent noise, its utility depends on precise querying. The authors strongly recommend using the reference queries stored in the [DivinWD/dataset-resources](https://github.com/DivinWD/dataset-resources) GitHub repository to ensure faithful reproduction of the original results.

    For authors whose names were available in Wikidata, we used those names to infer gender and nationality. Consequently, for authors who already possess gender or country-of-citizenship values within Wikidata, these attributes may appear to be repeated. However, this does not constitute a true redundancy; because the dataset utilizes the N-Triples format, the distinct origin of each data point is preserved through the use of different predicates.

    the dataset contains some unnecessary triples. Specifically, certain author URIs are linked to statement URIs via the ```http://www.wikidata.org/prop/P463``` (member of) predicate, but the corresponding values are absent from this specific dataset. These links persist because the property was originally used to identify memberships of countries in international organizations (e.g., the EU or UN). By filtering author and country data at the same time, author triples associated with predicate ```http://www.wikidata.org/prop/P463``` were included. It is important to note that corresponding objects are pseudonymized and do not point to any value.

10. **Is the dataset self‑contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)?** *(If it links to or relies on external resources, a) are there guarantees that they will exist, and remain constant, over time; b) are there official archival versions of the complete dataset (i.e., including the external resources as they existed at the time the dataset was created); c) are there any restrictions (e.g., licenses, fees) associated with any of the external resources that might apply to a future user? Please provide descriptions of all external resources and any restrictions associated with them, as well as links or other access points, as appropriate.)*

    The dataset is self-contained, in the sense that it provides all the necessary information to reproduce the results of the research. In addition, the file is [versioned on Zenodo](https://zenodo.org/records/18234750). However, the dataset captures the state of various sources gathered between April and November 2025 (for detailed timeframes, see the table in the *Collection Process* section, point 5).

    | Resource | Snapshot/Archival Available? | License | Access points and useful links |
    | :--- | :--- | :--- | :--- |
    | **Wikidata** | Yes (Monthly RDF Dumps): [Archived database dumps](https://archive.org/details/wikimediadownloads) | CC0 | [Home page](https://www.wikidata.org/wiki/Wikidata:Main_Page), [Latest database dumps](https://www.wikidata.org/wiki/Wikidata:Database_download) |
    | **Crossref** | Yes (Periodic Snapshots): [Public Data File](https://www.crossref.org/learning/public-data-file/) | CC0 | [Home page](https://www.crossref.org) |
    | **Dimensions** | No (API/Commercial) | Proprietary | [Home page](https://www.dimensions.ai), [End User Terms](https://www.dimensions.ai/policies-terms-legal/) |
    | **Genderize/Nationalize** | No (Live API) | Proprietary | [Home page](https://genderize.io), [Terms and conditions](https://genderize.io/terms) |
    | **OpenAlex** | Yes (Periodic Snapshots): [OpenAlex documentation](https://docs.openalex.org/download-all-data/openalex-snapshot) | CC0 | [Home page](https://openalex.org) |
    | **ROR** | Yes (Versioned on Zenodo): [ROR data on Zenodo](https://zenodo.org/records/18260365) | CC0 | [Home page](https://ror.org) |
    | **Scopus** | No (API/Commercial) | Proprietary | [Home page](https://www.elsevier.com/products/scopus), [Elsevier Policy](https://dev.elsevier.com/policy.html) |
    | **Semantic Scholar** | Yes (S2ORC/API) | CC BY-NC 4.0 | [Home page](https://www.semanticscholar.org), [S2FOS model repository](https://github.com/allenai/s2_fos?tab=Apache-2.0-1-ov-file), [API license agreement](https://www.semanticscholar.org/product/api/license) |

    By leveraging open-source repositories such as Crossref, OpenAlex, and ROR, this dataset incorporates direct metadata including article language and organizational information (types and locations). Additionally, the dataset provides processed attributes—fields of study, gender, and nationality. Note that while these inferences are included, the raw source inputs used to generate them are excluded from the dataset: abstracts collected from Crossref, Dimensions, OpenAlex, and Scopus allowed the classification of some articles, but they are not embedded in the dataset; author names are not included, even though they were used by Genderize/Nationalize to infer gender and nationality.

1.  **Does the dataset contain data that might be considered confidential (e.g., data that is protected by legal privilege or by doctor‑patient confidentiality, data that includes the content of individuals’ non‑public communications)?** *(If so, please provide a description.)*

    The dataset includes sensitive personal attributes, specifically authors' gender, nationality, and employers (for nationality and employment derived from Wikidata, time qualifiers may be present). While some data was gathered from records publicly available on Wikidata, a significant portion of the demographic information was inferred via Genderize/Nationalize using author names. Consequently, this dataset contains information that may not have been explicitly disclosed by the individuals.

1.  **Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?** *(If so, please describe why.)*

    No, the dataset does not contain any disturbing or outrageous content, nor is it intended to cause harm or unpleasant feelings if vewed directly.

1.  **Does the dataset relate to people?** *(If not, you may skip the remaining questions in this section.)*

    Yes. The dataset identifies individuals in their capacity as scholarly authors. Each instance characterizes an author by their demographic and professional background (gender, nationality, and employment) alongside metadata for their published work, including the publication date, language, and specific field of research.

1.  **Does the dataset identify any subpopulations (e.g., by age, gender)?** *(If so, please describe how these subpopulations are identified and provide a description of their respective distributions within the dataset.)*

    The dataset identifies several subpopulations, which are described in more detail in the article (the focus is on the 2010-2024 timeframe). In particular, authors are identified by:

    - Gender: Almost 2/3 of the authors in the dataset are male, whereas 1/3 of the others are female. A small group, accounting for a few hundreds, have other genders. A few thousands authors do not have a gender value.
    - Nationality: Since the dataset spans from 1671 to 2025 in terms of publication dates, various nationalities can be identified. Most of modern countries are located in Europe, followed by Asia and North America. Few authors come from Oceania, South America, and Africa.
    - Type of affiliation and employing location: Authors may be associated with multiple affiliation types. The most common ones are *education* and *founder*, meaning that the majority of authors are employed to, say, universities.

1.  **Is it possible to identify individuals (i.e., one or more natural persons), either directly or indirectly (i.e., in combination with other data) from the dataset?** *(If so, please describe how.)*

    In its standalone form, the dataset precludes direct identification. Original Wikidata identifiers have been replaced with pseudonyms, titles and names have been redacted, and unique persistent identifiers (such as DOIs) are excluded.
    
    While the dataset is pseudonymized, indirect identification is feasible if the dataset is cross-referenced with the original Wikidata RDF dump or external bibliographic databases (e.g., those mentioned at point 10). By correlating specific attributes, an observer could re-identify individual instances. Potential methods for re-identification include:

    - Article Triangulation: Individual papers can be isolated by combining metadata such as precise publication dates, language, specific fields of study, and authors.

    - Author Profiling: Researchers may be identified by aggregating gender, nationality, and research specializations inherited by articles' fields of study. Moreover, some subpopulation in the gender and nationality dimensions consist of only a few authors, which could ease identification.

    - Temporal Patterns: Unique publication histories can be reconstructed from the chronological sequence of publication dates, creating a "fingerprint" that matches public profiles.

1.  **Does the dataset contain data that might be considered sensitive in any way (e.g., data that reveals racial or ethnic origins, sexual orientations, religious beliefs, political opinions or union memberships, or locations; financial or health data; biometric or genetic data; forms of government identification, such as social security numbers; criminal history)?** *(If so, please provide a description.)*

    The dataset includes potentially sensitive information, specifically pertaining to biographical and professional identity: author genders and countries of citizenship; current and past employers, which may include specific geographic locations; optional time qualifiers (start and/or end dates) associated with both nationality and employment history.

1.  **Any other comments?**

    None.

## Collection Process

1.  **How was the data associated with each instance acquired?** *(Was the data directly observable (e.g., raw text, movie ratings), reported by subjects (e.g., survey responses), or indirectly inferred/derived from other data (e.g., part‑of‑speech tags, model‑based guesses for age or language)? If data was reported by subjects or indirectly inferred/derived from other data, was the data validated/verified? If so, please describe how.)*

    The majority of the dataset consists of directly observable metadata—including publication dates, languages, gender, nationality, and affiliations—extracted from the Wikidata RDF dump. In articles where language data was missing from Wikidata, values were inherited from corresponding records in Crossref and OpenAlex. For authors with available names on Wikidata, we enriched the dataset by inferring gender and nationality via the Genderize and Nationalize APIs and retaining the highest-confidence outputs.

    Regarding the thematic categorization of articles, fields of study were primarily retrieved from Semantic Scholar. Because Semantic Scholar records often contain multiple fields of study per article from various sources, we exclusively retained the primary value generated by the s2fos-model. For articles lacking this metadata, we inferred the field of study by processing abstracts collected from Crossref, Dimensions, OpenAlex, and Scopus through the Semantic Scholar Field of Study ([S2FOS](https://github.com/allenai/s2_fos)) classification model. While this model can produce multiple outputs with varying confidence levels, we consistently selected only the result with the highest confidence score.

2.  **What mechanisms or procedures were used to collect the data (e.g., hardware apparatus or sensor, manual human curation, software program, software API)?** *(How were these mechanisms or procedures validated?)*

    Raw data was aggregated from several open-access repositories—including Wikidata, Crossref, OpenAlex, and ROR—via direct downloads from their respective access points. For proprietary or specialized sources, we employed automated collection methods: metadata from Dimensions, Scopus, and Semantic Scholar was retrieved via software APIs using DOIs, while additional demographic insights were gathered through the Genderize and Nationalize APIs using name-based queries. Finally, missing field-of-study labels were computed using the S2FOS model, which processed article titles and abstracts to infer relevant classifications.

3.  **If the dataset is a sample from a larger set, what was the sampling strategy (e.g., deterministic, probabilistic with specific sampling probabilities)?**

    The articles and consequently all correlated information were selected following a deterministic strategy consisting of a set of constraints.

    Given a Wikidata entity:

    1. It must contain the statement ```instance of (P31) scholarly article (Q13442814)```.
    2. Each and every author must be a human entity, i.e., the article must reference authors exclusively via property```author (P50)```, and the object of that property must be an entity with at least the statement ```instance of (P31) human (Q5)```. Articles with non-human author entities, or authors (some or all of them) listed via property ```author name string (P2093)``` are not allowed.
    3. The article must have a consistent publication year, that is, values of statements with property ```publication date (P577)``` must fall within the same year. Articles published in multiple years are not included in the dataset.

4.  **Who was involved in the data collection process (e.g., students, crowdworkers, contractors) and how were they compensated (e.g., how much were crowdworkers paid)?**

    Data collection was conducted exclusively by the authors. No external compensation or remuneration was required.

5.  **Over what timeframe was the data collected?** *(Does this timeframe match the creation timeframe of the data associated with the instances (e.g., recent crawl of old news articles)? If not, please describe the timeframe in which the data associated with the instances was created.)*

    The data was collected between April and November 2025. Each source is continously curated and updated, thus the timeframe in which the data associated with the instances was created may span several years depending on the source.

    | Source           | Collection time | Launch time |
    |:-----------------|:----------------|:------------|
    | Wikidata         | 2025-05-01      | 2012        |
    | Crossref         | 2025-04-03      | 1999‡       |
    | Dimensions       | 2025-10-25      | 2018        |
    | OpenAlex         | 2025-05-07      | 2022        |
    | Scopus           | 2025-11-12      | 2004        |
    | Semantic Scholar | 2025-05-27      | 2015        |
    | ROR              | 2025-05-20      | 2019        |

    ‡The first public data file was released in 2020.

6.  **Were any ethical review processes conducted (e.g., by an institutional review board)?** *(If so, please provide a description of these review processes, including the outcomes, as well as a link or other access point to any supporting documentation.)*

    No formal ethical review processes were conducted.

7.  **Does the dataset relate to people?** *(If not, you may skip the remaining questions in this section.)*

    Yes. The dataset identifies individuals in their capacity as scholarly authors. Each instance characterizes an author by their demographic and professional background (gender, nationality, and employment) alongside metadata for their published work, including the publication date, language, and specific field of research.

8.  **Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources (e.g., websites)?**

    Data was primarily obtained via Wikidata, supplemented by the Research Organization Registry for affiliation types and organization locations. For incomplete records, gender and nationality were inferred using the Genderize and Nationalize APIs by providing author names available on Wikidata.

9.  **Were the individuals in question notified about the data collection?** *(If so, please describe (or show with screenshots or other information) how notice was provided, and provide a link or other access point to, or otherwise reproduce, the exact language of the notification itself.)*

    Individuals were not notified about the data collection.

10. **Did the individuals in question consent to the collection and use of their data?** *(If so, please describe (or show with screenshots or other information) how consent was requested and provided, and provide a link or other access point to, or otherwise reproduce, the exact language to which the individuals consented.)*

    Direct consent was not obtained from individuals, whose data is publicly available on Wikidata. Genderize/Nationalize inferences were based on names available on Wikidata.

1.  **If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?** *(If so, please provide a description, as well as a link or other access point to the mechanism (if appropriate).)*

    Direct consent was not obtained from individuals.

1.  **Has an analysis of the potential impact of the dataset and its use on data subjects (e.g., a data protection impact analysis) been conducted?** *(If so, please provide a description of this analysis, including the outcomes, as well as a link or other access point to any supporting documentation.)*

    No formal data protection impact assessment has been conducted. However, the accompanying paper explicitly addresses potential ethical risks—specifically those concerning demographic analysis—by building upon existing literature in the field.

    It is important to note that the dataset must not be used to detect or re-identify individuals. To enforce this, we have implemented some technical safeguards, including pseudonymization (all Wikidata identifiers have been pseudonymized) and redaction (article titles and author names have been entirely removed).

1.  **Any other comments?**

    Authors’ personal data—specifically gender, citizenship, and employment history—were primarily sourced from Wikidata, utilizing public database dumps available under a CC0 license.

    As Wikidata is a community-curated platform, we recognize that the data may not always perfectly reflect the real-world identities of the authors. Furthermore, we acknowledge the inherent limitations of tools like Genderize and Nationalize, which can struggle to accurately predict demographic data based solely on naming conventions. To address these concerns, our article cites existing literature that discusses the ethical and technical challenges associated with these data acquisition methods.

## Preprocessing/cleaning/labeling

1.  **Was any preprocessing/cleaning/labeling of the data done (e.g., discretization or bucketing, tokenization, part‑of‑speech tagging, SIFT feature extraction, removal of instances, processing of missing values)?** *(If so, please provide a description. If not, you may skip the remainder of the questions in this section.)*

    Several preprocessing and filtering steps were performed. First, the Wikidata RDF/N-Triples dump underwent a multi-stage refinement process. This involved filtering triples to include only those related to articles meeting the criteria specified in the *Collection Process* section, point 3. Additionally, we isolated triples containing the specific predicates listed in the *Composition* section, point 4. To protect privacy, all entity and statement URIs were replaced with pseudonyms prior to publication. Details about pseudonyms are available in the *Composition* section, point 4.

    Data from external repositories was also filtered and processed to augment the core Wikidata set. For records indexed by Crossref, Dimensions, OpenAlex, Scopus, and Semantic Scholar, we retained the DOI, the title, and the total number of distinct authors. After matching articles via DOIs, we assigned a single field of study to each record. This was achieved by utilizing existing Semantic Scholar labels or, where labels were unavailable, by applying the *Semantic Scholar Field of Study* ([S2FOS](https://github.com/allenai/s2_fos)) classification model to the collected abstracts. In this process, we prioritized abstracts from open-access sources, specifically Crossref and OpenAlex, and only utilized other databases if these primary sources were missing. Similarly, for records lacking language information, we assigned language codes inherited from Crossref and OpenAlex. These language codes were eventually mapped to Wikidata entities.

    Further inferences were made regarding author demographics, where name data was used to estimate gender and nationality through the Genderize and Nationalize APIs: for each author, we retreived the corresponding name on Wikidata and used it with Genderize/Nationalize to get a gender value (male/female) and country value. From ROR records, we extracted ROR IDs, organization types, and geographic locations. Finally, the processed data were encoded as triples for the final dataset. Information used during the processing and inference stages—including DOIs, titles, abstracts, and author names—was excluded from the published dataset.

2.  **Was the “raw” data saved in addition to the preprocessed/cleaned/labeled data (e.g., to support unanticipated future uses)?** *(If so, please provide a link or other access point to the “raw” data.)*

    Raw data was retained and made accessible based on the specific requirements of each source:

    - Open access sources: Raw data from Wikidata, Crossref, OpenAlex, ROR, and Semantic Scholar was preserved. Detailed access links for these repositories are provided in the table under *Composition* Section, Point 10.

    - Limited access sources: Due to licensing restrictions, data from Dimensions and Scopus cannot be distributed in bulk and requires subscription for access. While we have retained the derived results (such as field of study classifications), the raw source data, including original abstracts, was not saved.

3.  **Is the software used to preprocess/clean/label the instances available?** *(If so, please provide a link or other access point.)*

    .

4.  **Any other comments?**

    None.

## Uses

1.  **Has the dataset been used for any tasks already?** *(If so, please provide a description.)*

    The dataset has been utilized exclusively for research within the DivinWD project. Current analysis focuses on longitudinal distributions, specifically examining the volume of articles, linguistic diversity, and prominent fields of study. Additionally, the dataset has been used to evaluate demographic trends regarding gender and nationality, as well as the correlation between researchers' nationalities and their physical employment locations.

2.  **Is there a repository that links to any or all papers or systems that use the dataset?** *(If so, please provide a link or other access point.)*

    Yes. The [DivinWD organization](https://github.com/DivinWD) on GitHub serves as a centralized hub for this information. At the time of creatioin of the dataset, it contains links to essential tools designed to manage the dataset and facilitate the reproduction of the findings detailed in the original article.

3.  **What (other) tasks could the dataset be used for?**

    At this early stage, the data enables a focused analysis of a curated subset of scholarly articles within Wikidata. Beyond the relationships highlighted in our initial study, researchers could derive new insights by cross-referencing existing variables—for example, investigating the intersectional distribution of gender across various fields of study.

4.  **Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?** *(For example, is there anything that a future user might need to know to avoid uses that could result in unfair treatment of individuals or groups (e.g., stereotyping, quality of service issues) or other undesirable harms (e.g., financial harms, legal risks) If so, please provide a description. Is there anything a future user could do to mitigate these undesirable harms?)*

    Since the dataset is the result of the collection of data gathered from multiple sources, future users should be aware of the continuously evolving nature of community-curated databases such as Wikidata. The dataset is in fact a snapshot of a subset of articles and related information gathered around mid-2025. Furthermore, using the dataset to detect or identify individual authors would be inappropriate.

    To mitigate risks, the dataset should be used exclusively for inspecting and reproducing the results detailed in the original research. Furthermore, as this dataset represents a processed snapshot from mid-2025, it should not serve as a foundation for new studies. Future researchers are encouraged to access the most recent data dumps directly from the primary sources to ensure their work reflects the current state of these evolving databases.

5.  **Are there tasks for which the dataset should not be used?** *(If so, please provide a description.)*

    The dataset should not be used to identify, detect, or evaluate individual authors, to make hiring or promotion decisions. It is unsuitable for any high‑impact decisions affecting specific individuals.

6.  **Any other comments?**

    None.

## Distribution

1.  **Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?** *(If so, please provide a description.)*

    Yes, the dataset will be [publicly released via Zenodo](https://zenodo.org/records/18234750) to facilitate data sharing and accessibility within the broader research community.

2.  **How will the dataset will be distributed (e.g., tarball on website, API, GitHub)?** *(Does the dataset have a digital object identifier (DOI)?)*

    The dataset is available on Zenodo as a single Gzip-compressed N-Triples file, with the assigned DOI 10.5281/zenodo.18234750. Accompanying code and resources for handling the data are maintained in the [DivinWD/dataset-resources](https://github.com/DivinWD/dataset-resources) repository on GitHub.

3.  **When will the dataset be distributed?**

    The dataset will be distributed on January 15, 2026.

4.  **Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?** *(If so, please describe this license and/or ToU, and provide a link or other access point to, or otherwise reproduce, any relevant licensing terms or ToU, as well as any fees associated with these restrictions.)*

    Yes. All data, charts and content are released under the Creative Commons CC0 public domain dedication. The source code for the data pipeline is released under the MIT license.

5.  **Have any third parties imposed IP‑based or other restrictions on the data associated with the instances?** *(If so, please describe these restrictions, and provide a link or other access point to, or otherwise reproduce, any relevant licensing terms, as well as any fees associated with these restrictions.)*

    No third parties imposed restrictions on the data. Even though limited-access databases were used, such as Dimensions and Scopus, raw data was not embedded and it was only used for processing purposes.

6.  **Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?** *(If so, please describe these restrictions, and provide a link or other access point to, or otherwise reproduce, any supporting documentation.)*

    No export controls or regulatory restrictions apply to this dataset. It is being released into the public domain under a CC0 1.0 Universal license.

7.  **Any other comments?**

    None.

## Maintenance

1.  **Who is supporting/hosting/maintaining the dataset?**

    The dataset is hosted on Zenodo and maintained by the authors, while supporting code and resources are available via GitHub ([DivinWD/dataset-resources](https://github.com/DivinWD/dataset-resources)).

2.  **How can the owner/curator/manager of the dataset be contacted (e.g., email address)?**

    Contact information for the authors is available in the paper. Email addresses include zeno.saletti@studenti.unitn.it, cristian.consonni@acm.org, pedro.frau-amar@ext.ec.europa.eu, emilia.gomez-gutierrez@ec.europa.eu. Users can also open issues on the GitHub repository.

3.  **Is there an erratum?** *(If so, please provide a link or other access point.)*

    At the time of writing no erratum is published. Should errors in the dataset or supporting resources be discovered, they will be corrected in subsequent releases and documented on GitHub, Zenodo, and the [project page](https://divinwd.dev).

4.  **Will the dataset be updated (e.g., to correct labeling errors, add new instances, delete instances’)?** *(If so, please describe how often, by whom, and how updates will be communicated to users (e.g., mailing list, GitHub)?)*

    Yes. If errors are identified or improvements are required, the authors will update the dataset by releasing new versioned increments via Zenodo. All revisions, including changelogs and notifications of new releases, will be communicated through the GitHub repository.

5.  **If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances (e.g., were individuals in question told that their data would be retained for a fixed period of time and then deleted)?** *(If so, please describe these limits and explain how they will be enforced.)*

    There are currently no predefined limits on the data retention period.

6.  **Will older versions of the dataset continue to be supported/hosted/maintained?** *(If so, please describe how. If not, please describe how its obsolescence will be communicated to users.)*

    Yes, older versions of the dataset will be archived on Zenodo, which allow to track dataset versions through time.

7.  **If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?** *(If so, please provide a description. Will these contributions be validated/verified? If so, please describe how. If not, why not? Is there a process for communicating/distributing these contributions to other users? If so, please provide a description.)*

    Contributions are welcomed through the GitHub repository. Researchers can propose improvements by opening issues or submitting pull requests. The maintainers review contributions and, if accepted, integrate them into future releases.

8.  **Any other comments?**

    None.
