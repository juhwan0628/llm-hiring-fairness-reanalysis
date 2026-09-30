# AI 채용 편향 프로젝트 실행 계획

작성일: 2026-09-13. 상태: 수집 전 계획. 분석 결과가 아님.

후속 진행: 이 문서는 수집 전 계획을 보존한다. 실제 수집·구조 확인 결과와 정정 사항은 [collection_report.md](collection_report.md)를 참조한다. OSF 접근 성공 및 Rozado 저널 출판 확인으로 아래 당시 미확정 사항 일부가 해소됐다.

## 1. 현재 프로젝트 이해

공개 원데이터에서 LLM 지원자 평가의 집단별 격차를 재계산하고, 입력부터 표·그림까지 재실행 가능한 secondary-data analysis pipeline을 만든다.

- 1순위: An et al. (2025), PNAS Nexus, OSF replication data/code.
- 2순위: Rozado (2025), Zenodo experimental data/code.
- 동일 연구 내부의 동일 조건 모델 비교를 우선한다. 연구 간 metric을 통합한 Fairness Score나 모델 순위는 만들지 않는다.
- PNAS의 점수 평가와 Rozado의 후보자 쌍 선택을 구분한다. PNAS 관측값에 paired design을 임의로 가정하지 않는다.
- 논문 보고값과 직접 계산값을 분리한다. 예상 결론은 가설이며 결과 선택의 기준이 아니다.
- Assumption: 신규 LLM API 호출 없이 공개 응답을 재분석한다. Proxy bias·인간 비교는 별도 원자료 확보 전까지 문헌 논의로 한정한다.

## 2. 현재 서버 환경

아래는 같은 세션의 최초 읽기 전용 점검 결과다. 설치·Git 초기화·가상환경 생성은 하지 않았다.

| 항목 | 확인값 |
|---|---|
| 작업 디렉터리 | `<project-root>` |
| OS / CPU 아키텍처 | Ubuntu 24.04.4 LTS / aarch64 |
| 논리 CPU | 4 |
| Python / pip | 3.12.3 / 24.0 |
| 메모리 / swap | 23 GiB / 8 GiB |
| 디스크 여유 | 약 171 GB, raw 확장 크기는 미확인 |
| Git | 2.43.0 설치, 현재 경로는 저장소 아님 |
| 분석 패키지 | 현재 python3에서 numpy, pandas, scipy, statsmodels, matplotlib, pyarrow 미설치 |
| 도구 | curl·tmux 있음. unrar·7z·bsdtar·unzip·shellcheck 없음 |
| venv | 모듈 존재. 생성·pip bootstrap 미검증 |

실제 수집 전에 디스크를 다시 확인한다. ARM 환경에서 필요한 reader·압축 도구의 가용성은 실제 파일 형식에 맞춰 검증한다.

## 3. 기존 파일 검토 결과

proposal.md, references.md, references.bib, download_open_access_papers.sh 전체를 읽었다. ZIP 내 네 파일은 로컬 파일과 바이트 단위로 일치했다. ZIP에만 있는 README.md도 메모리에서 읽었다. 압축은 해제하지 않았다.

- proposal.md: 목적·우선순위는 적절하다. 페이지·표 중심 provenance를 원파일·관측값·experiment까지 확장해야 한다.
- references.md: 접근 가능성과 원자료 공개 범위를 실제 목록으로 검증해야 한다. Rozado 출판 상태는 아래 추가 조사 사항 참조.
- references.bib: 논문 8개 수록. 데이터셋 인용·버전·접근일을 추후 보강한다.
- 다운로드 스크립트: `bash -n` 통과. 실행하지 않았다. OSF·Zenodo 데이터는 다운로드하지 않고 URL만 출력한다.

### 스크립트 URL과 출력 경로

아래 출력은 모두 `papers/` 상대 경로다. 파일명 간 충돌은 없지만 실행 디렉터리에 의존하며 기존 파일을 덮어쓴다. 전체 PDF의 실제 수신 성공·내용은 미검증이다.

