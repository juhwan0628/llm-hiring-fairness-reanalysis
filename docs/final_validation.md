# 최종 검증 기록

실행일: 2026-09-14. PNAS 분석을 재실행하지 않고 동결 hash를 확인했다. 신규 검증 범위는 Rozado order/masking과 발표용 그림이다.

## 통과한 검증

| 명령 (`.venv/bin/python` 뒤) | 실제 확인 내용 |
|---|---|
| `tests/check_rozado_order_masking.py` | 실제 masked prompt의 두 매핑 구분, A와 첫 슬롯 분리, input identity, 비표준 label·gender mismatch 거부 |
| `src/clean/clean_rozado_order_masking.py` | 세 조건 각각 30,798행의 유일 input join, pair 내 매핑·슬롯 확인, projection 전수 저장/재읽기 일치, source member 및 raw archive hash |
| `tests/check_rozado_order_masking_stats.py` | 직접 CR1 식과 statsmodels 비교, signed paired change, 0분산·cluster 부족, 추정 불가를 포함한 계획 family Holm 처리 |
| `tests/check_rozado_order_masking_outputs.py` | 92,394개 source locator, 46,197개 pair, 176개 추정·CI·p의 독립 OLS/CR1 계산, 132/44 Holm, 대응 표본 membership |
| `tests/check_rozado_inference_outputs.py` | 이전 name 66개 추정치·3개 Holm family·EDA 평균·provenance 불변 |
| `tests/check_pnas_freeze.py` | PNAS 동결 65개 파일 SHA-256 불변 |
| `tests/check_final_figures.py` | 그림 7종×3 export, 원 추정치/출력 hash, 모델 식별자 대응, PNG/SVG/PDF 형식 |

mapping 검사는 구현 전 missing-module 실패를 먼저 확인한 뒤 구현 후 통과했다. 통계 함수는 서로 다른 cluster 크기와 음수 변화량을 포함한 합성 입력으로 검증했다. 176개 실제 추정은 모두 직업 70개·자유도 69였으며 추정 불가 사례는 없었다.

## 저장 결과와 재실행

- name/order 15,313, fixed 15,390, counterbalanced 15,394개 적격 pair.
- name과 공통 masking pair는 fixed 15,310, counterbalanced 15,311개.
- 정제 및 통계 산출물은 별도 디렉터리에 있다. 원래 문자열·비표준 선택을 임의 교정하지 않았다.
- order/masking 추론과 최종 그림 script를 두 번째 실행했다. 결과 4개 및 그림·목록·표시명 대응 23개, 총 27개 산출물의 SHA-256이 첫 실행과 동일했다.
- 최종 문서의 로컬 링크와 신규 Python 문법 검사, `git diff --check`도 통과했다.

## 시각·문서 검토

7개 PNG를 직접 열어 제목·모델명·축 단위·CI·레이아웃을 확인했다. SVG와 PDF는 export 형식 및 hash를 검증했다. score points, 선택 %, 변화 pp를 구분했다. CI는 pointwise이며 Holm 보정 후 유의성은 보고서의 p-value를 따르도록 표시했다.

PNAS 그림은 별도 `figures/final/`에서 저장된 추정치로 다시 그렸고 동결된 원 그림을 수정하지 않았다. 첫 후보 선택의 그래프 제목에는 내용과 위치를 분리하지 못한다는 한계를 명시했다. 50% 부근 masking 결과에 동등성·공정성 증명이라는 설명을 붙이지 않았다.

## 종료 snapshot

`src/analysis/close_analysis.py`는 raw/processed·코드·metadata·결과·그림·문서의 목록과 SHA-256을 기록한다. `--check`는 이후 내용 변경 및 목록 변경을 검출한다. interim 재추출물은 snapshot에 중복 포함하지 않으며, 원 archive와 source-member metadata를 통해 추적한다.

```bash
.venv/bin/python src/analysis/close_analysis.py --check
```

이 검증은 저자 파서의 의미 정확성, 실제 채용 인과효과, 논문 전체의 완전 재현을 보장하지 않는다. 미확정 사항은 최종보고서에 유지한다.
