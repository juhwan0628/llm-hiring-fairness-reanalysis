# 수집·구조 확인 보고서

확인일: 2026-09-13. 편향 분석 결과가 아닌 자료 확보 및 schema 점검 결과다.

후속 점검 완료: [PNAS 정제 명세](docs/pnas_cleaning_spec.md). baseline/heter의 행 순서 차이, 파일 간 직함 code mapping 차이, 모델별 결측과 인코딩 문제의 위치를 확인했다. 아래는 최초 수집 당시 기록이다.

## 완료 범위

- OSF API 접근 성공. provider 1개(osfstorage), 하위 component 0개, 파일 7개와 목록의 next=null 확인.
- PNAS 파일 7개, 총 62,303,866 bytes 수집. 전부 제공 SHA-256 및 파일 크기 일치.
- 저자 ReadMe.txt와 Code.do 전체 읽기. 실행하지 않음.
- Stata 데이터 5개의 행·변수·라벨·인코딩 경고 확인. 원본 hash 재검증.
- 프로젝트 가상환경 생성, pandas 및 의존 패키지 설치·버전 고정. pip check 통과.
- Git 저장소 초기화, raw·가상환경·대형 백업 제외 규칙 추가. commit·원격 설정은 하지 않음.
- Rozado 저널 출판 metadata 확인. 기존 제안서·출처 가이드에 정정 주석 추가, bibliography에 출판본·데이터 출처 추가.

## PNAS 확보 파일

공식 출처: https://osf.io/4dahv/ . 파일별 URL·버전·수신 시각·SHA-256은 [manifest](data/metadata/source_manifest.json)에 기록했다. 각 파일 current_version=1. OSF 프로젝트 metadata에 지정된 라이선스는 MIT다. 라이선스 응답과 저작권자 정보도 저장했다.

| 파일 | bytes | 행 × 변수 | 분류·역할 |
|---|---:|---|---|
| ReadMe.txt | 443 | — | 실행 환경·수동 결과 저장 설명 |
| Code.do | 35,035 | — | Stata 재현 코드 |
| data_gpt35_baseline.dta | 18,703,831 | 332,895 × 17 | Figure 1 및 Figure 3·4 재추정 입력 |
| data_gpt35_heter.dta | 21,368,271 | 332,895 × 19 | Figure 2 이질성 분석 입력 |
| data_score_4models.dta | 21,993,856 | 332,257 × 20 | Figure 5의 4개 모델 점수 |
| data_bootstrap_gpt35.dta | 173,035 | 3,000 × 7 | 저자 저장 추정치, Figure 3 그림 입력 |
| data_magnitude_gpt35.dta | 29,395 | 36 × 31 | 저자 저장 추정치, Figure 4 그림 입력 |

위 행 수는 직접 파일을 읽어 확인한 구조 정보다. 논문의 약 361,000이라는 설명과 자동으로 동일시하지 않는다. 저자의 원실험에서 현재 공개 표가 만들어진 필터·파싱 과정을 추가 확인해야 한다.

### 확인된 변수와 재현 조건

- 점수: baseline의 `score_gpt35`; 4models의 `score_gemini`, `score_llama`, `score_gpt4o`, `score_claude`.
- 공변량: `worknum`, `edunum`, `skillnum`, `num_high_level`, `avg_duration_work`, `first_work_start`, `avg_length_work_desc`, `duration_edu`, `first_edu_start`, `highest_degree`.
- 고정효과: `iposition`, `istate`, `last_work_title`.
- 저자 코드 cluster: `iposition#istate`의 조합. 두 변수를 별도 multiway cluster로 처리하는 것과 다르다.
- gender label 정의: 1=female, 2=male. baseline ethnicity label: 1=black, 2=white. 코드의 기준 category는 `ib2`.
- 4models에는 asian·hispanic의 label 정의도 있다. label 정의만으로 실제 관측값에 해당 집단이 존재한다고 주장하지 않는다. 실제 코드값과 분석 포함 범위는 정제 단계에서 확인한다.
- 파일에 명시적인 지원자 고유 ID·원 prompt·전체 응답 컬럼은 없다. 관측값의 provenance는 우선 파일 hash와 원본 행 번호로 보존한다. 행 번호는 파일 간 동일 지원자를 연결하는 ID로 쓰지 않는다.
- baseline과 4models는 행 수가 다르다. 638행 차이의 원인을 추측하지 않으며 행 순서로 join하지 않는다.

### 저자 코드에서 확인한 제한

ReadMe는 Stata/MP 16.0과 `reghdfe`, `resize`를 요구한다. Code.do에는 `eststo`, `resizecombine`도 등장하므로 Stata에서 직접 실행할 때 실제 package 의존성 점검이 더 필요하다. 이번에는 Stata나 해당 명령을 설치·실행하지 않았다.

