# PNAS 4모델 공통 표본 비교

업데이트: 2026-09-14. 통계 명세 v1 §2.C에 따른 secondary analysis다. 저자 논문의 별도 보고값을 옮긴 결과가 아니다.

## 분석 표본과 방법

- 공개 4모델 표: 332,257행. 하나 이상의 점수가 결측인 36,578행 제외 → 공통 유효 295,679행 → singleton 7행 제외 → 최종 295,672행.
- 모든 4개 단일모델 회귀와 6개 쌍 차이 회귀에 동일한 행·설명변수를 사용했다. 직업×주 cluster는 99개, t 자유도는 98, absorbed df는 1,662, 설명변수 rank는 16이다.
- 원 명세의 공변량·고정효과·비가중 회귀를 유지했다. 결측을 보간하거나 중복을 삭제하지 않았다. GPT-3.5는 다른 파일에 있어 포함하지 않았다.
- 쌍 회귀의 종속변수는 같은 공개 행의 `score_A − score_B`다. 추정량은 `(집단 − White male)_A − (집단 − White male)_B`. 모델별 SE를 독립이라고 가정해 합산하지 않는다.
- 6쌍 × 3집단 = 18개 검정을 별도 Holm family로 보정했다. 이전 5모델 15개 대비 family와 합치지 않았다. 4개 단일모델의 12개 계수는 계산 대조용이며 새로운 주요 유의성 family로 해석하지 않는다.

## 직접 계산한 결과

18개 중 12개가 Holm 보정 후 p<0.05다. 부호는 A의 **signed gap**에서 B의 signed gap을 뺀 방향이다. 절대 편향 크기의 차이나 공정성 점수가 아니다. 아래 95% CI는 pointwise이며 Holm 동시 신뢰구간이 아니다.

| A − B | 집단 (기준 White male) | 격차 차이 | 95% CI | p_Holm |
|---|---|---:|---|---:|
| GPT-4o − Gemini 1.5 Flash | Black female | -0.5393 | [-0.6987, -0.3799] | 2.106e-08 |
| GPT-4o − Gemini 1.5 Flash | White female | -0.5506 | [-0.7107, -0.3905] | 1.328e-08 |
| GPT-4o − Gemini 1.5 Flash | Black male | -0.3462 | [-0.5118, -0.1806] | 0.0007133 |
| GPT-4o − Claude 3.5 Sonnet | Black female | -0.2769 | [-0.4494, -0.1044] | 0.0155 |
| GPT-4o − Claude 3.5 Sonnet | White female | -0.6053 | [-0.7883, -0.4224] | 3.973e-08 |
| GPT-4o − Claude 3.5 Sonnet | Black male | 0.0131 | [-0.1296, 0.1558] | 1 |
| GPT-4o − Llama 3-70B | Black female | -0.4748 | [-0.6595, -0.2900] | 2.156e-05 |
| GPT-4o − Llama 3-70B | White female | -0.1926 | [-0.4092, 0.0240] | 0.4037 |
| GPT-4o − Llama 3-70B | Black male | -0.4647 | [-0.6362, -0.2932] | 7.216e-06 |
| Gemini 1.5 Flash − Claude 3.5 Sonnet | Black female | 0.2624 | [0.0865, 0.4383] | 0.02698 |
| Gemini 1.5 Flash − Claude 3.5 Sonnet | White female | -0.0547 | [-0.2191, 0.1097] | 1 |
| Gemini 1.5 Flash − Claude 3.5 Sonnet | Black male | 0.3592 | [0.2084, 0.5101] | 8.466e-05 |
| Gemini 1.5 Flash − Llama 3-70B | Black female | 0.0645 | [-0.1279, 0.2569] | 1 |
| Gemini 1.5 Flash − Llama 3-70B | White female | 0.3580 | [0.1837, 0.5323] | 0.0008419 |
| Gemini 1.5 Flash − Llama 3-70B | Black male | -0.1185 | [-0.3184, 0.0813] | 0.9685 |
| Claude 3.5 Sonnet − Llama 3-70B | Black female | -0.1979 | [-0.3571, -0.0387] | 0.09234 |
| Claude 3.5 Sonnet − Llama 3-70B | White female | 0.4127 | [0.2490, 0.5765] | 2.977e-05 |
| Claude 3.5 Sonnet − Llama 3-70B | Black male | -0.4778 | [-0.6458, -0.3098] | 2.429e-06 |

