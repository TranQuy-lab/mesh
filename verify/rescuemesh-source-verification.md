# RescueMesh-AI — source verification (2026-09-28)

Method: GitHub REST (`/repos`, `/git/trees?recursive=1`, `/commits`), raw READMEs/source, Crossref/OpenAlex/arXiv APIs, RFC editor, Kaggle, publisher PDFs. **`web_search` was dead in this session (HTTP 401)** — search was done via GitHub search API + DuckDuckGo/Bing HTML. ResearchGate 403, Semantic Scholar 429 (blocked).

| # | Item | Verdict |
|---|---|---|
| 1 | AleksPlekhov/ai-mesh-emergency-communication-platform | **EXISTS — largely implemented** (fork of bitchat-android) |
| 2 | njhyousha/ResqLink → ShadowVoid-T-T | **EXISTS, misattributed — mesh + "on-device Gemini" are simulated/cloud** |
| 3 | MeshGemma / Gemma 4 Good Hackathon | **EXISTS; Gemma 4 real; "grand-prize" UNVERIFIED** |
| 4 | raviprasad794063/disaster_mesh | **EXISTS — real BLE + Wi-Fi Direct, low maturity** |
| 5 | Crisis Mesh Messenger | **EXISTS — UI real, mesh is a stub** |
| 6 | RG 398912234 paper | **EXISTS but non-credible; contains a FABRICATED reference** |

## 1 — ResQMesh AI Platform ✅ substantial
<https://github.com/AleksPlekhov/ai-mesh-emergency-communication-platform> · Kotlin · **GPL-3.0** · **90★/32 forks** · created 2026-03-03 · pushed 2026-09-14 · branch `develop` · **fork=true, parent permissionlesstech/bitchat-android** (7,661★, GPL-3.0, 2025-07-08). 469 commits, 3 alpha releases.

Fork diff is real: the parent tree has **zero** `resqmesh`/`ai/`/`tflite`/`vosk` paths. The fork adds a Gradle module `:resqmesh-ai` (in `settings.gradle.kts`; `:app` does `implementation(project(":resqmesh-ai"))`) containing 2 TFLite models (1.16 MB text, 2.68 MB vision), `TFLiteMessageClassifier.kt` (tokenizer→TFLite→softmax→priority), `KeywordMessageClassifier.kt`, `VoskManager.kt` (offline STT), `ICS213ReportGenerator.kt` (FEMA/NIMS ICS-213 HTML), and a 31 KB unit test.
Audit: **on-device AI, Vosk STT and ICS-213 export = implemented.** **"Priority routing" is overstated** — classification feeds `EmergencyFeedSheet`/`EmergencyMessageStyle` + a `PriorityQueueBenchmarkTest`, but `services/MessageRouter.kt` has no priority logic (it only picks BLE-mesh vs Nostr). Working alpha; **README metrics (F1 0.92, macro-F1 0.98, +16–57% survival) are unaudited.**

## 2 — ResqLink ⚠️
`/repos/njhyousha/...` → **301** to repo 1317472781 = <https://github.com/ShadowVoid-T-T/ResqLink-AI-Powered-Emergency-Response-Smart-Triage-Platform>. **`/users/njhyousha` → 404: original owner gone.** Target: TypeScript, **no licence**, 37★/1 fork, created+last push 2026-07-30, **2 commits**.
- `src/services/meshEngine.ts` self-describes as *"Mesh Networking Simulator"*; no BLE plugin in the tree, encryption is `simulateEncrypt`. **Simulated, not BLE.**
- "On-device Gemini" is **FALSE**: `aiEngine.ts` = local keyword `includes()` scoring + a **server-side Gemini proxy needing `GEMINI_API_KEY`**. First-aid guidance is a hardcoded keyword→action map. No tests, no releases.