Figure 3·4의 추정 결과를 저자가 수동으로 별도 데이터에 저장했다고 ReadMe에 명시돼 있다. 따라서 두 결과 파일을 읽어 그림을 그리는 작업은 원관측으로 회귀를 재계산한 작업이 아니다. 우리 결과에는 저자 저장 추정치와 직접 재추정치를 분리해야 한다.

Figure 3 코드의 `uniform()<.2`는 각 행을 확률적으로 약 20% 선택하는 반복 subsampling이다. 파일명·주석에 bootstrap이라 적혀 있어도 복원추출 bootstrap으로 임의 구현하면 안 된다. `set seed`는 확인되지 않았다. 원그림 숫자의 완전 일치는 보장할 수 없으며 우리 재실행용 seed를 별도로 명시해야 한다.

그래프에는 숫자가 하드코딩된 `text()`도 있다. 우리 그림 숫자는 계산된 results에서만 가져와야 한다. 코드 첫 줄 `cd "..."`와 `graph ... replace` 때문에 저자 코드를 raw 위치에서 바로 실행해서도 안 된다.

### 인코딩 경고

baseline·heter를 pandas로 읽을 때 UTF-8 해석 실패 및 Latin-1 fallback 경고가 발생했다. 상세 경고는 [구조 목록](data/metadata/pnas_structure.json)에 파일별로 저장했다. 문자열 라벨의 정확성은 미확정이다. 원본은 변경하지 않았으며 자동 인코딩 교정도 하지 않았다.

첫 구조 metadata 저장 시 numpy int32 라벨 키가 JSON key로 지원되지 않아 실패했다. metadata에 한해 키를 정수 문자열로 변환한 뒤 재실행했고 성공했다. 원데이터 숫자·라벨은 변경하지 않았다.

## Rozado 확인 결과

Crossref의 출판사 등록 metadata에서 다음 출판본을 확인했다.

- David Rozado, *PeerJ Computer Science* 12:e3628.
- Published online: 2026-02-17.
- DOI: https://doi.org/10.7717/peerj-cs.3628
- 공식 metadata: https://api.crossref.org/works/10.7717/peerj-cs.3628
- 로컬 근거: [Crossref snapshot](data/metadata/rozado_crossref_20260913.json).

따라서 연구를 현재도 preprint만 존재하는 것으로 분류하는 것은 부정확하다. 다만 이 출판본과 2025 arXiv v2·Zenodo v4의 실험별 대응은 아직 확인하지 못했다. 논문에 대한 CC BY 4.0 metadata를 Zenodo 데이터 라이선스로 전용하지 않는다.

지정 Zenodo record는 https://zenodo.org/records/17173798 . 이전 공식 페이지 조회에서 `code.rar` 약 1.0 MB, `experimental data.rar` 약 280.7 MB와 MD5를 확인했다. 이번에는 페이지·API·code.rar 요청이 timeout, 수신 bytes=0이었다. 대형 experimental archive는 요청하지 않았다. 성공으로 표시한 Zenodo raw 파일은 없다.

## 산출물·검증

- `data/metadata/source_manifest.json`: PNAS verified 7개, Zenodo 코드 실패 1개·데이터 미수집 1개.
- `data/metadata/*_20260913.json`: OSF 파일·프로젝트·라이선스·provider·children 및 Crossref 응답.
- `data/metadata/metadata_receipts.json`: metadata hash와 접근 실패 기록.
- `data/metadata/pnas_structure.json`: 파일 hash와 연결된 변수·라벨·행 수·reader 경고.
- `src/ingest/inspect_pnas.py`: 원본 무결성 검사와 구조 확인 재실행. 편향 metric·회귀·정제 기능 없음.
- `requirements.txt`, `.gitignore`, `README.md`: 로컬 실행 환경과 데이터 보존 규칙.

## 다음 작업

1. Zenodo 연결 가능 시 metadata·코드를 우선 수집하고 checksum·라이선스·experiment 구조 확인.
2. PNAS 출판본·보충자료와 공개 관측 데이터의 표본 차이, ID 부재, 이름/원응답 공개 범위 확인.
3. 인코딩과 실제 demographic code 범위, 모델별 유효 관측 범위를 구조 점검 명세에 추가.
4. 위 확인 후 PNAS 정제 명세와 주 분석 대비를 고정. 그 다음에 정제·분석 코드를 구현.

자동 수집 기능과 기존 PDF 다운로드 스크립트 보완은 아직 미완료다. 새 checkout에서 다운로드부터 end-to-end로 재현된다고 주장하지 않는다. 이번 단계에는 정제 표·편향 분석·회귀·그림을 생성하지 않았다.
