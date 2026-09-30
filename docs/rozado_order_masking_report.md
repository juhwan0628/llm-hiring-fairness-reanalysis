# Rozado order/masking 분석 결과

작성: 2026-09-14. Zenodo v4 17173798의 공개 원자료에서 직접 계산했다. [분석 명세](rozado_order_masking_spec.md)는 name 결과를 확인한 뒤 이번 추정 전에 고정했다. 사전등록이 아니다.

## 입력 대응과 파생 자료의 의미

세 조건 각각 30,798행이 name 입력 9개 필드와 유일하게 연결됐다. 두 masking 조건은 저장 prompt 전체가 명시적 A/B 치환 결과와 일치했다. 임의의 fuzzy join이나 행 번호 기반 join은 사용하지 않았다.

- order는 name 응답을 재분류한 자료다. 첫 후보 이름과 저자 True/False 파생값은 30,798행 모두 재계산과 일치했다. 새로운 독립 모델 응답 30,798개로 세지 않는다.
- fixed masking: 모든 행이 원래 Male→A, Female→B다.
- counterbalanced masking: 원래 Male→A 15,400행, Male→B 15,398행. 각 name pair 안에서는 매핑이 동일하고 A가 놓인 제시 슬롯이 두 행에서 바뀜을 검증했다. 적격 pair에서는 두 매핑이 7,698개/7,696개다.
- 세 파생 파일군에 각각 6개씩, name의 문자열 `None`이 빈 문자열로 바뀐 복사 차이가 있었다. 원본 name 값과 파생 값을 별도로 보존했다. 나머지 원래 필드는 일치했다.

저자 code archive의 `estimate order effects.ipynb` cell 1, `choose best candidate - gender masked fixed.ipynb` cell 1, `choose best candidate - gender truly masked.ipynb` cell 1을 정적으로 읽었다. 코드의 행 인덱스 기반 배정을 그대로 신뢰하지 않고 실제 prompt와 기존 내용 기반 pair로 확인했다. 코드·CSV의 archive/member SHA는 [structure metadata](../data/metadata/rozado_2026/structure.json)에 보존돼 있다. 저자 코드는 실행하지 않았다.

## 표본

| 조건 | 전체 행 | 유효하지 않은 행 | 전체 pair | 해당 조건 적격 pair | name과 공통 적격 pair |
|---|---:|---:|---:|---:|---:|
| name/order | 30,798 | 108 | 15,399 | 15,313 | 15,313 |
| fixed | 30,798 | 10 | 15,399 | 15,390 | 15,310 |
| counterbalanced | 30,798 | 6 | 15,399 | 15,394 | 15,311 |

masked 선택값은 정확히 `Candidate A`/`Candidate B`여야 하고, 저장 gender가 실제 prompt 매핑과 일치해야 한다. 이번 masked 제외는 모두 비표준 또는 미선택 label이다. `Neither`, `Candidate 1`, `候选人B`, 문자열 `None` 등을 임의로 A/B로 바꾸지 않았다. 유효하지 않은 행도 compact 정제 표에 남겼고 긴 원문은 원파일 locator로 연결했다.

masking 단독 지표는 name 선택 오류만으로 제외하지 않는다. 반면 masking−name 차이는 두 조건 모두 유효한 동일 pair만 사용한다. 모델별 표본이 다르며 전체 합계는 서로 다른 모델을 합친 표본 관리용 숫자다.

## 추정 결과

pair 두 행의 평균을 모델별 추정했다. 모든 실행에서 직업 70개 cluster, CR1 표준오차, t(69) 양측 검정을 사용했다. 진단 6종×22모델은 하나의 Holm family 132개, 대응 변화 2종×22모델은 별도 family 44개다. 평균 선택률의 기준은 0.5, 변화량 기준은 0이다. 추정 불가 결과는 없었다.

| 조건 | 지표 | 모델별 추정 범위 | Holm p<0.05 | family |
|---|---|---:|---:|---|
| fixed masking | masking − name Female 선택 | -16.138–-3.818 pp | 22/22 | 44 |
| fixed masking | Candidate A 선택 | 47.214–59.084 % | 13/22 | 132 |
| fixed masking | 첫 번째 후보 선택 | 43.544–88.286 % | 17/22 | 132 |
| counterbalanced masking | masking − name Female 선택 | -12.141–-2.003 pp | 21/22 | 44 |
| counterbalanced masking | Candidate A 선택 | 46.643–58.727 % | 12/22 | 132 |
| counterbalanced masking | 첫 번째 후보 선택 | 43.123–88.286 % | 17/22 | 132 |
| counterbalanced masking | 원래 Female 할당 선택 | 49.214–51.857 % | 0/22 | 132 |
| name/order | 첫 번째 후보 선택 | 41.223–81.377 % | 18/22 | 132 |

