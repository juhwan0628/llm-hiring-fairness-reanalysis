# Rozado name 추론·민감도 분석 결과

작성: 2026-09-14. 아래는 Zenodo v4 `experiment_name`의 저자 파싱 선택값을 우리가 직접 계산한 결과다. 최종 논문의 figure별 수치 재현 완료를 뜻하지 않는다. PNAS는 commit `66a9e46` 상태로 동결한다.

## 방법과 표본

[실행 명세](rozado_name_inference_spec.md)는 EDA 이후 추론 실행 전에 작성한 작업 가정이며 사전등록이 아니다. 이름 배치를 교환한 두 행을 하나의 pair로 묶고 Female 선택 비율(0, 0.5, 1)을 계산했다. 주 분석은 두 행 모두 선택값 일관성을 통과한 15,313개 pair(30,626행)다. 전체 15,399개 pair 중 86개를 주 분석에서 제외했으나 원자료·정제 표에는 보존했다.

모델별 intercept-only OLS, 직업 cluster CR1 표준오차, t(69) 양측 검정으로 평균 0.5와 비교했다. 모든 모델에서 직업 70개가 유지됐다. 주 분석은 pair 동일 가중이다. 22모델을 하나의 Holm family로 보정했다. 95% CI는 모델별 pointwise 구간이며 Holm 동시 신뢰구간이 아니다.

## 주 결과: 직접 계산

22개 모델 모두 Female 선택 비율이 50%보다 높았고 Holm 보정 후 p<0.05였다. 비율 범위는 53.290%–61.782%, 보정 p 최댓값은 약 0.001872였다. 아래 모델명은 원본 식별자를 유지한다. 표의 순서는 순위가 아니다.

