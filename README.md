# LLM 채용 평가 편향 공개 데이터 재분석

이 저장소는 **LLM 기반 채용 평가에서 나타나는 성별·이름·순서 관련 편향을 공개 데이터로 재분석한 종료 프로젝트**입니다.

분석은 **2026-09-14에 종료**했으며, PNAS 데이터 재분석과 Rozado 데이터의 name / order / masking 분석, 최종 보고서 및 발표용 시각화까지 완료했습니다.

이 공개 저장소에는 코드·문서·메타데이터·집계 결과·직접 생성한 시각화만 포함합니다. 원본/정제/중간 데이터와 행 단위 파생표는 제3자 자료의 재배포를 피하기 위해 포함하지 않습니다.


## 공개 저장소 범위

- 포함: 분석 코드, 테스트, provenance/출처 metadata, 집계 통계, 보고서, 발표 PDF, 직접 생성한 SVG 시각화
- 제외: 원본·정제·중간 데이터, 행 단위 파생표, 논문 PDF, 내부 에이전트 작업기록
- 제3자 데이터의 권리와 라이선스는 원 저자·배포처에 있으며, 이 저장소는 해당 자료를 재라이선스하지 않습니다.

자세한 내용은 [NOTICE.md](NOTICE.md)를 참고하세요.

## 주요 결과물

- [최종보고서](docs/final_report.md)
- [10분 발표 스토리라인](docs/final_storyline.md)
- [발표 스크립트](docs/presentation_script_10min.md)
- [최종 검증 기록](docs/final_validation.md)
- [발표 PDF](지정사%20발표%20PPT.pdf)
- [발표용 그래프](figures/final/README.md)
- [출처 manifest](data/metadata/source_manifest.json)

공개 저장소는 포트폴리오·재현 설명에 필요한 핵심 산출물만 담은 curated snapshot입니다. 원본/행 단위 데이터와 상세 중간 산출물은 재배포하지 않습니다.

## 현재 보관 상태

프로젝트 종료 후 서버 공간 절약을 위해 다음과 같이 정리했습니다.

```text
llm-hiring-fairness-reanalysis/
├── src/              # 수집·정제·분석·시각화 코드
├── tests/            # 핵심 결과 검증 코드
├── docs/             # 최종 보고서·발표 문서
├── figures/final/    # 최종 SVG 시각화
├── results/          # 공개 가능한 집계 통계 결과
├── data/metadata/    # 출처 및 provenance metadata
└── 지정사 발표 PPT.pdf
```

로컬 분석 환경에서는 대용량 원본·정제·중간 데이터를 별도로 보관하지만 공개 Git 저장소에는 포함하지 않습니다.

기존 `.venv/`는 재생성 가능한 환경이므로 프로젝트 종료 시 제거했습니다.

## Python 환경 재생성

가상환경은 저장하지 않으므로 분석 코드를 다시 실행하려면 새로 생성합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

일부 Rozado 원본 archive 처리에는 `libarchive-tools`의 `bsdtar`가 필요합니다.

## 재현 안내

분석 코드는 `src/`에 공개되어 있지만 원본·행 단위 데이터는 이 저장소에 재배포하지 않습니다. `data/metadata/`의 source manifest와 `references.*`에 기록된 원 출처에서 데이터를 취득한 뒤 `requirements.txt` 환경에서 실행해야 합니다. 공개 저장소의 `results/`에는 보고서와 발표에 사용한 집계 결과를 포함합니다.

## 공개 데이터 구분

- `data/metadata/`: 출처와 provenance 정보
- `results/`: 공개 가능한 집계 결과
- `figures/final/`: 최종 시각화
- 원본·정제·중간·행 단위 데이터: 공개 저장소에서 제외

## 참고

`download_open_access_papers.sh`는 초기 문헌 수집 과정에서 사용한 보조 스크립트입니다. 오류 처리와 덮어쓰기 처리가 충분히 강하지 않으므로 현재 데이터 수집의 공식 재현 경로로 사용하지 않습니다.

이 프로젝트는 현재 **분석 완료 및 보관 상태**입니다.
