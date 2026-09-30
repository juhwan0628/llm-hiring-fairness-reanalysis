# 생성형 AI 기반 채용은 공정한가? — 공개 원자료 재분석 최종보고서

분석 종료일: 2026-09-14. 범위: PNAS 핵심 회귀·공통 표본 비교, Rozado name/order/두 masking 조건. PNAS는 `66a9e46` 동결을 유지했다. 공개 데이터의 secondary analysis이며 신규 LLM 실험을 수행하지 않았다.

## 핵심 결론

**평가 결과의 집단별 차이, 이름 선택의 차이, A/B label 선택, 제시 위치의 차이는 따로 측정해야 한다.** 두 연구의 공개 자료에서 여러 차이를 확인했지만, 하나의 Fairness Score나 “가장 공정한 모델” 순위로 통합하지 않았다.

PNAS에서는 White male 대비 교차집단의 조정된 점수 격차가 모델별로 달랐다. Rozado에서는 이름 조건의 Female 선택 비율이 22모델 모두 50%를 웃돌았다. Counterbalanced masking의 원래 Female 할당 선택은 50% 근처로 모였지만 A/B label 및 첫 후보 선택의 비대칭은 남았다. 따라서 성별 역매핑 지표 하나의 변화로 채용 시스템 전체의 공정성이 확보됐다고 결론 내릴 수 없다.

## 1. 연구 질문과 자료

1. 같은 연구 안에서 어떤 집단·조건의 평가 격차가 관측되는가?
2. 모델 간 비교는 동일 표본을 사용할 때도 유지되는가?
3. 이름을 가리고 label을 교차 배정하면 선택 비율은 어떻게 달라지는가?
4. 자료 구조·파싱·추론 가정은 어디까지 결론을 허용하는가?

| 연구 | 고정 자료 | 분석 단위·metric | 완료 범위 |
|---|---|---|---|
| An et al. (2025), PNAS Nexus | OSF replication 7개 파일 | 0–100 평가 점수의 조정된 차이 | 5모델 회귀 및 4모델 공통 표본 비교 |
| Rozado (2026), PeerJ Computer Science 12:e3628 | Zenodo v4 record 17173798, 2025-09-29 공개 | 이름 교환 pair 선택 비율; 대응 변화는 pp | name/order/fixed masking/counterbalanced masking |

Rozado의 초기 제안서 연도 2025와 출판본 연도 2026을 구분한다. 데이터 v4 공개 연도는 2025다. 기록된 snapshot과 모델 식별자를 사용하며 현재 서비스 버전으로 일반화하지 않는다. 출처는 [PNAS manifest](../data/metadata/source_manifest.json), [Rozado manifest](../data/metadata/rozado_2026/source_manifest.json), [출판 metadata](../data/metadata/rozado_crossref_20260913.json)에 보존했다.

## 2. 재현 가능한 분석 과정

원본 수집·hash 확인 → 구조 확인 → 원값 보존 정제 → 기술통계 → 명세 고정 → 통계 추정 → script 기반 그래프 → 독립 계산·provenance 검증 순서로 진행했다. EDA 이후 만든 명세는 사전등록이라고 부르지 않는다.

- raw는 수정하지 않는다. 추출물은 interim, 정제 표는 processed, 추정치는 results에 분리했다.
- provenance는 논문/데이터셋 → archive/member → 원파일 logical CSV record 또는 Stata 행 → pair/회귀 표본 → 결과까지 연결한다.
- missing 및 비표준 선택을 임의로 추정하거나 보간하지 않았다. 포함·제외 기준과 분모를 기록했다.
- 저자 notebook은 정적으로 읽었다. API 호출이나 파일 삭제를 포함한 저자 코드를 실행하지 않았다.
- 그림은 Python script에서 생성했다. pointwise CI와 Holm 보정 검정을 구분했다.

## 3. 직접 계산한 결과

### 3.1 PNAS: 교차집단 점수 격차

