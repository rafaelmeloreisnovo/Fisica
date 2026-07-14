# Propulsão Hall — base acadêmica, invariantes e disciplina de evidência

**Estado:** documento técnico de enquadramento; não constitui resultado experimental, parecer jurídico, pedido de patente ou declaração de desempenho.

**Data de consolidação:** 2026-07-14  
**Autor do projeto:** Rafael Melo Reis  
**Método de organização:** DeepRafa2 / engenharia de evidência

---

## 1. Objetivo e limite epistemológico

Este documento converte o conteúdo conceitual da sessão sobre “motor Hall” em uma base tecnicamente coerente e academicamente auditável.

A separação fundamental é:

```text
conceito != modelo matemático validado != simulação reproduzível
         != protótipo != ensaio independente != patente concedida
```

Toda alegação deve possuir um estado explícito:

| Estado | Significado |
|---|---|
| `REFERENCE` | estabelecido em literatura técnica citada |
| `HYPOTHESIS` | proposição testável ainda sem validação |
| `SIMULATED` | resultado produzido por simulação reproduzível |
| `MEASURED` | medição com instrumento, incerteza e cadeia de custódia |
| `REPLICATED` | repetido em execução independente |
| `IP_CANDIDATE` | possível família inventiva; anterioridade pendente |
| `TOKEN_VAZIO` | evidência necessária ausente |

Nenhum número originado apenas em conversa deve ser promovido a `MEASURED`, `REPLICATED` ou “patente”.

---

## 2. Desambiguação obrigatória

### 2.1 Propulsor Hall

Um **Hall-effect thruster (HET)** é um dispositivo de propulsão elétrica espacial. Ele ioniza um propelente e acelera íons por campo elétrico; um campo magnético transversal reduz a mobilidade axial dos elétrons e sustenta a descarga.

Vetor físico mínimo:

\[
\mathbf{x}_{HET}=
(V_d,I_d,\dot m,B,T_w,p,F,I_{sp},\eta_T)
\]

### 2.2 Motor BLDC com sensores Hall

Um **motor BLDC com sensores Hall** é uma máquina eletromecânica rotativa cuja comutação utiliza sensores do efeito Hall para estimar a posição do rotor.

Vetor mínimo:

\[
\mathbf{x}_{BLDC}=(V,I,\omega,\tau,\theta,T,\eta)
\]

### 2.3 Regra de não-colisão semântica

Aplicações como bicicletas, scooters, robôs terrestres, bombas e ventiladores pertencem normalmente ao domínio BLDC/atuadores elétricos, e não demonstram propulsão Hall de plasma.

A aplicação inicial coerente para um HET é uma **bancada de caracterização em vácuo**, seguida, apenas após validação, de integração com subsistema espacial.

---

## 3. Invariantes físicos

### 3.1 Conservação de massa

\[
\frac{\partial \rho}{\partial t}+\nabla\cdot(\rho\mathbf{u})=S_m
\]

Em balanço estacionário simplificado:

\[
\dot m_{in}\approx
\dot m_{ions}+\dot m_{neutral}+\dot m_{loss}
\]

A vazão deve ser medida e registrada com unidade, calibração e incerteza.

### 3.2 Conservação de momento e empuxo

Para uma aproximação unidimensional:

\[
F \approx \dot m_i v_i + (p_e-p_a)A_e
\]

A validade dessa expressão depende das hipóteses de escoamento, distribuição de velocidades, espécies iônicas e condições da câmara.

### 3.3 Velocidade iônica idealizada

Para um íon de carga \(q\) acelerado por potencial \(V_a\):

\[
v_i\approx \sqrt{\frac{2qV_a}{m_i}}
\]

Esta é uma aproximação energética, não um substituto para diagnóstico do feixe.

### 3.4 Impulso específico

\[
I_{sp}=\frac{F}{\dot m g_0}
\]

Logo:

\[
F=\dot m g_0 I_{sp}
\]

Essa identidade funciona como gate dimensional entre empuxo, vazão e impulso específico.

### 3.5 Balanço de potência

\[
P_{in}=V_d I_d+P_{magnets}+P_{cathode}+P_{control}+P_{aux}
\]

Uma eficiência propulsiva frequentemente usada é:

\[
\eta_T=\frac{F^2}{2\dot m P_{in}}
\]

A equação deve ser acompanhada pela definição exata da fronteira do sistema. Omitir cátodo, bobinas, controle ou cargas auxiliares gera comparação enganosa.

### 3.6 Condições de magnetização

A literatura de referência descreve a separação operacional desejada entre elétrons magnetizados e íons aproximadamente não magnetizados no canal.

Raio de Larmor eletrônico:

\[
r_e=\frac{v_{\perp e}}{\omega_{ce}}\ll L
\]

Parâmetro Hall eletrônico:

\[
\Omega_e^2=\frac{\omega_{ce}^2}{\nu^2}\gg 1
\]

Raio de Larmor iônico em relação à escala do canal:

