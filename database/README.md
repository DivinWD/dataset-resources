# The content of the dataset file

The dataset is available on Zenodo as a single [RDF/N-Triples](https://www.w3.org/TR/n-triples/) file, where each line follows the form:

```
<subject> <predicate> <object> .
```

Subjects, predicates, and objects are collectively referred to as _terms_ and are represented by URIs (though objects may also be other data types, such as strings).

## The Wikidata subgraph
This file contains a subgraph of the Wikidata knowledge graph (as of May 2025). It includes triples related to scholarly articles, authors, and their employers as examined in the study. Wikidata defines a precise [RDF dump format](https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format) that describes how entities, statements, and other elements of the Wikidata data model map to RDF formats and what URIs identify terms.

The file contains triples with the following Wikidata predicates:

* Article-related predicates:
```
Publication date
<http://www.wikidata.org/prop/direct/P577>

Language of work or name
<http://www.wikidata.org/prop/direct/P407>

Author
<http://www.wikidata.org/prop/direct/P50>
```

* Author-related predicates:
```
Gender
<http://www.wikidata.org/prop/direct/P21>

Country of citizenship
<http://www.wikidata.org/prop/P27>
<http://www.wikidata.org/prop/statement/P27>

Employer
<http://www.wikidata.org/prop/P108>
<http://www.wikidata.org/prop/statement/P108>
```

* Employer-related predicates:
```
ROR ID
<http://www.wikidata.org/prop/direct/P6782>
```

* Country-related predicates:
```
Inception
<http://www.wikidata.org/prop/direct/P571>

Dissolved
<http://www.wikidata.org/prop/direct/P576>

Continent
<http://www.wikidata.org/prop/direct/P30>

Member of
<http://www.wikidata.org/prop/P463>

ISO 3166-1 alpha-2 code
<http://www.wikidata.org/prop/direct/P297>
```

* Other predicates:
```
Instance of
<http://www.wikidata.org/prop/direct/P31>

Start time and end time (used as qualifiers)
<http://www.wikidata.org/prop/qualifier/P580>
<http://www.wikidata.org/prop/qualifier/P582>

Type (used to select best-ranked statements)
<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
```

## Notes on pseudonymization and data enhancement

The Wikidata subgraph has been modified through pseudonymization and the addition of new triples representing information derived from external data sources (bibliographic databases, Genderize, and ROR).

### Pseudonymization

Wikidata maps entities and statements to RDF terms, each assigned a unique identifier. We replace these identifiers with pseudonyms consisting of a prefix—`X` for entities and `XS` for statements—followed by a randomly chosen number. Statements are also pseudonymized because their identifiers contain references to subject identifiers. Related URIs are mapped to new ones as follows:

```
http://www.wikidata.org/entity/

becomes

https://divinwd.dev/wd/entity/
```

For example, the Wikidata term `<http://www.wikidata.org/entity/Q42>` becomes `<http://divinwd.dev/wd/entity/X34>`, where `Q42` maps to the pseudonym `X34`.

```
http://www.wikidata.org/entity/statement/

becomes

https://divinwd.dev/wd/entity/statement/
```

For example, the Wikidata term `<http://www.wikidata.org/entity/statement/Q42-4cc>` becomes `<http://divinwd.dev/wd/entity/statement/X901>`, where `Q42-4cc` maps to `X901`.

The following entities remain unchanged:
* Article languages (values for `language (P407)`)
* Values for `sex or gender (P21)`
* Countries (values for `country of citizenship (P27)`)
* `scholarly article (Q13442814)`, `human (Q5)`, and continents (`Africa (Q15)`, `Asia (Q48)`, `Europe (Q46)`, `North America (Q49)`, `Oceania (Q55643)`, `South America (Q18)`)

### Data enhancement

Additional triples have been added to represent information extracted from external sources: Crossref, OpenAlex, Semantic Scholar, Genderize, and ROR.

#### Crossref and OpenAlex

Crossref and OpenAlex provide article language information, encoded using the predicate `https://divinwd.dev/oacr/lang`. The subject is an article and the object is a Wikidata entity representing a language. For example, if `X12` is an article written in English (identified by `Q1860` in Wikidata), the corresponding triple is:

```
<https://divinwd.dev/wd/entity/X12> <https://divinwd.dev/oacr/lang> <http://www.wikidata.org/entity/Q1860> .
```

#### Semantic Scholar

Semantic Scholar provides information about article fields of study. We distinguish between data from Semantic Scholar labels and predictions from the [S2FOS model](https://github.com/allenai/s2_fos): the predicate `https://divinwd.dev/semanticscholar/fos/value` is used for values available in Semantic Scholar, while `https://divinwd.dev/semanticscholar/fos/prediction` is used for model predictions. Both predicates are followed by a string representing one of the 23 Semantic Scholar categories, with the subject being an article.

```
<https://divinwd.dev/wd/entity/X45> <https://divinwd.dev/semanticscholar/fos/value> "art" .
<https://divinwd.dev/wd/entity/X43> <https://divinwd.dev/semanticscholar/fos/prediction> "art" .
```

#### Genderize

Genderize estimates author gender and nationality. The predicate `https://divinwd.dev/genderize/gender` is followed by either `"male"` or `"female"`, while `https://divinwd.dev/genderize/nationality` is followed by an ISO 3166-1 alpha-2 country code. In both cases, the subject is an author.

```
<https://divinwd.dev/wd/entity/X88> <https://divinwd.dev/genderize/gender> "female" .
<https://divinwd.dev/wd/entity/X42> <https://divinwd.dev/genderize/nationality> "JP" .
```

#### ROR

ROR organizations are mapped to terms using `https://divinwd.dev/ror/org/` as a prefix followed by their respective ROR IDs. The predicate `https://divinwd.dev/ror/id` links the organization to its corresponding ROR ID, encoded as a string literal. The predicate `https://divinwd.dev/ror/type` is followed by a string representing one of the 9 ROR-defined categories: ```"archive"```, ```"company"```, ```"education"```, ```"facility"```, ```"funder"```, ```"government"```, ```"healthcare"```, ```"nonprofit"```, ```"other"```,. Finally, `https://divinwd.dev/ror/location` is followed by a country represented as a Wikidata entity.

```
<https://divinwd.dev/ror/org/abcde> <https://divinwd.dev/ror/id> "abcde" .
<https://divinwd.dev/ror/org/abcde> <https://divinwd.dev/ror/type> "other" .
<https://divinwd.dev/ror/org/abcde> <https://divinwd.dev/ror/location> <http://www.wikidata.org/entity/Q408> .
```