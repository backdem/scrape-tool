# scrape-tool
## eu_rul_of_law
```
python src/main_eu_rule_of_law.py --configfile src/config.json --outputfolder ./data/sources/eu-rule-of-law/raw-csv/ --overwrite
```
## download GRECO pdf files
```
python src/download_greco_pdfs.py --outputfolder data/sources/greco/raw-pdf
```
## parse GRECO pdf files
```
python src/main_greco.py --outputfolder data/sources/greco/raw-csv/ --inputfolder data/sources/greco/raw-pdf/ --overwrite
```



