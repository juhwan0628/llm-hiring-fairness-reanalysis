# 발표용 그래프

같은 번호의 PNG(220 dpi), SVG, PDF를 제공한다. SVG/PDF는 벡터 형식이다. 원본 PNAS 그래프는 변경하지 않았다.

모델 순서는 원 식별자 기준이며 성능 순위가 아니다. [표시명 대응표](model_labels.csv)는 원 모델명을 보존한다. 모든 CI는 pointwise이며 Holm 동시 구간이 아니다.

재생성: `.venv/bin/python src/visualization/build_final_figures.py`

## 01_pnas_intersection: 교차집단 점수 격차

[SVG](01_pnas_intersection.svg) · [PDF](01_pnas_intersection.svg)

입력: [results/pnas_2025/analysis/coefficients.csv](../../results/pnas_2025/analysis/coefficients.csv)

0–100 척도의 점수 차이. 모델별 표본 상이. 15검정 Holm 중 14개 유의. CI는 동시 구간이 아님.

## 02_rozado_name: 이름 조건의 Female 선택 비율

[SVG](02_rozado_name.svg) · [PDF](02_rozado_name.svg)

입력: [results/rozado_2026/name/inference/estimates.csv](../../results/rozado_2026/name/inference/estimates.csv)

15,313 pair. 22/22 Holm 유의. 실험 내 50% 대비이며 실제 채용 차별 판정 아님.

## 03_rozado_position: 첫 번째 제시 후보 선택

[SVG](03_rozado_position.svg) · [PDF](03_rozado_position.svg)

입력: [results/rozado_2026/order_masking/estimates.csv](../../results/rozado_2026/order_masking/estimates.csv)

CV 내용을 순서 교환하지 않은 자료. 순서의 인과효과로 해석 금지. 조건별 표본 상이.

## 04_rozado_labels: A/B label 진단

[SVG](04_rozado_labels.svg) · [PDF](04_rozado_labels.svg)

입력: [results/rozado_2026/order_masking/estimates.csv](../../results/rozado_2026/order_masking/estimates.csv)

A는 첫 번째 후보와 다름. fixed에서 A와 원래 남성이 동일하므로 성별 단독 효과 해석 금지.

## 05_rozado_masking_changes: 동일 pair의 masking 전후 변화

[SVG](05_rozado_masking_changes.svg) · [PDF](05_rozado_masking_changes.svg)

입력: [results/rozado_2026/order_masking/estimates.csv](../../results/rozado_2026/order_masking/estimates.csv)

같은 pair 내 원래 Female 선택 비율 차이. pp 단위. 별도 생성 시점·파서·proxy 단서의 한계가 있어 공정성 개선 인과효과 아님.

## 06_rozado_masked_assignment: counterbalanced 원래 성별 역매핑

[SVG](06_rozado_masked_assignment.svg) · [PDF](06_rozado_masked_assignment.svg)

입력: [results/rozado_2026/order_masking/estimates.csv](../../results/rozado_2026/order_masking/estimates.csv)

실제 표시 성별이 아닌 원래 할당값. 유의하지 않음은 동등성이나 공정성 증명 아님.

## A1_pnas_model_contrasts: 부록: PNAS 공통 표본 모델 비교

[SVG](A1_pnas_model_contrasts.svg) · [PDF](A1_pnas_model_contrasts.svg)

입력: [results/pnas_2025/common_sample/paired_contrasts.csv](../../results/pnas_2025/common_sample/paired_contrasts.csv)

18개 중 12개 Holm 유의. signed gap의 차이이며 절대 편향 순위 아님.
