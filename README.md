# scrape-tool

## eu_rul_of_law

```
python src/main_eu_rule_of_law.py --configfile src/config.json --outputfolder ./data/sources/eu-rule-of-law/raw-csv/ --overwrite
```

or for 2021 reports

```
python src/main_eu_rule_of_law.py --configfile src/config_eu_rule_of_law_2021.json --overwrite --xlsx --outputfolder ./data/sources/eu-rule-of-law/raw-csv/2021/
```

the --xlsx will also output .xlsx format alongside the csv file.
Assuming reports will remain standardized in the future, to process future reports modify/create `./src/config_eu_rule_of_law_2021.json` and change the `baseURL` and `docIds` so that the `baseURL + docId`
provides the URL for a report.

## download GRECO pdf files

```
python src/download_greco_pdfs.py --outputfolder data/sources/greco/raw-pdf
```

## parse GRECO pdf files

```
python src/main_greco.py --outputfolder data/sources/greco/raw-csv/ --inputfolder data/sources/greco/raw-pdf/ --overwrite
```

## download and parse freedom house reports

```
python src/main_freedomhouse.py --configfile src/config.json --outputfolder ./data/sources/freedomhouse/raw-csv/ --overwrite
```

## parse BTI rtf report files

```
python src/main_bti.py --datafolder ./data/sources/bti/raw-rtf/ --outputfolder ./data/sources/bti/raw-csv/ --overwrite
```

### download freedomhouse complete book archives

```
python src/download_freedomhouse_archive_pdfs.py --outputfolder ./data/source/freedomhouse/raw-pdf/
```

## generate dataset

```
python src/generate_dataset.py --rootfolder data/sources/ --outputfilename ./all_countries_0.0.4.csv
```
