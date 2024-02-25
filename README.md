# Installation

## turkishnlp
```
pip install turkishnlp
```

## langdetect
```
pip install langdetect
```

# Run
- Notes: 
- It must be run on src directory.
- In the src directory, there must be "turkish_dump_input", and "turkish_dump_test" files. Google Drive links of those files are given in the report.
- Without training, perplexity and sentence generation won't work.
- Jupyter Notebook file is given for testing (after training and providing dump files).

## training
```
python train_ngrams.py
```

## perplexity
```
python perplexity.py
```

## sentence generation
```
python sentence_generator.py
```

- Details of the implementation, and results are in the doc.
- I shared example result as Jupyter Notebook, after training it can also be used for testing.