| URL | 출력 파일명 | 검토 |
|---|---|---|
| https://arxiv.org/pdf/2403.15281 | 01_an_2025_pnas_resume_bias.pdf | 관련 2024 preprint. 2025 출판본과 혼동하지 않도록 버전 표시 필요 |
| https://arxiv.org/pdf/2505.17049 | 02_rozado_2025_gender_position_bias.pdf | 공식 abs 페이지 제목 일치. 버전 고정 필요 |
| https://aclanthology.org/2025.naacl-industry.55.pdf | 03_iso_2025_naacl_bias_job_resume.pdf | 공식 페이지 제목 일치 |
| https://aclanthology.org/2024.acl-short.37.pdf | 04_an_2024_acl_hiring_discrimination.pdf | 공식 페이지 제목 일치 |
| https://backoffice.biblio.ugent.be/download/01HQJV82M4XY2PDVB0BTT257EP/01HQJV9V3QRMG39Y8A9CY7MDEQ | 05_lippens_2024_computer_says_no.pdf | HEAD 200, application/pdf, 2,415,777 bytes. 내용 일치는 미검증 |
| https://aclanthology.org/2025.findings-naacl.270.pdf | 06_vaishampayan_2025_human_llm_resume.pdf | 공식 페이지 제목 일치 |
| https://arxiv.org/pdf/2606.28978 | 07_gao_2026_llms_hire_fairly.pdf | 공식 abs 페이지 제목 일치 |
| https://arxiv.org/pdf/2603.05189 | 08_tan_2026_sociocultural_markers.pdf | 공식 abs 페이지 제목 일치 |

향후 수정 조건: 프로젝트 루트 기준 `papers/pdf/`, HTTP 오류 실패 처리, timeout·제한된 retry, 임시 파일 수신 후 형식 검증과 최종 이동, 기존 파일 무단 덮어쓰기 방지, 버전·URL·checksum 기록. `set -euo pipefail`만으로 HTTP 오류 페이지 저장은 막을 수 없다. 이번에는 스크립트를 변경하지 않는다.

## 4. 권장 프로젝트 구조

아래는 제안이다. 디렉터리를 미리 만들지 않는다. `papers/pd`는 기존 요청 맥락상 `papers/pdf`로 해석한다(Assumption).

```text
jijungsa/                       # 현재 경로 유지 제안
├── 기존 자료 5개
├── execution_plan.md
├── README.md
├── requirements.txt
├── papers/{pdf,notes}/
├── data/
│   ├── raw/{pnas_2025,rozado_2025}/
│   ├── interim/{pnas_2025,rozado_2025}/
│   ├── processed/{pnas_2025,rozado_2025}/
│   └── metadata/
├── src/{pnas_2025,rozado_2025}/
├── notebooks/
├── results/{pnas_2025,rozado_2025}/
├── figures/{pnas_2025,rozado_2025}/
├── tests/
├── logs/
└── docs/
```

연구별 src 내부에 ingest·clean·analysis·plot 스크립트를 필요한 만큼 추가한다. 공통 추상화는 실제 중복이 확인될 때만 만든다. requirements.txt와 가상환경으로 시작하고 데이터 형식 확인 후 필요한 패키지만 고정한다.

raw에는 받은 archive·저자 코드·데이터를 변경 없이 보관한다. 압축 해제 사본은 interim에 둔다. 수정해야 하는 저자 코드는 작업 사본에서만 다룬다. 정제 관측값은 processed, 추정치·검정 결과는 results에 둔다. Git에는 코드·문서·작은 metadata를 중심으로 기록하고 대형 원자료는 제외한다.

## 5. 데이터셋별 수집 계획

### PNAS / OSF

공식 출판사의 Data Availability에서 저장소 주소를 확인했다.

- 논문: https://academic.oup.com/pnasnexus/article/4/3/pgaf089/8071848
- 저장소: https://osf.io/4dahv/
- 본문 대체 경로: https://pmc.ncbi.nlm.nih.gov/articles/PMC11937954/
- 보충자료 후보: `pgaf089_supplementary_data.docx`, PMC 검색 metadata 표시 약 2.4 MB. 원데이터로 간주하지 않으며 아직 수신하지 않았다.

2026-09-13 접근 결과: 이전 웹 조회는 OSF 403. 이번 웹 도구의 API 조회도 실패했고, 서버에서 아래 metadata endpoint를 20초 timeout으로 조회했으나 둘 다 read timeout이었다. 저장소 삭제·비공개라고 단정할 수 없다.

- `https://api.osf.io/v2/nodes/4dahv/`
- `https://api.osf.io/v2/nodes/4dahv/files/osfstorage/`

따라서 실제 OSF 파일명·크기·형식·버전·라이선스는 미확정이다. CSV나 Stata 파일 등이 있다고 추측해 manifest를 채우지 않는다.

향후 조사·수집 순서:

1. OSF 공개 페이지 또는 API 접근 복구 시 node, 하위 component, storage provider와 페이지네이션을 포함한 목록 확보.
2. 파일 ID·경로·크기·수정일·버전·checksum·라이선스 기록.
3. README·변수 설명·replication code 우선 확인. 코드 실행 전 외부 호출·입출력·의존성 검토.
4. 코드가 참조하는 평가 데이터·지원자 특성·실험조건 파일의 의존 관계 작성.
5. 출판본·보충자료의 핵심 표와 연결되는 최소 파일 집합 수집.
6. 관측 단위, 모델별 표본 수, 이력서 반복 여부, 원응답 제공 여부 검증.