\[
r_i=\frac{v_i}{\omega_{ci}}\gg L
\]

Essas relações não definem sozinhas um projeto ótimo; estabelecem restrições físicas iniciais.

### 3.7 Consistência dimensional

Toda fórmula candidata deve conservar dimensões:

```text
[eta] = 1
[F]   = N
[P]   = W
[Isp] = s
[B]   = T
[mdot]= kg/s
```

Uma expressão que some temperatura, pressão, campo magnético e corrente sem normalização ou coeficientes dimensionais é rejeitada pelo gate `DIMENSIONAL_FAIL`.

---

## 4. Vetor DeepRafa2 para o HET

O ciclo operacional defensável é:

```text
intenção -> hipótese -> modelo físico -> instrumento -> dado bruto
-> controle de qualidade -> modelo estatístico -> decisão -> novo ensaio
```

Forma discreta:

\[
x_{t+1}=F(x_t,u_t,y_t,e_t)
\]

com:

- \(x_t\): estado estimado do sistema;
- \(u_t\): ação de controle;
- \(y_t\): observação instrumental;
- \(e_t=y_t-\hat y_t\): resíduo;
- \(F\): dinâmica física ou híbrida.

### 4.1 Modelo híbrido físico-estatístico

Um modelo de aprendizado de máquina só deve complementar, e não apagar, os invariantes físicos:

\[
\hat x_{t+1}=f_{physics}(x_t,u_t)+r_\theta(x_t,u_t)
\]

onde \(r_\theta\) aprende o resíduo do modelo físico.

### 4.2 Função de otimização candidata

\[
\max_u J =
\eta_T
-\lambda_1\sigma_F
-\lambda_2 T_w^{norm}
-\lambda_3 R_{erosion}
-\lambda_4 P_{aux}^{norm}
\]

sujeita a:

\[
T_w\leq T_{max},\quad
I_d\leq I_{max},\quad
p\leq p_{max},\quad
u_{control}\leq \nu_{safe}
\]

A função é uma especificação de pesquisa. Os pesos \(\lambda_i\) permanecem `TOKEN_VAZIO` até definição do caso de uso.

---

## 5. Protocolo experimental mínimo

### 5.1 Infraestrutura

- câmara de vácuo com curva de bombeamento documentada;
- medição de pressão compatível com o regime experimental;
- fonte de potência com telemetria de tensão e corrente;
- alimentação de propelente com controlador de vazão calibrado;
- sistema de ignição e cátodo com intertravamentos;
- suporte térmico e elétrico compatível;
- bancada de empuxo calibrável;
- aquisição sincronizada e relógio de amostragem conhecido;
- proteção contra alta tensão, implosão, asfixia e superfícies quentes.

### 5.2 Variáveis mínimas

| Variável | Unidade | Instrumento/derivação | Estado inicial |
|---|---:|---|---|
| pressão de fundo | Pa | medidor de vácuo | `TOKEN_VAZIO` |
| vazão de propelente | kg/s ou sccm | MFC calibrado | `TOKEN_VAZIO` |
| tensão de descarga | V | aquisição elétrica | `TOKEN_VAZIO` |
| corrente de descarga | A | aquisição elétrica | `TOKEN_VAZIO` |
| potência auxiliar | W | soma instrumentada | `TOKEN_VAZIO` |
| campo magnético | T | gaussímetro/mapeamento | `TOKEN_VAZIO` |
| temperatura de parede | K | termopar/IR validado | `TOKEN_VAZIO` |
| empuxo | N | thrust stand | `TOKEN_VAZIO` |
| espectro de corrente | A²/Hz | FFT com janela declarada | `TOKEN_VAZIO` |

### 5.3 Cadeia de custódia

Cada execução deve produzir:

```text
run_id
commit_sha
hardware_revision
sensor_serials
calibration_ids
utc_start
utc_end
sampling_rate_hz
raw_data_sha256
environment
operator_notes
known_anomalies
```

### 5.4 Incerteza

Um resultado sem incerteza é incompleto. Para uma grandeza derivada \(z=f(x_1,...,x_n)\), usar propagação apropriada, por exemplo:

\[
u_z^2\approx
\sum_i\left(\frac{\partial f}{\partial x_i}\right)^2u_{x_i}^2
+2\sum_{i<j}\frac{\partial f}{\partial x_i}\frac{\partial f}{\partial x_j}\operatorname{cov}(x_i,x_j)
\]

Registrar também resolução, repetibilidade, drift e erro sistemático conhecido.

---

## 6. Estatística e aprendizado de máquina

### 6.1 Ordem correta

1. definir a variável-alvo;
2. estabelecer baseline físico ou estatístico simples;
3. congelar protocolo de divisão treino/validação/teste;
4. impedir vazamento temporal ou entre execuções;
5. medir calibração e incerteza;
6. avaliar drift;
7. testar fora do domínio de treino;
8. manter fallback determinístico.

