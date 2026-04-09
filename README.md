# qsproteome-cli

Self-documenting CLI for the QSProteome API documented at `https://qsproteome.org/api-usage`.

## Install

```bash
pip install .
```

## Inspect

```bash
qsproteome --help
qsproteome doc
qsproteome doc lookup
qsproteome doc lookup biocyc
qsproteome doc serve
```

## Lookups

```bash
qsproteome lookup biocyc ECOLI ABC-12-CPLX
qsproteome lookup complexportal CPX-4822
qsproteome lookup uniprot P0AEQ4
qsproteome lookup uniprot P0AEQ4 --iptm 0.8
qsproteome lookup pdb 2QI9
qsproteome lookup gene-signature '{"P01308": 1, "Q76KP1": 1}'
```

## Local Preview

```bash
qsproteome serve biocyc ECOLI ABC-12-CPLX
qsproteome serve complexportal CPX-4822 --port 8001
```
