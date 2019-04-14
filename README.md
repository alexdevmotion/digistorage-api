# digistorage-api
A Python API that enables basic features provided via the [DigiStorage REST API for Developers](https://storage.rcs-rds.ro/help/developers/api).

## Prerequisites
- Python 3.6+ (may work on older versions, but didn't test)
- Required packages:
```
pip install reqests argparse
```

## Command line usage
- Copy `config.example.yaml` to `config.yaml` & fill out the `email` & `password`
- Examples:
```
python digistorage.py -h
python digistorage.py --upload=README.md --remote_path=
python digistorage.py --info --remote_path=README.md
python digistorage.py --mkdir --remote_path=new_folder
python digistorage.py --rm --remote_path=new_folder
```

## Python API usage
- Create an instance of the `DigiStorageApi` class
- You can manually pass the `email` & `password` to the `DigiStorageApi` constructor or use the same `config.yaml` approach
- Read the docs for more info