### 6.2 Padrões “ocultos”

PCA, clustering, análise espectral e redes neurais podem revelar estruturas candidatas, mas não demonstram causalidade por si.

Um padrão só é promovido quando possui:

\[
\mathcal P=(detecção,repetibilidade,controle,generalização,hipótese\ causal)
\]

### 6.3 Predição de vida remanescente

Forma candidata:

\[
RUL_t=f_\theta(I_d^{t-k:t},V_d^{t-k:t},B^{t-k:t},T_w^{t-k:t},S_I(f))
\]

Estado atual: `HYPOTHESIS`. Falta dataset longitudinal com eventos de degradação e rótulo confiável.

---

## 7. Livro de alegações da sessão

| Alegação anterior | Classificação correta |
|---|---|
| “25% mais eficiente” | `UNVERIFIED`; sem protocolo/dataset |
| “20% de perda a cada 10 °C” | `UNVERIFIED`; relação não demonstrada |
| “5% de vibração prevê falha em 3 h” | `UNVERIFIED`; sem série temporal rotulada |
| “30% de economia” | `UNVERIFIED`; cenário sem ensaio |
| “50% de aumento de vida útil” | `UNVERIFIED`; sem teste de vida |
| “Patent A–E” | rótulos ilustrativos; não são números de depósito |
| valores financeiros | `SCENARIO_ONLY`; valuation ausente |
| status “prototipagem/concluído” | não comprovado por artefatos nesta cadeia |

Estado prudente do caso Hall nesta documentação:

```text
conceito: PRESENTE
base acadêmica: PRESENTE
modelo específico: PARCIAL
simulação reproduzível: TOKEN_VAZIO
protótipo documentado: TOKEN_VAZIO
ensaio em vácuo: TOKEN_VAZIO
patente depositada: TOKEN_VAZIO
TRL aproximado: 1–2, sujeito a auditoria
```

---

## 8. Propriedade intelectual: núcleo defensável

No Brasil, descobertas, teorias científicas, métodos matemáticos e programas de computador em si não devem ser tratados automaticamente como invenção patenteável. A estratégia correta é descrever uma solução técnica concreta, com meios, etapas, restrições e efeito técnico mensurável, e então realizar pesquisa de anterioridade.

Forma mínima de uma família candidata:

```text
problema técnico
+ arquitetura física
+ sequência operacional
+ variáveis observadas
+ ação de controle
+ efeito técnico medido
+ comparação com estado da técnica
```

Famílias candidatas, ainda sem alegação de novidade:

1. controle adaptativo fechado de descarga/vazão/campo;
2. diagnóstico de erosão e instabilidade por sinais multissensoriais;
3. gêmeo digital híbrido física + modelo residual;
4. sequência de partida e transição segura entre regimes.

Estado: `IP_CANDIDATE`; pesquisa de anterioridade e parecer profissional permanecem necessários.

---

## 9. Critérios de avanço

| Gate | Condição de passagem |
|---|---|
| `G0_TERMS` | HET e BLDC estão semanticamente separados |
| `G1_UNITS` | todas as equações passam por análise dimensional |
| `G2_MODEL` | hipóteses e condições de contorno declaradas |
| `G3_DATA` | schema, integridade e hashes disponíveis |
| `G4_CALIBRATION` | instrumentos e incertezas rastreados |
| `G5_BASELINE` | baseline simples documentado |
| `G6_REPRODUCE` | execução repetível por terceiro |
| `G7_SAFETY` | riscos e intertravamentos revisados |
| `G8_IP` | anterioridade e reivindicação técnica analisadas |
| `G9_VALUE` | custos e valuation derivados de dados, não de narrativa |

Não há promoção automática. Falta de evidência resulta em `TOKEN_VAZIO`, não em `PASS`.

---

## 10. Referências primárias e institucionais

1. D. M. Goebel; I. Katz. *Fundamentals of Electric Propulsion: Ion and Hall Thrusters*. JPL Space Science and Technology Series, 2008. https://descanso.jpl.nasa.gov/SciTechBook/series1/Goebel__cmprsd_opt.pdf
2. National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, 2023. https://doi.org/10.6028/NIST.AI.100-1
3. Brasil. Lei nº 9.279, de 14 de maio de 1996 — Lei da Propriedade Industrial, especialmente arts. 8º, 10, 11, 13 e 15. https://www.planalto.gov.br/ccivil_03/leis/l9279.htm
4. NASA Technical Reports Server — literatura técnica de propulsão elétrica e ensaios Hall. https://ntrs.nasa.gov/

---

## 11. Síntese

\[
\boxed{
validade = física + medição + incerteza + reprodução + rastreabilidade
}
\]

\[
\boxed{
DeepRafa2_{Hall} =
modelo\ físico \oplus bancada \oplus dados \oplus controle \oplus falsificabilidade
}
\]

O primeiro produto defensável deste eixo não é uma alegação de desempenho. É um **protocolo capaz de produzir evidência**.