접근이 계속 안 되면 수집 보류 상태를 기록하고 Zenodo metadata 조사만 진행한다. 사용자 동의 없이 PNAS 주 분석을 다른 데이터로 대체하거나 저자에게 연락하지 않는다.

### Rozado / Zenodo

공식 record: https://zenodo.org/records/17173798

지정 record의 표시 버전은 v4, 공개일은 2025-09-29이다. 다음은 공식 페이지에서 확인한 표시 용량·checksum이며 로컬 파일 검증 결과가 아니다.

| 파일 | 용량 | 제공 MD5 |
|---|---|---|
| code.rar | 약 1.0 MB | 8ed9d587a601b3374bb94cc10084e5e9 |
| experimental data.rar | 약 280.7 MB | 3010c8031c88615d8f26709a1fcc8668 |

파일 링크 후보는 record의 Download 링크에서 확정한다. URL을 파일명으로 추측해 실행하지 않는다. API `https://zenodo.org/api/records/17173798`는 이번 서버 조회에서 read timeout이었다. 공개 페이지는 웹 도구로 조회 가능했다. 라이선스 값은 이번 조회에서 확인하지 못했다.

arXiv https://arxiv.org/abs/2505.17049 는 v1 2025-05-16, v2 2025-05-27을 표시한다. 데이터 v4가 더 나중이므로 제목 일치만으로 v2 완전 재현용이라고 확정하지 않는다.

추가 검증 필요: 2026년 PeerJ Computer Science 출판본 DOI `10.7717/peerj-cs.3628` 단서를 외부 색인과 ResearchGate 검색에서 발견했다. 공식 https://peerj.com/articles/cs-3628/ 는 403, DOI·Crossref 웹 조회도 실패했다. 기존의 “현재도 preprint만 존재” 설명은 확정적으로 유지하지 않는다. 출판사 metadata 확인 후 references와 bibliography 수정 여부를 결정한다. 이 단서를 출판 상태의 최종 검증으로 취급하지 않는다.

향후 수집 순서:

1. record metadata·라이선스·버전 관계·논문 대응을 기록.
2. code.rar 먼저 수집하고 archive 목록과 코드 입력 의존성 검토.
3. experimental data.rar 수집 후 제공 MD5 검증 및 로컬 SHA-256 기록.
4. archive 경로 탈출·중복 경로·확장 크기 확인 후 interim으로 해제.
5. 이름·명시적 성별·중립 identifier·pronoun·단독 점수 평가 등 실제 experiment를 분리.
6. candidate identity, A/B label, 실제 prompt 순서, 이름 교환 pair를 별도 변수로 매핑.

## 6. 분석 pipeline 설계

| 단계 | 작업 | 완료 기준 / 산출물 |
|---|---|---|
| 수집 | 버전 지정·checksum 검증·원본 보존 | source manifest, 수집 로그 |
| 구조 확인 | schema·관측 단위·키·반복 구조·experiment 분류 | 데이터 사전, 파일 의존 관계, 분석 가능 범위 |
| 정제 | 자료형·라벨 정리, 응답 파싱, 실패 사유 기록 | 연구별 processed 표, 정제·제외 내역 |
| Exploratory analysis | 표본 수·분포·결측·직업 구성·pair 완전성 | 탐색 표·그림, 확정 분석 명세 |
| Statistical analysis | 원 논문 핵심 결과 재현 후 별도 추가 분석 | 효과 추정치·CI·표본 수·검정 결과 |
| Visualization | results에서 script로 생성 | PNG와 SVG/PDF, caption, 입력 결과 연결 |
| Validation | raw hash·변환·계산·재실행 검증 | 검증 보고서, reported/computed 비교표 |

검증은 마지막에만 하지 않고 각 단계에서도 수행한다. Notebook은 탐색용이며 채택한 계산은 Python script로 옮긴다.

### 통계 분석 명세의 확정 조건

- PNAS: 비조정 score gap과 조정 회귀계수를 분리. 원 논문의 표본 필터·공변량·고정효과·표준오차 정의 확인 후 재현. 성별×인종 대비와 interaction은 해당 데이터가 지원하는 범위에서 수행.
- PNAS threshold 기반 selection은 가정한 점수 cutoff의 결과다. 실제 채용 여부와 구분하고 기준 threshold 및 민감도 분석을 명시.
- Rozado: counterbalanced pair 구조를 보존. gender selection, A/B label preference, 첫 번째 위치 선호를 구분. 단독 평가 점수는 쌍 선택률과 분리.
- 모델 비교: 공통 표본·조건 여부를 확인한다. 서로 다른 반복 관측을 독립으로 취급하지 않는다.
- 미확정: 기준집단, 주요 대비, cluster 단위, 직업별 가중치, tie·거절·파싱 실패의 분모 처리. schema·설계 확인 후 결과 검정을 보기 전에 명세에 고정.
- 다중비교 family와 보정법을 기록한다. 유의성만으로 공정/불공정을 판정하지 않는다.
- 결측값·모델 snapshot을 추정하지 않는다. NA에는 가능한 경우 사유를 별도로 기록한다. 0 분모의 비율은 정의 불가로 남긴다.
- 이름이 암시하는 집단 라벨은 실험에서 조작한 cue다. 실제 개인의 성별·인종을 추론한 사실로 표현하지 않는다.

