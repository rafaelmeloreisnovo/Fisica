# Física — RAFAELIA

Repositório para documentação, modelos, simulações e protocolos experimentais de física com **separação explícita entre referência, hipótese, simulação e medição**.

## Documentação técnica

- [`docs/propulsao_hall/BASE_ACADEMICA_E_INVARIANTES.md`](docs/propulsao_hall/BASE_ACADEMICA_E_INVARIANTES.md) — base acadêmica, equações, invariantes, protocolo experimental, disciplina estatística e limites patentários para propulsão Hall.
- [`docs/GEOPHYSICAL_PIEZOELECTRIC_TRIBOLUMINESCENCE_RADIATION_INVARIANT.md`](docs/GEOPHYSICAL_PIEZOELECTRIC_TRIBOLUMINESCENCE_RADIATION_INVARIANT.md) — síntese multiescala de sólidos, sismos, quartzo, radiação, amortecimento e observação.
- [`docs/GEOPHYSICAL_TRANSDUCTION_EXECUTABLE_GATE.md`](docs/GEOPHYSICAL_TRANSDUCTION_EXECUTABLE_GATE.md) — implementação executável com registro DOI, comparadores físicos, torneio de mecanismos e testes adversariais.
- [`docs/GEOPHYSICAL_REAL_DATA_RECEIPT.md`](docs/GEOPHYSICAL_REAL_DATA_RECEIPT.md) — manifesto de canais crus, relógios, calibrações, controles quartzo/sem-quartzo, hashes e recibo determinístico para futura medição física.
- [`docs/SOLID_EARTH_HUM_DEEP_WATER_AND_SCALE_BOUNDARIES.md`](docs/SOLID_EARTH_HUM_DEEP_WATER_AND_SCALE_BOUNDARIES.md) — extensão para microseísmos, hum terrestre, fluxo subterrâneo, água em minerais e limites de escala radiativa.

## Execução dos gates geofísicos

```bash
python3 src/geophysical_transduction.py validate-registry \
  data/literature/geophysical_transduction_sources.json
python3 src/geophysical_transduction.py evaluate-manifest \
  configs/geophysical_transduction_experiment.example.json
python3 src/geophysical_run_receipt.py validate-run \
  tests/fixtures/geophysical_run/manifest.json
python3 src/solid_earth_hydrology.py validate-registry \
  data/literature/solid_earth_hydrology_sources.json
python3 src/solid_earth_hydrology.py classify-period 100
python3 -m pytest -q \
  tests/test_geophysical_transduction.py \
  tests/test_geophysical_run_receipt.py \
  tests/test_solid_earth_hydrology.py
```

O manifesto conceitual começa sem dados e deve retornar `winner=TOKEN_VAZIO`. O manifesto de dados crus distingue `synthetic_fixture` de `physical_measurement`: um fixture sintético testa integridade, mas nunca vira evidência. `READY_FOR_ANALYSIS` também não equivale a causalidade física. Sinal óptico ou de rádio não é promovido a raio X sem espectro, calibração, controle de fundo, atenuação e balanço energético.

## Regra de evidência

```text
conceito != modelo validado != simulação reproduzível
         != protótipo != ensaio independente != patente concedida
```

Estados aceitos: `REFERENCE`, `HYPOTHESIS`, `SIMULATED`, `MEASURED`, `REPLICATED`, `IP_CANDIDATE` e `TOKEN_VAZIO`.

## Escopo e autoria

Conteúdo autoral de Rafael Melo Reis no ecossistema RAFAELIA. Referências externas permanecem atribuídas às respectivas fontes. Alegações técnicas, acadêmicas, econômicas ou patentárias só devem ser promovidas quando acompanhadas de evidência verificável.

> Este repositório não substitui revisão por pares, avaliação de segurança, certificação de engenharia ou parecer jurídico profissional.
