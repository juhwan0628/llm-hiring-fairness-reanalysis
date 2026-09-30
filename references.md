# 참고 논문 및 데이터 다운로드 가이드

> 2026-09-13 정정: Rozado 연구의 저널 출판본이 Crossref 공식 metadata에서 확인됐다. *PeerJ Computer Science* 12:e3628, 2026-02-17, DOI: https://doi.org/10.7717/peerj-cs.3628 . 아래의 “No / preprint” 및 “X”는 2025년 arXiv 버전에 대한 기존 분류이며, 연구의 현재 출판 상태를 뜻하지 않는다. 출판본과 Zenodo v4의 실험별 대응은 아직 미확정이다. 상세: [collection_report.md](collection_report.md).

> 선정 원칙: **peer-reviewed 연구를 핵심 근거로 사용하고, 원데이터·재현 코드가 공개된 연구를 우선한다.**
> 2026년 preprint는 최신 경향을 보여주는 탐색적 근거로만 사용한다.

---

## A. 핵심 분석 논문

### 1. An, Huang, Lin, & Tai (2025) — 최우선

**Measuring gender and racial biases in large language models: Intersectional evidence from automated resume evaluation**

- 저널: *PNAS Nexus*, 4(3), pgaf089
- 출판: 2025-03-12
- Peer-reviewed: **Yes**
- DOI: `10.1093/pnasnexus/pgaf089`
- 규모: 약 361,000 resume evaluations
- 모델: GPT-3.5 Turbo, GPT-4o, Gemini 1.5 Flash, Claude 3.5 Sonnet, Llama 3-70B
- 핵심: gender × race intersectional bias
- 역할: **본 과제의 주 분석 데이터셋**

공식 논문:
https://academic.oup.com/pnasnexus/article/4/3/pgaf089/8071848

무료 전체본문(PMC):
https://pmc.ncbi.nlm.nih.gov/articles/PMC11937954/

Preprint:
https://arxiv.org/abs/2403.15281

Replication data + code:
https://osf.io/4dahv/

**왜 중요한가**
- 여러 주요 LLM을 동일한 연구설계에서 직접 비교
- 지원자 능력을 통제하고 social identity를 무작위화
- 원 데이터 및 재현 코드 공개
- 본 과제의 모델별 비교와 intersection heatmap을 직접 재분석 가능

---

### 2. Rozado (2025)

**Gender and Positional Biases in LLM-Based Hiring Decisions: Evidence from Comparative CV/Résumé Evaluations**

- 저자: David Rozado
- 공개: 2025
- Peer-reviewed: **No / preprint**
- 규모: 22 LLM × 70 professions
- 핵심: gender bias + candidate position bias
- 역할: **다수 모델 확장 분석**

논문:
https://arxiv.org/abs/2505.17049

PDF:
https://arxiv.org/pdf/2505.17049

공개 데이터/코드:
https://zenodo.org/records/17173798

Zenodo DOI:
`10.5281/zenodo.17173798`

공개 파일:
- `code.rar` 약 1 MB
- `experimental data.rar` 약 280.7 MB

**왜 중요한가**
- 모델 수가 매우 많음
- 동일한 CV의 male/female cue를 교환하는 counterbalanced design
- gender-neutral candidate 조건으로 positional bias도 확인 가능
- prompt와 model response까지 공개되어 추가 분석에 적합

**주의**
peer-reviewed 연구가 아니므로 PNAS 결과보다 강한 결론의 근거로 사용하지 않는다.

---

## B. Peer-reviewed 보조 연구

### 3. Iso et al. (2025)

**Evaluating Bias in LLMs for Job-Resume Matching: Gender, Race, and Education**

- 학회: NAACL 2025 Industry Track
- Peer-reviewed: **Yes**
- DOI: `10.18653/v1/2025.naacl-industry.55`
- 핵심: gender / race / education background
- 역할: **명시적 demographic bias와 implicit/proxy bias 비교**

공식 페이지:
https://aclanthology.org/2025.naacl-industry.55/

PDF:
https://aclanthology.org/2025.naacl-industry.55.pdf

arXiv:
https://arxiv.org/abs/2503.19182

**과제 활용**
최근 모델에서 직접적인 gender/race bias가 상대적으로 줄어들어도 educational background와 같은 변수가 평가에 영향을 줄 수 있다는 논거에 사용.

---

### 4. An et al. (2024)

**Do Large Language Models Discriminate in Hiring Decisions on the Basis of Race, Ethnicity, and Gender?**

- 학회: ACL 2024, Short Papers
- Peer-reviewed: **Yes**
- DOI: `10.18653/v1/2024.acl-short.37`
- 핵심: 이름을 이용한 race/ethnicity/gender manipulation
- 역할: **name discrimination + prompt sensitivity**

공식 페이지:
https://aclanthology.org/2024.acl-short.37/

PDF:
https://aclanthology.org/2024.acl-short.37.pdf

arXiv:
https://arxiv.org/abs/2406.10486

**과제 활용**
같은 demographic group이라도 prompt template에 따라 상대적 acceptance rate가 달라질 수 있다는 점을 통해 “모델 공정성”이 모델명 하나로 고정되는 특성이 아님을 설명.

---

### 5. Lippens (2024)

**Computer says ‘no’: Exploring systemic bias in ChatGPT using an audit approach**

- 저널: *Computers in Human Behavior: Artificial Humans*
- Peer-reviewed: **Yes**
- Open Access: **Yes**
- DOI: `10.1016/j.chbah.2024.100054`
- 규모: 34,560 vacancy–CV combinations
- 핵심: ethnic + gender bias in ChatGPT
- 역할: **초기 ChatGPT audit baseline**