White male 대비 Black female·White female·Black male의 15개 대비 중 14개가 Holm 보정 후 p<0.05였다. Black female과 White female의 점추정치는 양수, Black male은 음수였다. Llama Black male 대비는 보정 p≈0.222로 유의하지 않았다. 교차집단 점추정치 절댓값은 모두 1점 미만이었다. 통계적 유의성과 실제 채용 결정에서의 중요성을 구분해야 한다.

모델별 유효 표본이 다르므로 위 결과만으로 모델 간 차이를 검정하지 않았다. 별도 4모델 공통 표본 295,672행에서 같은 행의 모델 점수 차이를 회귀한 18개 대비 중 12개가 Holm 보정 후 유의했다. 이 값은 **signed gap의 모델 간 차이**이며 절대 편향 크기나 공정성 순위가 아니다.

그림: [교차집단 격차](../figures/final/01_pnas_intersection.svg), [공통 표본 비교 부록](../figures/final/A1_pnas_model_contrasts.svg). 전체 수치·표본·방법은 [회귀 보고서](pnas_regression_report.md), [공통 표본 보고서](pnas_common_sample_report.md)에 있다.

### 3.2 Rozado name: 실험 내 이름 선택 차이

원본 30,798행을 내용에 근거해 15,399개 이름 교환 pair로 연결했다. 저자 선택 이름과 성별이 일관되지 않은 108행이 속한 86개 pair를 주 분석에서 제외했다. 원본·정제 표에는 모두 보존했다.

적격 15,313개 pair에서 모델별 Female 선택 비율은 **53.290%–61.782%**였다. 직업 70개 cluster CR1 및 t(69), 22검정 Holm 보정 후 모든 모델이 50%보다 높았다. 전체 저자 label 및 직업 동일 가중 민감도도 각각 22모델 모두 유의했으나, 파싱 정확성이나 표본 선택 문제가 완전히 해결됐다는 뜻은 아니다.

그림: [name 선택 비율](../figures/final/02_rozado_name.svg). 방법·전체 모델 값: [name 추론 보고서](rozado_name_inference_report.md).

### 3.3 Order/masking: 무엇을 가렸고 무엇이 남았는가

order는 기존 name 응답의 파생 label이다. masking은 별도 생성 응답이다. 두 종류를 독립 반복 실험으로 합산하지 않았다. 세 파생 조건의 모든 행을 name 입력과 정확히 연결했다.

fixed masking은 원래 Male=A, Female=B의 고정 대응이다. Counterbalanced masking은 실제 prompt에서 두 매핑을 확인했으며, 원래 Female 역매핑 지표를 A/B나 첫 번째 슬롯 선택과 구분했다.

| 진단 지표 | 모델별 선택 비율 범위 | Holm p<0.05 모델 수 |
|---|---:|---:|
| name/order: 첫 번째 후보 | 41.223%–81.377% | 18/22 |
| fixed: Candidate A | 47.214%–59.084% | 13/22 |
| fixed: 첫 번째 후보 | 43.544%–88.286% | 17/22 |
| counterbalanced: Candidate A | 46.643%–58.727% | 12/22 |
| counterbalanced: 첫 번째 후보 | 43.123%–88.286% | 17/22 |
| counterbalanced: 원래 Female 할당 | **49.214%–51.857%** | **0/22** |

위 여섯 지표는 **132개 검정의 단일 Holm family**다. 분모는 각 조건의 적격 pair로, fixed 15,390개·counterbalanced 15,394개다. 선택 비율을 합성 점수로 합치지 않았다.

name과 masking이 모두 유효한 공통 pair에서의 차이는 별도로 계산했다. Fixed−name은 −16.138∼−3.818 pp, counterbalanced−name은 −12.141∼−2.003 pp였다. 두 비교를 합친 44검정 Holm family에서 각각 22/22, 21/22가 유의했다. Counterbalanced의 `o3-mini`는 보정 p≈0.06326이었다.

**유의하지 않음은 동등성·공정성의 증명이 아니다.** 또한 첫 후보 선택 비율은 CV 내용 순서와 분리되지 않는다. 이 자료는 CV1/CV2를 뒤집어 위치만 바꾼 실험이 아니므로 순서의 인과효과라고 주장하지 않는다. Fixed의 역매핑 변화에는 A/B label 대응이 섞여 있어 이를 곧바로 편향 감소라고 부르지 않는다.

