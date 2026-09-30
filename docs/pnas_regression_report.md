# PNAS Figure 1·5 회귀 재현 결과

작성일: 2026-09-13. 공개 replication 관측 표를 이용한 Python 재분석. Stata 자체 실행 결과와의 직접 대조는 아니다.

## 재현 범위와 결과

5개 모델 × minority/additive/intersection = 15개 회귀를 실행하고, 주요 설명변수 계수 30개를 저자 `Code.do`의 Figure 1·5 숫자 annotation과 대조했다. 계수 30/30, 95% CI 하한 29/30, 상한 30/30이 사전에 정한 `0.00005 + 1e-8` 기준 안에서 일치했다.

비교 대상은 저자 코드에 적힌 annotation이다. 논문 PDF의 숫자 또는 원 저자의 Stata 실행 결과를 직접 검증했다고 표시하지 않는다. 원 저자 SE·N은 이 annotation에 없으므로 추정해 채우지 않았다.

## 실제 회귀 표본

| 모델 | 공개 표 행 수 | 점수 결측 | singleton 제외 | 회귀 N | cluster | t 자유도 |
|---|---:|---:|---:|---:|---:|---:|
| GPT-3.5 Turbo | 332,895 | 1 | 8 | 332,886 | 100 | 99 |
| Gemini 1.5 Flash | 332,257 | 9,430 | 8 | 322,819 | 99 | 98 |
| Llama 3-70B | 332,257 | 1,811 | 8 | 330,438 | 100 | 99 |
| GPT-4o | 332,257 | 12,771 | 8 | 319,478 | 100 | 99 |
| Claude 3.5 Sonnet | 332,257 | 14,105 | 7 | 318,145 | 100 | 99 |

각 모델 내부의 세 specification은 같은 행 집합을 사용한다. Gemini의 실제 cluster 수는 99개다. 모든 모델에 100개 또는 자유도 99를 일괄 적용하지 않았다. 공변량 결측은 없었고, 모든 실행에서 absorbed df는 1,662다. 설명변수 rank는 minority 14, additive 15, intersection 16이다. 실제 표본에서는 nested 고정효과나 rank deficiency가 검출되지 않았다.

원본 중복은 유지했고 추가 trimming은 적용하지 않았다. 날짜는 Stata의 원래 숫자를 사용했다. 연속 통제변수만 수치 안정성을 위해 중심화·표준화했으며, 보고 대상 집단 지표와 점수 단위는 유지했다.

## 직접 계산한 교차집단 대비

기준집단은 White male. 값은 0–100 점수 척도의 조정된 차이이며 퍼센트가 아니다. 아래 CI는 pointwise 95% cluster CI다.

| 모델 | Black female | White female | Black male |
|---|---|---|---|
| GPT-3.5 Turbo | 0.3786 [0.2784, 0.4789] | 0.2227 [0.1062, 0.3392] | -0.3032 [-0.4323, -0.1741] |
| Gemini 1.5 Flash | 0.9560 [0.8284, 1.0836] | 0.8271 [0.6649, 0.9894] | -0.2517 [-0.4124, -0.0909] |
| Llama 3-70B | 0.8972 [0.6967, 1.0977] | 0.4965 [0.2739, 0.7191] | -0.1043 [-0.2728, 0.0641] |
| GPT-4o | 0.4139 [0.2663, 0.5614] | 0.2868 [0.1253, 0.4484] | -0.5907 [-0.7478, -0.4335] |
| Claude 3.5 Sonnet | 0.7098 [0.5366, 0.8831] | 0.8983 [0.7233, 1.0733] | -0.6114 [-0.7353, -0.4875] |

본 과제에서 정한 15개 intersection 대비의 Holm family에서 14개는 보정 p<0.05다. Llama의 Black male 대비는 p_Holm≈0.222다. 이는 그 대비가 0이라는 증명이 아니다. 나머지 specification의 p-value는 재현 확인용 미보정 값이며 같은 family에 섞지 않았다.

모델마다 유효 표본이 다르다. 이 표로 모델 간 격차의 차이를 직접 검정하거나 공정성 순위를 매기지 않는다. 높은 평균 점수, 유의한 대비, 실제 채용 차별은 서로 다른 주장이다. 위 교차집단 점추정치의 절댓값은 모두 1점 미만이므로 통계적 유의성과 실제 의사결정에서의 중요성을 별도로 논의해야 한다.

## 불일치 1건과 한계

- Llama White female 대비의 CI 하한: computed `0.27394996004246858`, author annotation `0.2740`.
- 차이: `−0.000050039957531444745`. 사전 허용오차 `0.00005001`을 약 `2.996e-8` 초과한다.
- 반올림 경계에 매우 가깝지만 자동으로 일치 처리하지 않았다. 원 저자의 실행 정밀도·버전·annotation 생성 이력이 없어 원인을 확정할 수 없다. 숫자나 허용오차를 조정하지 않는다.
- 3개 이상 고정효과의 pairwise absorbed df는 일반적으로 근사다. 원 저자의 reghdfe 버전을 복원하거나 Stata에서 직접 재실행한 검증은 미수행이다.
- 공개 표 생성 이전 탈락·trimming 이력, 결측 발생 이유, 정확한 모델 snapshot은 여전히 미확정이다.

## 산출물과 재실행

```bash
.venv/bin/python tests/check_pnas_regression_backend.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python src/analysis/regress_pnas.py
.venv/bin/python tests/check_pnas_regression_outputs.py
```

- `results/pnas_2025/analysis/coefficients.csv`: computed 계수·SE·CI·p_raw·p_holm 및 출처.
- `author_annotations.csv`: 저자 코드 숫자와 각 숫자의 원본 line·SHA-256.
- `reported_computed.csv`: reported/computed 비교 및 차이·엄격한 반올림 판정.
- `score_*_sample.csv.gz`: 원파일의 1-based 행 번호와 included/missing_outcome/singleton 상태. 해당 원파일 hash는 run의 각 regression에 연결된다. 지원자 고유 ID로 해석하지 않는다.
- `run.json`: 15개 실행의 표본·rank·df·보정계수, 입력·코드·출력 hash, Git HEAD/dirty 상태, 패키지 버전. 현재 스크립트는 커밋 이후 작성되어 dirty 상태와 코드 hash로 구분된다.
- `figures/pnas_2025/analysis/intersection_coefficients.png` 및 `.svg`: 발표 재사용용 자동 생성 그림.

합성 dummy 비교, 보정 SE·CI·p 검증, 입력/출력/code hash, 15개 회귀·30개 대비·검정 family·행 membership 검증을 통과했다. raw 7개는 공식 SHA-256과 일치했다. PNG 그림도 직접 확인했다. 전체 회귀의 두 번째 완전 재실행은 아직 하지 않았다.

다음 작업은 위 미세 불일치의 원자료 정밀도·저자 실행 정보 확인과 4모델 공통 유효 표본 비교다. 후자는 명세 v1의 별도 18검정 family를 유지한다. Rozado 자료 수집은 독립 과제로 남아 있다.