공식 페이지:
https://www.sciencedirect.com/science/article/pii/S2949882124000148

arXiv:
https://arxiv.org/abs/2309.07664

기관 저장소 PDF:
https://backoffice.biblio.ugent.be/download/01HQJV82M4XY2PDVB0BTT257EP/01HQJV9V3QRMG39Y8A9CY7MDEQ

**과제 활용**
최근 모델 이전의 ChatGPT 기반 지원자 평가에서 나타난 ethnic/gender disparity의 배경 자료.

---

### 6. Vaishampayan et al. (2025)

**Human and LLM-Based Resume Matching: An Observational Study**

- 학회: Findings of NAACL 2025
- Peer-reviewed: **Yes**
- DOI: `10.18653/v1/2025.findings-naacl.270`
- 데이터: 실제 제출된 736 resumes
- 비교: human ratings vs GPT-4
- 역할: **인간 평가를 기준선으로 비교**

공식 페이지:
https://aclanthology.org/2025.findings-naacl.270/

PDF:
https://aclanthology.org/2025.findings-naacl.270.pdf

**과제 활용**
“AI가 편향되어 있으므로 인간에게 맡기면 된다”는 단순한 결론을 피하고, 인간과 LLM의 rating 차이와 fairness를 함께 논의.

---

## C. 최신 경향 탐색용 preprint

### 7. Gao, Jiang, & Yan (2026)

**Can LLMs Hire Fairly? Racial Bias in Resume Screening**

- 공개: 2026-06-27
- Peer-reviewed: **No / preprint**
- 모델: 14 mainstream LLMs
- 각 모델: 24,024 paired postings
- 핵심: model generation에 따른 racial/gender bias direction 변화
- 역할: **모델 세대별 변화 탐색**

arXiv:
https://arxiv.org/abs/2606.28978

PDF:
https://arxiv.org/pdf/2606.28978

**과제 활용**
2023-vintage model과 2024+ model에서 bias direction이 달라지는 결과를 바탕으로
“편향 감소인가, 방향 전환인가?”를 토론.

**주의**
preprint이므로 확정된 일반적 사실처럼 표현하지 않는다.

---

### 8. Tan et al. (2026)

**Small Changes, Big Impact: Demographic Bias in LLM-Based Hiring Through Subtle Sociocultural Markers in Anonymised Resumes**

- 공개: 2026
- Peer-reviewed: **No / preprint**
- 데이터: 100 neutral resumes → 4,100 variants
- 모델: 18 LLMs
- 핵심: anonymised resume의 sociocultural proxy
- 역할: **PII 제거 이후의 proxy bias 탐색**

arXiv:
https://arxiv.org/abs/2603.05189

PDF:
https://arxiv.org/pdf/2603.05189

**과제 활용**
이름을 삭제해도 language, hobbies, extracurricular activity 등이 ethnicity/gender의 proxy로 작동할 가능성을 설명.

**주의**
2026-08까지 revision된 최신 preprint이므로 주 분석보다는 토론·향후 연구 부분에 배치.

---

# 권장 읽기 순서

## 반드시 읽기

1. **An et al. 2025 — PNAS Nexus**
2. **Rozado 2025**
3. **Iso et al. 2025 — NAACL**

이 세 편을 읽으면 본 과제의 데이터 분석 구조가 거의 결정된다.

## 그다음

4. Vaishampayan et al. 2025 — 인간 vs LLM
5. An et al. 2024 — prompt-sensitive discrimination
6. Lippens 2024 — 초기 baseline

## 발표를 고급화할 때

7. Gao et al. 2026 — 세대별 bias reversal
8. Tan et al. 2026 — proxy / sociocultural bias

---

# 분석 우선순위

## 1순위

PNAS OSF 데이터를 Oracle Cloud에 내려받아 구조 확인.

확인할 것:
- 원본 데이터 파일 형식
- model column
- race/gender column
- score column
- occupation / resume quality 관련 변수
- 제공된 replication code

## 2순위

Rozado Zenodo 데이터를 다운로드.

확인할 것:
- 22개 모델명
- experiment condition
- male/female selection
- prompt ordering
- position bias condition
- profession

## 3순위

두 데이터셋의 metric을 억지로 하나로 합치지 않고 각각 독립 분석.

PNAS:
- score gap / regression coefficient / intersection

Rozado:
- selection rate / odds / position bias

## 4순위

peer-reviewed 보조 논문으로 해석 검증.

---

# 논문 상태 요약

| 논문 | Peer-reviewed | 원데이터/코드 | 주 역할 |
|---|---:|---:|---|
| An et al., PNAS Nexus 2025 | O | O | **주 분석** |
| Rozado 2025 | X | O | 22 LLM 확장 |
| Iso et al., NAACL 2025 | O | 논문 중심 | proxy bias |
| An et al., ACL 2024 | O | 논문 중심 | prompt sensitivity |
| Lippens 2024 | O | 공개 연구 | 초기 baseline |
| Vaishampayan et al., NAACL 2025 | O | 논문 중심 | human comparison |
| Gao et al. 2026 | X | preprint | generation trend |
| Tan et al. 2026 | X | preprint | sociocultural proxy |

---

# 핵심 판단

현재 자료만으로도 과제는 충분히 수행 가능하다.

특히 **PNAS Nexus 2025의 공개 replication data**를 주 데이터로 두고,
**Rozado의 22-LLM 공개 raw data**를 확장 데이터로 두는 구성이 가장 강하다.

여기에 peer-reviewed NAACL/ACL 연구를 해석 근거로 결합하면,
단순 문헌조사가 아니라 실제 공개 데이터의 재분석을 포함하는 과제로 만들 수 있다.