| 모델 | Female 선택 % | 95% CI (%) | Holm p |
|---|---:|---:|---:|
| `Qwen/Qwen2-VL-72B-Instruct` | 53.372 | 51.292–55.452 | 0.00187159 |
| `claude-3-5-haiku-20241022` | 53.934 | 52.234–55.635 | 5.27969e-05 |
| `claude-3-5-sonnet-20241022` | 61.527 | 59.283–63.772 | 3.03882e-14 |
| `deepseek-ai/DeepSeek-R1` | 58.727 | 57.121–60.332 | 3.28643e-15 |
| `deepseek-ai/DeepSeek-V3` | 61.782 | 59.541–64.022 | 1.18165e-14 |
| `gemini-1.5-flash` | 58.345 | 56.778–59.913 | 7.29107e-15 |
| `gemini-1.5-pro` | 59.668 | 57.865–61.471 | 5.66723e-15 |
| `gemini-2.0-flash` | 55.532 | 53.838–57.225 | 6.0257e-08 |
| `gemini-2.0-flash-thinking-exp-01-21` | 53.669 | 52.003–55.335 | 7.87714e-05 |
| `google/gemma-2-27b-it` | 57.974 | 56.205–59.743 | 4.60735e-12 |
| `google/gemma-2-9b-it` | 54.714 | 52.889–56.540 | 9.33252e-06 |
| `gpt-3.5-turbo` | 59.241 | 57.329–61.152 | 3.24706e-13 |
| `gpt-4o` | 55.651 | 54.027–57.275 | 1.34698e-08 |
| `gpt-4o-mini` | 55.365 | 53.910–56.819 | 2.9796e-09 |
| `grok-2-1212` | 56.662 | 55.072–58.252 | 5.25629e-11 |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 54.441 | 53.174–55.708 | 1.23585e-08 |
| `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo` | 58.321 | 56.658–59.985 | 8.6475e-14 |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` | 57.571 | 55.852–59.291 | 9.64642e-12 |
| `mistralai/Mistral-7B-Instruct-v0.3` | 57.317 | 55.089–59.546 | 6.0257e-08 |
| `mistralai/Mixtral-8x22B-Instruct-v0.1` | 56.014 | 54.546–57.483 | 1.07653e-10 |
| `o1-mini` | 57.439 | 55.753–59.126 | 9.64642e-12 |
| `o3-mini` | 53.290 | 52.073–54.507 | 4.55906e-06 |

## 민감도 분석

세 scope는 서로 다른 추정 대상이며, 각각 22개 검정에 별도로 Holm 보정했다. 민감도 결과로 주 분석을 대체하지 않았다.

| scope | 입력 pair 합계 | 모델당 추정 단위 | Holm p<0.05 |
|---|---:|---|---:|
| eligible_pairs (주) | 15,313 | 적격 pair | 22/22 |
| author_all | 15,399 | 전체 pair | 22/22 |
| equal_profession | 15,313 | 적격 pair를 평균한 직업 70개 | 22/22 |

전체 저자 label과 주 분석의 선택 비율 차이 절댓값은 모델별 최대 0.403319 percentage points였다. 직업 동일 가중과 주 분석의 차이는 최대 0.125541 percentage points였다.

선택값 일관성을 통과한 30,690행만 남긴 표본도 별도 기술통계로 저장했다. 이 표본은 pair 균형이 깨지므로 CI·p-value를 계산하지 않았다. 108개 문제 행과 pair 제외에 따른 172행은 다른 분모다.

## 해석 한계와 Assumption

- 직업 clustering은 직업 간 독립성 등을 가정한다. 공유 이름·prompt 자산에서 생기는 모든 의존성을 제거하지 않는다. 이 실험의 직업 집합을 넘어서는 일반화는 추가 가정이 필요하다.
- 결과는 저자가 저장한 선택값에 근거한다. first-name/성별 일관성 검사는 원응답 해석의 정확성을 보장하지 않는다. 비표준 선택값을 임의로 재분류하거나 결측을 대체하지 않았다.
- 제외 여부가 응답 특성과 연관되면 선택 편향이 남는다. 두 민감도에서 같은 유의성 판정이 나와도 모든 편향에 강건하다는 뜻은 아니다.
- 이름 교환 외에 모든 현실적 채용 조건을 통제한 결과가 아니다. 50% 대비 유의성은 실제 차별의 확정 증거나 보편적 Fairness Score가 아니다.
- 모델별 표본이 다르며 모델 간 차이에 대한 직접 검정은 수행하지 않았다. 현재 서비스 모델의 성능으로 해석하지 않는다.
- 최종 출판본 접근 제한으로 figure별 dataset 대응은 미확정이다. 논문의 주장과 이번 계산을 동일시하지 않는다. PNAS와 metric을 통합하지 않는다.

## 산출물과 검증

- [추정치 66개](../results/rozado_2026/name/inference/estimates.csv): scope·표본수·SE·CI·raw/Holm p·family ID.
- `pair_outcomes.csv.gz` (행 단위 로컬 산출물; 공개 저장소 제외): 전체 15,399개 pair와 두 원본 observation locator, 적격 flag.
- [행 단위 기술통계](../results/rozado_2026/name/inference/consistent_rows_descriptive.csv).
- [실행 receipt](../results/rozado_2026/name/inference/run.json): 입력·명세·코드·출력 SHA-256, 라이브러리 버전, 모델별 DOI→archive→member provenance. pair locator는 정제 pair 표와 대조한다.
- 발표용 [SVG](../figures/rozado_2026/name/inference/primary_estimates.svg) / [SVG](../figures/rozado_2026/name/inference/primary_estimates.svg): script 자동 생성, 시각 확인 완료.

합성 데이터에서 CR1을 독립 cluster-score 계산식과 비교하고 직업 동일 가중 SE를 SD/√G 및 일표본 t 검정과 대조했다. 저장된 66개 추정치·CI·p-value를 pair 결과에서 독립 재계산하고, Holm 누적 최대 보정·EDA 평균·전체 pair locator·hash를 검증했다. PNAS 동결 파일 65개도 불변 검증했다.

```bash
.venv/bin/python tests/check_rozado_inference.py
.venv/bin/python src/analysis/infer_rozado_name.py
.venv/bin/python tests/check_rozado_inference_outputs.py
.venv/bin/python tests/check_pnas_freeze.py
```

다음 단계: `experiment_order_effects`와 두 masking 실험의 name 입력 대응을 원값으로 검증하고, 독립 실험/파생 결과 구분 및 위치·A/B·성별 변수의 정제 명세를 작성한다. 대응이 확인되기 전 단순 행 번호 join이나 추가 추론은 하지 않는다.