## 3 — MeshGemma / Gemma 4 Good Hackathon
- **Gemma 4 is real**: <https://ai.google.dev/gemma/docs/core/model_card_4> — E2B, E4B, 12B, 26B A4B, 31B; E2B = 2.3B effective, 128K ctx, multimodal. Not a lineup error.
- **Competition exists**: <https://www.kaggle.com/competitions/gemma-4-good-hackathon> → **HTTP 200**, title *"The Gemma 4 Good Hackathon | Kaggle"*. Leaderboard is JS-rendered, so **winners could not be read**.
- **App exists**: <https://github.com/JasperG134/MeshGemma> — Jasper Groen & Guus Adema, Expo/React Native iOS, created 2026-05-17, **1 commit**, 4★, **CC BY 4.0** (content licence, not code). README lists tracks "Main / Impact: Global Resilience / Special Technology: llama.cpp"; the video <https://www.youtube.com/watch?v=gJu21-9NuGc> says *"Built for The Gemma 4 Good Hackathon (Google DeepMind)"*. **No evidence of a grand prize → UNVERIFIED.**
- `LocalLlamaService.ts` really runs Gemma 4 E2B GGUF (2.29 GB) + mmproj (986 MB) via llama.rn/Metal: **on-device inference + photo analysis = implemented**. Its own README: **"The BLE transport is presence-only"** (data over TCP/mDNS + MultipeerConnectivity) and radio TX is a simulated animation.

## 4 — disaster_mesh ✅/⚠️
<https://github.com/raviprasad794063/disaster_mesh> · Kotlin/Android · **MIT** · **2★** · created 2025-10-02 · last push 2026-02-05 · **10 commits, 0 releases**, ~90 files, 142 MB.
Both radios are genuinely coded: `mesh/WiFiDirectManager.kt` (13.9 KB, real `WifiP2pManager`, `ServerSocket:8888`, `_disastermesh._tcp`), `BluetoothLeManager.kt`, `MeshService.kt` (20.7 KB), plus `MeshNetworkTest.kt`/`MeshDebugger.kt`. Maturity: no CI, no test dir, no tags. **Prototype-grade real code.**

## 5 — Crisis Mesh Messenger ✅ repo / ❌ mesh
<https://github.com/FundacjaHospicjum/crisis-mesh-messenger> · Dart/Flutter · **MIT** (API says NOASSERTION) · **197★/22 forks** · created 2025-10-12 · **all 6 commits on 2025-10-12**, nothing since. `mesh_network_service.dart`: `// TODO: Implement platform-specific discovery` + `_simulatePeerDiscovery()`. **Mesh = empty scaffold**; SOS/UI screens are real. (`vrychka/crisis-mesh-messenger` is a 0-byte clone.)

## 6 — "Disaster-Resilient Mesh Network with AI Load Balancing"
RG page <https://www.researchgate.net/publication/398912234_Disaster-Resilient_Mesh_Network_with_AI_Load_Balancing> → **403, unverifiable directly**. Canonical: **DOI 10.17148/ijarcce.2025.141297**, IJARCCE **14(12), Dec 2025**, *Tejass Publishers*, ISSN 2278-1021 — authors Chaitrashree S, Bhuvaneshwari L Kinagi, Darshan Gowda A, Gaganasruti R Naidu, Davuluri Naresh (Oxford College of Eng., VTU). **Crossref: 0 references, 0 citations**; 1 hit in OpenAlex. PDF: <https://ijarcce.com/wp-content/uploads/2025/12/IJARCCE.2025.141297-Disaster.pdf> ("Impact Factor 8.471, peer-reviewed" is self-asserted — pay-to-publish outlet, **treat as predatory/unrefereed**).
Content: mentions **Random Forest + XGBoost**; **"Decision Tree" appears 0 times**; keywords say "Reinforcement Learning" but no RL exists; no dataset, no evaluation, no results — a proposal. **Reference [2] is fabricated**: cited as *"BLUEMERGENCY… arXiv:1905.02465"*, but arXiv:1905.02465 is *"Photometry… of comet C/2014 A4 (SONEAR)"*.