그림: [첫 후보](../figures/final/03_rozado_position.svg), [A/B label](../figures/final/04_rozado_labels.svg), [공통 pair 변화](../figures/final/05_rozado_masking_changes.svg), [counterbalanced 성별 역매핑](../figures/final/06_rozado_masked_assignment.svg). 상세: [order/masking 보고서](rozado_order_masking_report.md).

## 4. 저자의 보고와 우리의 계산을 구분

| 근거 종류 | 확인한 범위 | 하지 않은 주장 |
|---|---|---|
| 저자 코드 annotation | PNAS 계수 30/30, CI 끝점 59/60이 사전 허용오차 내 일치 | 저자 Stata 환경·논문 전체를 완전히 재현했다 |
| 우리 계산 | PNAS 공통 표본 회귀, Rozado pair 추론·masking 대응 비교 | 논문의 reported 값과 동일한 분석이다 |
| 공개 원자료·저자 코드 구조 | Rozado input identity, 실제 masked prompt, A/B 배정, 파생 order | 모든 파싱값이 원응답 의미를 정확히 반영한다 |
| 통계 가정 | cluster 추론 및 명시한 다중검정 family | 실제 채용시장 전체 또는 현재 모델의 공정성이 입증됐다 |

PNAS Llama White female CI 하한의 미세 불일치 1건은 그대로 남겼다. 허용오차를 넓히지 않았다. Rozado 최종 출판본 figure별 dataset 대응도 접근 제한으로 미확정이다. 이 한계가 있으므로 “두 논문 완전 재현”이라고 발표하지 않는다.

## 5. 결론의 한계

공개 표가 생성되기 전의 탈락 이력, 모델의 정확한 snapshot, 결측 발생 이유를 모두 복원하지 못했다. 이름 기반 gender/race 할당은 실험 설계의 범주이며 개인의 실제 정체성으로 해석하지 않는다. 성별을 가린 prompt에도 CV의 proxy 단서가 남을 수 있다.

직업 clustering은 공유 이름·prompt 자산의 모든 의존성을 해결하지 않는다. 파서 오류와 제외에 따른 선택 편향이 남을 수 있다. 동일 pair를 사용한 masking 비교도 별도 생성 시점이나 모델 상태를 무작위 통제한 인과 실험은 아니다.

이 연구는 집단별 점수/선택 차이의 재현 가능한 진단이다. 실제 선발 threshold, 지원자 풀의 분포, downstream hiring outcome은 분석하지 않았으므로 불이익의 실제 크기나 법적 판단을 제시하지 않는다.

## 6. 분석 종료와 인계

**완료:** PNAS 핵심 회귀·공통 표본 비교, Rozado name/order/두 masking, 입력 연결·정제·추론 검증, 최종 스토리라인, 발표용 그림 7종(각 PNG/SVG/PDF).

**범위 밖으로 종료:** name_gender, pronouns, CV scores 추가 분석; 신규 모델 호출; threshold 확장; 모델 간 공정성 순위; PNAS 미세 CI 불일치 해결; Rozado 최종 figure별 완전 재현. 미완료 범위를 완료로 표시하지 않는다.

[스토리라인](final_storyline.md), [그래프 목록·주의점](../figures/final/README.md), [실행 안내](../README.md)를 따라 발표 자료에 옮길 수 있다. 최종 snapshot은 `data/metadata/analysis_closure_20260914.json`에 raw/processed·코드·metadata·결과·그림·보고서의 SHA-256을 기록한다. Git commit/push를 대신하는 기록은 아니며, 새로운 분석으로 수정할 때는 별도 버전으로 다룬다.

```bash
.venv/bin/python src/analysis/close_analysis.py --check
```

재실행 검증의 상세 명령·결과는 [최종 검증 기록](final_validation.md)에 기록한다. 이후 작업은 결과를 변경하는 확장이 아니라 발표 편집·제출 형식 조정이다.