예를 들어 GPT-4o − Gemini의 Black female 대비는 −0.5393점이다. 이는 같은 행 표본에서 Black female 대 White male의 조정된 점수 격차가 GPT-4o에서 Gemini보다 0.5393점 작다는 뜻이다. GPT-4o 전체가 더 공정하다는 결론은 아니다.

Claude − Llama의 Black female 대비는 pointwise CI가 0을 포함하지 않지만 p_Holm≈0.0923이다. 그래프의 CI만 보고 다중검정 후 유의하다고 판단하면 안 된다. 유의하지 않은 결과도 두 모델이 동등함을 증명하지 않는다.

공통 표본은 비교 행을 맞추지만 결측에 의한 선택 편향을 제거하지 않는다. 이 결과를 원실험 전체나 실제 채용시장으로 일반화하지 않는다. 행 내 대응을 활용했을 뿐 원래 지원자 ID를 복원한 것이 아니다.

## 이전 CI 불일치 조사

- 저자 `ReadMe.txt` 7행은 Stata/MP 16.0을 명시한다. 이전 중간보고에서 Stata 버전 전체를 미확정으로 표현한 부분을 정정했다. 미확정은 reghdfe 버전, 실제 실행 로그 및 정밀도 설정이다.
- 저자 코드에는 `generate cilb = .`가 있고, 하한 annotation `0.2740`은 `Code.do` 1003행에 직접 적혀 있다. 프로그램 내부 `version` 명령은 발견되지 않았다. 그 부재가 사용한 Stata 버전이 미상이라는 뜻은 아니다.
- 계산 하한 `0.27394996004246858`을 float32로 바꾸면 `0.2739499509334564`다. 둘 다 Python 소수 4자리 표시에서 `0.2739`이므로 단순한 float32 저장 변환만으로는 annotation을 설명하지 못한다.
- Stata 자체 실행·solver tolerance 민감도 재실행은 하지 않았다. 원인 미확정 상태와 기존 불일치 판정을 유지한다. 허용오차를 넓히거나 원 수치를 수정하지 않는다.
- 이번 공통 표본 회귀는 검증된 Python 구현을 이용한 별도 분석이며, 이 미세 불일치를 해결한 Stata 완전 재현이라고 주장하지 않는다.

## 산출물과 재실행

```bash
.venv/bin/python tests/check_pnas_pairs.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python src/analysis/compare_pnas_models.py
.venv/bin/python tests/check_pnas_common_outputs.py
```

- `results/pnas_2025/common_sample/paired_contrasts.csv`: 18개 paired 대비, SE·CI·p_raw·p_holm 및 출처.
- `individual_common_coefficients.csv`: 공통 표본의 모델별 교차집단 계수 12개. 쌍 회귀 계수가 두 단일모델 계수 차이와 일치하는지 대조한다.
- `sample.csv.gz`: 원본 1-based 행 번호와 포함·제외 상태. source file/hash는 run 및 각 추정 결과에 연결된다.
- `precision_audit.json`: 이전 비교표·저자 코드·ReadMe의 hash와 line, CI float32 변환 결과, 미확정 상태.
- `run.json`: 표본·rank·보정계수·설정·패키지·Git 상태·코드/입력/출력 hash.
- `figures/pnas_2025/common_sample/paired_gap_differences.png` 및 `.svg`: script 자동 생성 그림.

합성 데이터에서 6개 쌍 모두 명시적 dummy 회귀와 계수·보정 SE가 일치했다. 공통 오차가 있는 데이터로 모델 간 공분산을 보존하는지 검증했다. 원파일·코드·결과 hash, 행 membership, 18검정 family와 쌍의 부호 검증을 통과했다. ReadMe 출처 보강 후 전체 공통 표본 분석을 재실행했고, 결과표 2개·표본 목록 1개·그림 2개의 SHA-256이 첫 실행과 동일했다. precision audit과 실행 receipt는 출처·코드 변경을 반영했다. 기존 Figure 1·5 결과의 무결성 검사도 통과했다.

다음 우선 작업은 Rozado/Zenodo 접근 재확인, 파일 목록·버전·라이선스 및 소형 코드 확보다. PNAS threshold 분석 등 확장은 핵심 두 연구의 데이터 확보 이후로 둔다.
