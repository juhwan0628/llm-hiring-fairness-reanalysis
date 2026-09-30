# LLM 채용 평가 편향 공개 데이터 재분석

이 저장소는 **LLM 기반 채용 평가에서 나타나는 성별·이름·순서 관련 편향을 공개 데이터로 재분석한 종료 프로젝트**입니다.

분석은 **2026-09-14에 종료**했으며, PNAS 데이터 재분석과 Rozado 데이터의 name / order / masking 분석, 최종 보고서 및 발표용 시각화까지 완료했습니다.

이 공개 저장소에는 코드·문서·메타데이터·집계 결과·직접 생성한 시각화만 포함합니다. 원본/정제/중간 데이터와 행 단위 파생표는 제3자 자료의 재배포를 피하기 위해 포함하지 않습니다.


## 공개 저장소 범위

- 포함: 분석 코드, 테스트, provenance/출처 metadata, 집계 통계, 보고서, 발표 PDF, 직접 생성한 PNG/SVG 시각화
- 제외: 원본·정제·중간 데이터, 행 단위 파생표, 논문 PDF, 내부 에이전트 작업기록
- 제3자 데이터의 권리와 라이선스는 원 저자·배포처에 있으며, 이 저장소는 해당 자료를 재라이선스하지 않습니다.

자세한 내용은 [NOTICE.md](NOTICE.md)를 참고하세요.

## 주요 결과물

- [최종보고서](docs/final_report.md)
- [10분 발표 스토리라인](docs/final_storyline.md)
- [발표용 그래프 7종](figures/final/README.md)
- [최종 검증 기록](docs/final_validation.md)
- [연구 제안서](proposal.md)
- [실행 계획](execution_plan.md)
- [중간보고서](interim_report.md)
- [수집·구조 확인 보고서](collection_report.md)
- [출처 manifest](data/metadata/source_manifest.json)

세부 분석·검증 문서는 `docs/`에 정리되어 있습니다.

## 현재 보관 상태

프로젝트 종료 후 서버 공간 절약을 위해 다음과 같이 정리했습니다.

```text
jijungsa/
├── src/                         # 수집·정제·분석·시각화 코드
├── tests/                       # 검증 코드
├── docs/                        # 분석 명세 및 보고서
├── figures/                     # 최종 및 탐색 시각화
├── results/                     # 통계 분석 결과
├── data/
│   ├── raw/                     # 로컬 전용, Git 제외
│   ├── processed/               # 로컬 전용, Git 제외
│   ├── metadata/                # 출처·hash·구조·검증 기록
│   └── interim-archive.tar.gz   # 로컬 전용, Git 제외
├── requirements.txt
└── README.md
```

로컬 분석 환경에서는 대용량 원본·정제·중간 데이터를 별도로 보관하지만 공개 Git 저장소에는 포함하지 않습니다.

기존 `.venv/`는 재생성 가능한 환경이므로 프로젝트 종료 시 제거했습니다.

## 중간 데이터 복구

`data/interim-archive.tar.gz`는 공개 저장소에 포함되지 않습니다. 로컬 백업을 보유한 경우에만 다음 명령으로 복구할 수 있습니다.

```bash
tar -xzf data/interim-archive.tar.gz -C data
```

복구 후:

```text
data/interim/
```

이 다시 생성됩니다.

압축본 자체를 검증하려면:

```bash
gzip -t data/interim-archive.tar.gz
tar -tzf data/interim-archive.tar.gz >/dev/null
```

## Python 환경 재생성

가상환경은 저장하지 않으므로 분석 코드를 다시 실행하려면 새로 생성합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

일부 Rozado 원본 archive 처리에는 `libarchive-tools`의 `bsdtar`가 필요합니다.

## 종료 snapshot 확인

중간 데이터를 복구하고 Python 환경을 만든 뒤 다음 명령으로 종료 시점 산출물을 확인할 수 있습니다.

```bash
.venv/bin/python src/analysis/close_analysis.py --check
```

`data/metadata/analysis_closure_20260914.json`에는 분석 종료 시점의 raw / processed 데이터, 코드, 결과, 문서, 그림 상태가 기록되어 있습니다.

이 snapshot은 Git commit이나 원격 백업을 대신하지 않습니다.

## Rozado 분석 재현

Rozado 데이터 전체 파이프라인을 다시 실행할 경우 먼저 `data/interim-archive.tar.gz`를 복구하고 Python 환경을 준비합니다.

주요 재현 순서는 다음과 같습니다.