counterbalanced의 원래 Female 선택 비율은 49.214%–51.857%이며 Holm p 최솟값은 약 0.5051이다. 이는 해당 50% 검정에서 차이를 검출하지 못했다는 뜻이다. 실질적 동등성이나 편향 부재를 검증한 결과가 아니다.

공통 pair의 counterbalanced−name 차이는 22모델 모두 음수지만 21개만 44검정 Holm 보정 후 유의했다. `o3-mini`는 −2.003 pp, pointwise 95% CI [−4.119, 0.114] pp, p_Holm≈0.06326이다. fixed의 변화는 22/22 유의했다. fixed의 음수 변화는 A/B label과 원래 gender가 고정 대응하는 조건이라, 그 자체로 편향 감소·개선이라고 부르지 않는다.

진단 132개 중 77개, 대응 변화 44개 중 43개가 보정 p<0.05다. 이 개수는 공정성 점수 또는 서로 다른 metric의 통합 효과가 아니다. 전체 176개 결과를 공개하며 유리한 모델만 선택하지 않았다.

## 해석 한계

1. **첫 후보 선택과 순서의 인과효과는 다르다.** 기존 pair는 이름 할당을 교환했으나 CV1/CV2 내용 순서는 그대로다. 내용 품질과 위치를 분리할 수 없다.
2. **A/B label과 성별 역매핑은 다르다.** fixed는 원래 남성=A다. counterbalanced의 `chosen_gender_masked`는 실제 prompt에 드러난 gender가 아닌 원래 할당이다.
3. **마스킹은 완전 익명화를 보장하지 않는다.** 폴더명 `truly_masked`를 성별 단서 완전 제거의 증거로 쓰지 않는다. CV의 proxy와 다른 이름 흔적까지 전수 의미 검증한 것은 아니다.
4. **전후 차이가 곧 인과효과는 아니다.** 같은 입력을 대응시켰지만 별도 생성 시점·모델 상태·파서 영향을 통제하지 못한다.
5. **표준오차와 누락의 가정이 남는다.** 직업 간 독립성, 공유 자산, 파싱 정확성, 선택값 오류에 따른 제외가 해석을 제한한다. 결측 보간·추정은 하지 않았다.
6. 최종 논문 figure별 수치 대응은 접근 제한으로 미확정이다. 이번 결과는 우리 secondary analysis이며 저자 결과 완전 복제라고 표시하지 않는다.

## 산출물·재실행

- [정제·연결 receipt](../data/metadata/rozado_2026/order_masking_cleaning_report.json): 입력 identity, 복사 차이, 원 archive/member, 정제 결과 hash.
- `data/processed/rozado_2026/order_masking/observations.csv.gz`: 92,394행 compact projection. 정제 결과이며 분석 추정치는 포함하지 않는다.
- [추정치](../results/rozado_2026/order_masking/estimates.csv), [coverage](../results/rozado_2026/order_masking/coverage.csv), `pair_outcomes.csv.gz` (행 단위 로컬 산출물; 공개 저장소 제외), `matched_pair_changes.csv.gz` (행 단위 로컬 산출물; 공개 저장소 제외), [분석 receipt](../results/rozado_2026/order_masking/run.json).
- [발표용 그림 목록](../figures/final/README.md)의 03–06에 결과를 정리했다.

```bash
.venv/bin/python tests/check_rozado_order_masking.py
.venv/bin/python src/clean/clean_rozado_order_masking.py
.venv/bin/python tests/check_rozado_order_masking_stats.py
.venv/bin/python src/analysis/infer_rozado_order_masking.py
.venv/bin/python tests/check_rozado_order_masking_outputs.py
.venv/bin/python src/visualization/build_final_figures.py
```

완료 범위는 name/order/두 masking 조건이다. name_gender·pronouns·CV score는 구조 확인 상태로 분석을 종료한다. PNAS 동결은 유지한다.