### Provenance와 실행 기록

`paper_id → dataset version → source file/hash → 원본 locator → experiment_id → observation_id → analysis_id → 표/그림`

locator는 원본 행, JSON 경로, archive 내부 경로 등 실제 형식에 맞춘다. 원본 ID가 없으면 파일 hash와 locator에서 추적용 ID를 만들고 원본 ID가 아님을 표시한다. 집계 결과는 여러 입력 관측값과 연결되도록 필터·집계 정의 및 입력 파일 hash를 보존한다.

source manifest 예정 필드: paper_id, dataset_id, version, file_id, source_url, resolved_url, retrieved_at_utc, bytes, upstream_checksum, sha256, local_path, license, access_status. 미확인은 빈값과 사유로 남긴다.

결과 metadata: reported/computed 구분, experiment, metric, 단위, 기준집단, 분모, 표본 수, 설정, 입력 hash, 코드 commit, Python·패키지 버전, random seed(난수 사용 시). 논문 보고값은 논문 버전·페이지·표/그림 locator 추가.

## 7. 예상 위험요소

| 위험 | 대응 |
|---|---|
| OSF 접근 실패 / 파일 누락 | 접근 상태와 재현 불가능 범위 명시. 다른 연구로 자동 대체하지 않음 |
| 논문·데이터 버전 불일치 | 각각 고정, 변경 이력 및 입력 의존성 대조 |
| 원데이터 대신 집계자료만 공개 | 수행 가능한 재현 수준을 구분 |
| 파일 형식·코드 언어 차이 | 실제 형식 확인 후 reader 선택. 유료 도구 의존 시 Python 재구현 가능성 검토 |
| metric 차이 | 연구별 분석·단위 유지, 통합 score 금지 |
| 모델명·버전 누락 | 원래 문자열 보존, unknown 명시 |
| 반복 관측·불완전 pair | 설계 단위 보존, 의존성 반영, 제외 기록 |
| huge responses / 압축 팽창 | 원응답과 분석 표 분리. 크기 확인 후 필요 시 chunk 처리 |
| 파싱 오류·tie·거절 | 별도 상태. 비선택으로 자동 변환하지 않음 |
| 표본 불균형 | 직업 동일 가중과 관측치 가중 결과 구분 |
| 결과 선별·다중검정 | 주 분석 대비 사전 기록, 탐색 결과 표시 |
| 라이선스·재배포 범위 | 공개 접근과 재배포 허용 구분, 라이선스 확인 |
| 해석 과장 | 실험 조건 밖의 실제 채용·현재 모델·alignment 원인으로 일반화하지 않음 |

## 8. 다음 단계에서 실제로 수행할 작업

현재 단계에서 완료: 기존 자료 검토, 환경 확인, 공식 metadata 조사, 본 문서 작성. 논문 PDF·archive·dataset 수신, 스크립트 실행·수정, 패키지 설치, 폴더 일괄 생성, 분석 코드 구현은 하지 않았다.

다음 수집 단계의 순서:

1. OSF 접근 복구 여부와 파일 목록 확인. 불가하면 차단 상태 유지.
2. Rozado 출판 상태·논문 버전·Zenodo v4 대응·라이선스 확인.
3. 실제 URL·크기·checksum을 갖춘 수집 manifest 작성.
4. 다운로드 스크립트 보완, 필요한 최소 폴더·가상환경·Git 설정.
5. 문서·저자 코드부터 수집해 입력 의존성 검토 후 필요한 raw 수집.
6. 구조 확인 보고서 작성. 그 뒤 정제·통계 명세 확정 및 구현.

수집 전 확정할 항목: 원자료 접근, 파일 목록, 라이선스, 용량, 버전. 통계 분석 전 확정할 항목: 관측 단위, pair/cluster 구조, 주요 대비, 결측·분모 처리, 가중치, 다중비교 계획. 지금 임의로 확정하지 않는다.

주요 최종 산출물: 출처 manifest, 데이터 사전, experiment/model mapping, 정제 표·제외 로그, 재실행 script·환경 명세, reported/computed 비교표, 발표용 그림·caption, 원본 무결성·파싱·pair 보존·metric 계산 테스트, 재실행 검증 보고서와 README.