```bash
.venv/bin/python tests/check_rozado_ingest.py
.venv/bin/python src/ingest/collect_rozado.py
.venv/bin/python src/ingest/inspect_rozado.py
.venv/bin/python tests/check_rozado_collection.py

.venv/bin/python tests/check_rozado_pairs.py
.venv/bin/python src/ingest/audit_rozado_pairs.py
.venv/bin/python tests/check_rozado_pair_outputs.py

.venv/bin/python tests/check_rozado_clean.py
.venv/bin/python src/clean/clean_rozado_name.py
.venv/bin/python tests/check_rozado_clean_outputs.py

.venv/bin/python tests/check_rozado_eda.py
.venv/bin/python src/analysis/eda_rozado_name.py
.venv/bin/python tests/check_rozado_eda_outputs.py

.venv/bin/python tests/check_rozado_inference.py
.venv/bin/python src/analysis/infer_rozado_name.py
.venv/bin/python tests/check_rozado_inference_outputs.py

.venv/bin/python tests/check_rozado_order_masking.py
.venv/bin/python src/clean/clean_rozado_order_masking.py
.venv/bin/python tests/check_rozado_order_masking_stats.py
.venv/bin/python src/analysis/infer_rozado_order_masking.py
.venv/bin/python tests/check_rozado_order_masking_outputs.py

.venv/bin/python src/visualization/build_final_figures.py
.venv/bin/python tests/check_pnas_freeze.py
```

새 환경에서 데이터를 다시 수집하면 metadata의 검증 시각이나 receipt가 갱신될 수 있으므로 종료 snapshot과 byte 단위로 동일하지 않을 수 있습니다.

Zenodo 원본 archive와 추출된 대용량 데이터는 공개 저장소에 재배포하지 않습니다. `data/metadata/`의 source manifest와 DOI를 통해 원 출처에서 다시 받을 수 있습니다.

## PNAS 재현

PNAS 분석은 65개 파일 hash와 의존성 snapshot으로 동결한 과거 작업입니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python src/ingest/inspect_pnas.py
.venv/bin/python src/ingest/audit_pnas.py
.venv/bin/python tests/check_pnas_overlap.py
.venv/bin/python tests/check_raw_guard.py

.venv/bin/python src/clean/clean_pnas.py
.venv/bin/python tests/check_pnas_clean.py

.venv/bin/python src/analysis/eda_pnas.py
.venv/bin/python tests/check_pnas_eda.py

.venv/bin/python tests/check_pnas_regression_backend.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python src/analysis/regress_pnas.py
.venv/bin/python tests/check_pnas_regression_outputs.py

.venv/bin/python tests/check_pnas_pairs.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python src/analysis/compare_pnas_models.py
.venv/bin/python tests/check_pnas_common_outputs.py
```

스크립트는 manifest에 기록된 로컬 PNAS 원본의 크기와 SHA-256을 확인하고, Stata 변수·라벨·행 수·읽기 경고 등을 metadata에 기록합니다.

원본 데이터와 저자 코드는 수정하지 않습니다.

## 데이터 구분

- `data/raw/`: 외부에서 받은 원본 자료. 가능한 한 원형 그대로 보존합니다.
- `data/processed/`: 분석에 직접 사용하는 정제 데이터입니다.
- `data/metadata/`: 출처, checksum, 구조, 검증 결과 및 종료 snapshot입니다.
- `data/interim-archive.tar.gz`: 로컬 전용 대용량 중간 산출물이며 공개 Git 저장소에는 포함하지 않습니다.
- `results/`: 통계 분석 결과와 표입니다.
- `figures/`: 탐색 및 최종 발표용 시각화입니다.

서로 다른 연구의 metric은 임의로 통합하지 않았으며, 논문 보고값과 직접 계산값도 구분해서 기록했습니다. 모델·실험 버전과 원본 파일 단위의 provenance를 유지하는 것을 원칙으로 했습니다.

## 정제 표 읽기

PNAS 정제 표는 `src/clean/clean_pnas.py`의 `read_processed(path, dtypes)`를 사용하는 것을 권장합니다.

`dtypes` 정보는 정제 report의 각 파일 항목에 저장되어 있습니다. 일반 CSV 기본 설정으로 읽으면 결측 코드의 빈 문자열 처리나 부동소수점 정밀도가 달라질 수 있습니다.

점수별 `_missing_code`는 값이 존재하면 빈 문자열이고, 결측이면 원래 Stata 표기를 유지합니다. `duplicate_original_row`는 중복 묶음의 첫 행을 포함한 전체 묶음을 표시합니다.

## 참고

`download_open_access_papers.sh`는 초기 문헌 수집 과정에서 사용한 보조 스크립트입니다. 오류 처리와 덮어쓰기 처리가 충분히 강하지 않으므로 현재 데이터 수집의 공식 재현 경로로 사용하지 않습니다.

이 프로젝트는 현재 **분석 완료 및 보관 상태**입니다.
