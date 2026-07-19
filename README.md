# Física — RAFAELIA

Repositório para documentação, modelos, simulações e protocolos experimentais de física com **separação explícita entre referência, hipótese, simulação e medição**.

## Documentação técnica

- [`docs/propulsao_hall/BASE_ACADEMICA_E_INVARIANTES.md`](docs/propulsao_hall/BASE_ACADEMICA_E_INVARIANTES.md) — base acadêmica, equações, invariantes, protocolo experimental, disciplina estatística e limites patentários para propulsão Hall.
- [`docs/GEOPHYSICAL_PIEZOELECTRIC_TRIBOLUMINESCENCE_RADIATION_INVARIANT.md`](docs/GEOPHYSICAL_PIEZOELECTRIC_TRIBOLUMINESCENCE_RADIATION_INVARIANT.md) — síntese multiescala de sólidos, sismos, quartzo, radiação, amortecimento e observação.
- [`docs/GEOPHYSICAL_TRANSDUCTION_EXECUTABLE_GATE.md`](docs/GEOPHYSICAL_TRANSDUCTION_EXECUTABLE_GATE.md) — implementação executável com registro DOI, comparadores físicos, torneio de mecanismos e testes adversariais.

## Execução do gate geofísico

```bash
python3 src/geophysical_transduction.py validate-registry \
  data/literature/geophysical_transduction_sources.json
python3 src/geophysical_transduction.py evaluate-manifest \
  configs/geophysical_transduction_experiment.example.json
python3 -m pytest -q tests/test_geophysical_transduction.py
```

O manifesto de exemplo começa sem dados e deve retornar `winner=TOKEN_VAZIO`; prontidão experimental não equivale a causalidade física.

## Regra de evidência

```text
conceito != modelo validado != simulação reproduzível
         != protótipo != ensaio independente != patente concedida
```

Estados aceitos: `REFERENCE`, `HYPOTHESIS`, `SIMULATED`, `MEASURED`, `REPLICATED`, `IP_CANDIDATE` e `TOKEN_VAZIO`.

## Escopo e autoria

Conteúdo autoral de Rafael Melo Reis no ecossistema RAFAELIA. Referências externas permanecem atribuídas às respectivas fontes. Alegações técnicas, acadêmicas, econômicas ou patentárias só devem ser promovidas quando acompanhadas de evidência verificável.

> Este repositório não substitui revisão por pares, avaliação de segurança, certificação de engenharia ou parecer jurídico profissional.