## 7 — Background primaries
- **BitChat**: <https://github.com/permissionlesstech/bitchat> (Swift, 36,288★, 2025-07-04, **Unlicense**, BLE mesh, max 7 hops, Noise E2E); Android: <https://github.com/permissionlesstech/bitchat-android> (Kotlin, 7,661★, GPL-3.0).
- **"Courier card rotation"** — phrase not canonical anywhere. Real mechanism = **§6.2 "Couriers", <https://github.com/permissionlesstech/bitchat/blob/main/WHITEPAPER.md>**: sealed **courier envelopes** with a **16-byte rotating recipient tag = HMAC(static key, UTC day)**, ≤3 couriers, spray-and-wait budget 4→8. The README notes the BLE mesh itself uses a *persistent* per-device ID.
- **SisFall** — Sensors 2017, DOI **10.3390/s17010198**.
- **MobiFall** — IEEE BIBE 2013, DOI **10.1109/bibe.2013.6701629**.
- **UP-Fall** — Sensors 2019, DOI **10.3390/s19091988**.
- **Trickle** — **RFC 6206** (Mar 2011): suppresses redundant flooding via redundancy constant *k*, listen-before-transmit.
- **RPL** — **RFC 6550** (Mar 2012): IPv6 distance-vector routing for LLNs over a DODAG.

## Comparables missing from the summary
| Project | URL | Licence | BLE | Store-&-fwd | Sensor-SOS | Maturity |
|---|---|---|---|---|---|---|
| bitchat | github.com/permissionlesstech/bitchat | Unlicense | **Yes** | Yes (couriers) | No | 36k★, stores |
| bitchat-android | github.com/permissionlesstech/bitchat-android | GPL-3.0 | **Yes** | Yes | No | 7.7k★ |
| Meshtastic | github.com/meshtastic/firmware | GPL-3.0 | link only | Yes (flood) | No | 8.3k★, 2020– |
| MeshCore | github.com/meshcore-dev/MeshCore | MIT | No (LoRa) | Yes (hybrid) | No | 3.7k★, 2025– |
| Briar | code.briarproject.org/briar/briar | GPL-3.0 | **Yes** | Yes (Tor) | No | high, reviewed |
| Bridgefy SDK | github.com/bridgefy/sdk-android | proprietary | **Yes** | Partial | No | commercial |
| Serval | github.com/servalproject/batphone | GPL-3.0 | **Yes** | Yes | No | **dormant (2018)** |
| qaul.net | github.com/qaul/qaul.net | AGPL-3.0 | **Yes** | Yes | No | 727★, 2014– |
| disaster.radio | github.com/sudomesh/disaster-radio | none | No (LoRa) | Yes | No | **paused** |
| Sideband/Reticulum | github.com/markqvist/Sideband | Reticulum | Yes | Yes | No | 1.8k★, active |
| ATAK-CIV | github.com/deptofdefense/AndroidTacticalAssaultKit-CIV | — | plugin | plugin | No | 494★, stale 2024 |

**Gap worth claiming:** none of these ships **sensor-triggered auto-SOS**; the SisFall/MobiFall/UP-Fall datasets are the standard route. That plus an audited offline classifier is the defensible novelty.

## Safe to cite
Repo 1 as *"an active GPL-3.0 Android bitchat-android fork adding on-device TFLite priority classification, Vosk offline STT and ICS-213 export; 469 commits, alpha"*; repo 4's BLE+Wi-Fi Direct code; BitChat + whitepaper; Meshtastic/MeshCore/Briar/Serval/qaul/Sideband/Bridgefy; all five dataset/RFC primaries; Gemma 4 model card. MeshGemma as *"a Gemma-4-E2B on-device iOS app built for the Gemma 4 Good Hackathon (Kaggle competition confirmed)"*.

## Must NOT cite
IJARCCE 10.17148/ijarcce.2025.141297 (fabricated ref [2], no evaluation, no Decision Tree); ResqLink as BLE-mesh or on-device-Gemini (browser sim + cloud proxy, unlicensed, 2 commits); Crisis Mesh Messenger as a working mesh (`_simulatePeerDiscovery()` stub); MeshGemma's "grand prize" (unverified); "courier card rotation" as a sourced term; any ResQMesh README performance number.
