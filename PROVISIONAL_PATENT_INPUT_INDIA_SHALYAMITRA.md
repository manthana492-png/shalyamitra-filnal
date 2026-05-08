# PROVISIONAL PATENT APPLICATION
## Indian Patent Office | The Patents Act, 1970

---

**TITLE OF THE INVENTION**

**SHALYAMITRA: A MULTI-MODAL, MULTI-AGENT, REAL-TIME INTRAOPERATIVE SURGICAL INTELLIGENCE SYSTEM INTEGRATING A TRIVISION THREE-CAMERA OPERATIVE ENVIRONMENT PERCEPTION ARCHITECTURE, DUAL-PATH SAFETY AUDIO ARCHITECTURE, REAL-TIME MARMA VIGYANA PROXIMITY INTELLIGENCE WITH SUSHRUTA-CITED CLASSICAL GUIDANCE, AGENTIC CLINICAL ORCHESTRATION ACROSS ELEVEN CONCURRENT INTELLIGENCE AGENTS, REAL-TIME PHARMACOKINETIC MODELLING FOR TOTAL INTRAVENOUS ANAESTHESIA, PROTECTED HEALTH INFORMATION REDACTION FOR INDIAN LEGISLATIVE CONTEXT, AND BIDIRECTIONAL CLASSICAL SHALYATANTRA TO MODERN SURGICAL KNOWLEDGE INTEGRATION**

---

**FORM 1 — APPLICATION FOR GRANT OF PATENT**

- **Applicant:** [Applicant Name/Entity to be filled by Counsel]
- **Inventor(s):** [To be declared in Statement of Inventorship]
- **Nationality:** Indian
- **Address:** [To be completed by Counsel]
- **Category of Applicant:** Natural person / Startup (as applicable)
- **International Classification (IPC):**
  - G16H 40/63 (ICT specifically adapted for medical diagnosis, medical simulation or medical data mining)
  - G16H 50/20 (ICT specially adapted for medical diagnosis, medical simulation or medical data mining; for supporting clinical decision)
  - A61B 34/00 (Surgery; Computer-assisted surgery)
  - G06F 40/56 (Speech synthesis)
  - G06V 20/50 (Image analysis for medical diagnosis)
  - G06V 10/80 (Image analysis; pattern recognition — image fusion; combining of multiple images)
  - G06N 5/04 (Inference or reasoning models — multi-agent systems)
  - A61B 5/00 (Measuring for diagnostic purposes — physiological parameter monitoring)

---

## PART I — FIELD OF THE INVENTION

The present invention relates to the field of medical informatics and intraoperative clinical decision support. More specifically, the invention provides a computer-implemented, multi-modal, multi-agent software architecture that operates in real time within an operating theatre environment, continuously integrating audio, video, physiological, pharmacological, and knowledge-base inputs to produce contextually appropriate guidance, safety alerts, and documentation outputs throughout the full duration of a surgical procedure, including pre-operative preparation and post-operative handover generation.

The invention further relates to a novel three-camera operative environment perception architecture — designated the TriVision System — comprising simultaneously processed camera streams from three distinct vantage points: a head-mounted surgeon's perspective camera for operative field analysis, a fixed camera directed at the patient physiological monitoring station for vital sign extraction, and an overhead wide-field camera for theatre-level environmental safety monitoring. The three streams are processed in parallel within a shared GPU computation graph and their outputs are fused into a unified contextual model of the operative environment.

The invention additionally relates to a novel dual-path audio signalling architecture that separates critical surgical safety alerts from conversational artificial intelligence interaction, ensuring that time-critical alerts are never delayed by conversational reasoning workloads. The invention further relates to the integration of structured classical Ayurvedic surgical corpus knowledge — specifically the doctrine of Shalyatantra and Marma Vigyana as described in the Sushruta Samhita and related classical texts — alongside contemporary surgical and pharmacological knowledge within a single unified intraoperative intelligence runtime, with real-time proximity detection of classical Marma anatomical regions and delivery of cited shloka-level guidance to the operating surgeon.

---

## PART II — BACKGROUND AND PRIOR ART

### 2.1 The Intraoperative Context Problem

A surgical operation involves simultaneous management of multiple high-stakes information streams, including but not limited to: the operative anatomical field under visual scrutiny, continuous haemodynamic and physiological monitoring, anaesthetic pharmacology and drug timelines, instrument and swab accounting, intraoperative clinical decision-making, and verbal communication within the surgical team. The surgeon is required to maintain cognitive management of all these streams simultaneously while performing physically precise manual tasks.

Existing approaches to surgical assistance address these streams in isolation:

1. Anaesthetic monitoring systems track vital signs but do not integrate this information with real-time surgical context or produce predictive trend analysis.
2. Clinical decision-support databases require the surgeon to manually query a separate system, breaking operative flow.
3. Intraoperative documentation systems record events retrospectively and require manual input.
4. Surgical robotics platforms assist with instrument mechanics but do not provide cognitive or knowledge-layer assistance to the surgeon.
5. Traditional knowledge sources — textbooks, pharmacopoeias, classical surgical texts — are not accessible in voice-activated, context-aware form during surgery.

No prior art known to the inventors provides a unified architecture that continuously integrates all of the above streams into a single, voice-controlled, predictively aware, real-time intelligence system operating for the full duration of a surgical session.

### 2.2 Deficiency of Multi-Vantage Surgical Perception

Prior art surgical video AI systems are uniformly built around a single camera stream — typically a laparoscopic or robotic endoscope feed — directed at the operative field. This single-stream approach creates three categorical blind spots: (a) physiological deterioration occurring on the monitoring display is invisible to the vision AI unless a human reads it aloud; (b) instrument and swab accounting, which requires a whole-theatre overhead view, is not supported; and (c) the environmental safety of the operating theatre as a whole — patient positioning, sterile field breaches, team positioning during prolonged procedures — is entirely outside the scope of single-camera systems.

The present invention addresses this deficiency through a three-camera TriVision architecture that assigns distinct observational roles and distinct vision pipelines to three simultaneously processed streams, providing for the first time a complete environmental model of the operating theatre that integrates close-field operative vision, physiological display vision, and theatre-level environmental awareness into a single, unified, concurrent computation.

### 2.3 Deficiency of Classical Knowledge Accessibility

The Sushruta Samhita, composed approximately 2,500 years ago, contains the world's earliest and most comprehensive documented surgical system. The doctrine of Shalyatantra — Ayurvedic surgery — includes detailed anatomical classification of Marma points, which are vital anatomical junctions whose injury causes predictable clinical consequences. The doctrine of Marma Vigyana enumerates 107 such points across the human body, classifying them by consequence of injury and prescribing protective surgical doctrines.

No prior system is known to the inventors that delivers structured, cited, real-time Marma awareness to a surgeon at the moment of operative proximity to a classical Marma point, nor that provides bidirectional translation between classical Shalyatantra terminology and modern anatomical nomenclature within an intraoperative context.

### 2.4 The Deployment Economics Problem

Prior art surgical AI systems have predominantly been designed for deployment in well-resourced tertiary hospital environments with dedicated on-premises GPU infrastructure. This creates a market gap for a system that can be deployed on commodity hardware — Android smartphones as cameras, consumer-grade Bluetooth neckbands as audio interfaces, a cloud GPU instance provisioned only for the duration of the surgery — whilst retaining the full capability set of a high-tier system.

### 2.5 The Patient Data Protection Problem

Intraoperative systems that process speech in real time inevitably encounter Protected Health Information (PHI) and Personally Identifiable Information (PII). India-specific identifiers — including Aadhaar numbers, PAN cards, ABHA health account identifiers, voter IDs, and hospital registration identifiers — require specific redaction logic that prior art systems do not address in the Indian legislative context of the Digital Personal Data Protection Act, 2023 (DPDP Act) and the National Digital Health Mission framework.

---

## PART III — OBJECTS OF THE INVENTION

The objects of the present invention include:

1. To provide a unified real-time intraoperative intelligence architecture that concurrently integrates voice, multi-camera video, physiological monitoring data, pharmacological event recording, structured knowledge retrieval, and session memory into a single operating system.

2. To provide a TriVision three-camera operative environment perception architecture comprising simultaneously processed, role-differentiated camera streams from a surgeon's head-mounted perspective, a physiological monitoring display perspective, and an overhead theatre-wide perspective, wherein the outputs of all three streams are fused into a unified contextual model of the operative environment.

3. To provide a dual-path audio output architecture wherein safety-critical surgical alerts are generated and delivered through a direct, low-latency path that is architecturally independent of any large language model inference pipeline, ensuring that critical alerts are never delayed by conversational AI processing.

4. To provide a specialised multi-agent software architecture wherein eleven distinct intelligence agents — each with a defined clinical role, event subscription, memory scope, and output channel — operate concurrently within a single session, coordinated by a shared event bus and session state store.

5. To provide real-time Marma Vigyana awareness during surgery, wherein the system computationally detects operative proximity to classical Marma anatomical regions and delivers cited, shloka-specific, Sushruta-referenced guidance — including the Marma's Sanskrit name, injury classification category, clinical consequences, and the protective operative doctrine — to the surgeon at the moment of proximity.

6. To provide a bidirectional classical-modern knowledge bridge that can translate between Shalyatantra surgical concepts and contemporary anatomical and surgical terminology in either direction, enabling a surgeon trained in either tradition to access the knowledge of the other in real time.

7. To provide an intraoperative pharmacokinetic modelling engine that computes real-time plasma and effect-site concentrations for total intravenous anaesthesia agents from voice-logged drug administration events, using established population pharmacokinetic models.

8. To provide session-level continuity from pre-operative patient analysis through intraoperative event logging to post-operative chronicle generation and structured handover brief creation, retaining full traceability of AI interventions through a Surgical Memory Cortex that accumulates the complete session history.

9. To provide a protected health information redaction engine specifically designed for the Indian regulatory context, recognising Indian national identifiers, health account numbers, and hospital registration identifiers.

10. To provide a cross-agent safety challenge mechanism that monitors for logical conflicts between agent states at surgical decision points and surfaces a single confirmatory query to the surgeon without blocking or delaying the decision.

11. To provide a surgeon-adaptive voice companion that builds a persistent profile of each surgeon's linguistic preferences, interaction rhythm, and informational needs over successive surgical sessions.

12. To provide a deployment-flexible architecture that operates across a range of compute profiles, from cloud GPU instances provisioned per surgery to local on-premises configurations, without requiring changes to the core inventive architecture.

---

## PART IV — STATEMENT OF THE INVENTION

In one aspect, the present invention provides a computer-implemented intraoperative surgical intelligence system comprising:

a multimodal input subsystem configured to receive concurrent audio streams from one or more voice input devices worn by operative personnel, and concurrent video streams from three cameras in a TriVision configuration, each camera assigned a distinct observational role within the operating theatre;

a TriVision three-camera operative environment perception subsystem comprising: (i) a first camera mounted on or proximate to the surgeon's head, providing a perspective of the operative field and processing through an anatomical recognition, haemorrhage detection, tissue stress monitoring, and Marma proximity detection pipeline; (ii) a second camera fixed with a direct view of the patient physiological monitoring display, processing through a perspective correction, region-of-interest detection, and optical character recognition pipeline to extract vital sign values in real time; and (iii) a third camera mounted overhead with a wide-field view of the operative theatre environment, processing through an object detection, multi-object tracking, and sterile field monitoring pipeline for instrument, swab, and environmental safety accounting; wherein all three camera streams are processed concurrently within a shared GPU computation graph and their outputs are fused into a unified contextual model of the operative environment;

a real-time transport subsystem implementing a WebRTC-based selective forwarding architecture for routing audio and video streams between physical devices in the operating theatre and a compute environment;

a multi-agent orchestration subsystem comprising a plurality of software agents, each agent assigned to a specific clinical intelligence role, wherein each agent subscribes to relevant event types on a shared event bus, maintains agent-specific persistent memory scoped to the current surgical session, and publishes events or output actions in response to received inputs;

a dual-path audio output subsystem comprising a first conversational path configured to process voice queries through speech recognition, language model inference, and neural text-to-speech synthesis, and a second critical alert path configured to deliver safety alerts directly from classifier outputs to audio output without language model involvement, wherein the second path is latency-constrained to below five hundred milliseconds end-to-end;

a Marma Vigyana intelligence subsystem configured to detect operative proximity to classical Ayurvedic Marma anatomical regions through analysis of the TriVision operative field stream, query a structured citation-preserving Shalyatantra corpus, and deliver to the surgeon a response comprising the Marma's Sanskrit name, its injury classification under the fivefold Sushruta system, the clinical consequences of injury, the protective operative doctrine, and the specific shloka citation including chapter and verse reference from the Sushruta Samhita;

a knowledge retrieval subsystem comprising a vector database populated with embeddings of a modern clinical knowledge corpus and a structured classical Ayurvedic surgical corpus, wherein retrieval is performed by semantic similarity search and contextual reranking;

a pharmacokinetic modelling subsystem implementing one or more population pharmacokinetic models for anaesthetic agents, configured to receive drug administration events logged by voice and compute real-time predicted plasma and effect-site concentrations;

a protected health information redaction subsystem configured to identify and redact PHI categories specific to the Indian legislative context from transcript and report data prior to storage or transmission;

a session continuity subsystem maintaining a comprehensive event log throughout the surgical session within a Surgical Memory Cortex, and generating structured post-operative chronicle and handover outputs upon session closure;

wherein the system is configured to operate for the complete duration of a surgical procedure from pre-operative preparation through post-operative handover, maintaining full contextual continuity without session resets.

---

## PART V — SUMMARY OF THE INVENTION

The present disclosure describes ShalyaMitra, a software system that functions as an AI co-presence in the operating theatre. The system perceives the operative environment through a TriVision three-camera architecture and voice audio, reasons over this input using eleven specialised software agents, retrieves from both modern clinical and classical Ayurvedic surgical knowledge, models anaesthetic pharmacokinetics in real time, protects patient data through an Indian-context PHI redaction engine, and generates structured post-operative documentation automatically.

The primary architectural innovation is the TriVision three-camera operative environment perception system. Prior art surgical AI systems use a single camera stream. The present invention uses three simultaneously processed streams from three distinct vantage points — a head-mounted surgeon's perspective camera for operative field analysis and Marma proximity detection, a fixed camera pointed at the physiological monitoring display for real-time vital sign extraction without any hardware integration requirement, and an overhead wide-field camera for instrument, swab, and environmental safety monitoring. Each stream is processed by a dedicated vision pipeline tailored to the observational role of that camera. All three pipeline outputs are fused into a single contextual model that integrates what the surgeon sees, what the patient's monitors show, and what is happening across the theatre environment as a whole. This three-stream contextual fusion is a defining architectural novelty of the present invention.

The secondary architectural innovation is the separation of two audio output paths. In prior art systems, safety alerts and conversational responses are generated through the same pipeline. In the present invention, safety alerts — particularly haemorrhage detection, physiological deterioration trajectories, retraction injury thresholds, and instrument/swab count discrepancies — are delivered through a direct path that never enters a language model inference queue. This eliminates the risk that a conversational query being processed at the time of an emergency event could delay the alert.

The tertiary architectural innovation is the cross-agent conflict detection mechanism, implemented as a specialised agent that continuously monitors the outputs of all other agents and flags logical conflicts at decision points. This agent never makes clinical decisions; it asks a single confirmatory question when a conflict is detected, and accepts the clinician's confirmation without repetition.

The quaternary innovation is the real-time Marma Vigyana intelligence system — the first known intraoperative system to computationally detect operative proximity to a classical Ayurvedic Marma anatomical region and deliver cited, shloka-level guidance from the Sushruta Samhita to the operating surgeon at the moment of proximity. The Marma intelligence subsystem is paired with a bidirectional Shalyatantra-modern surgical knowledge bridge, enabling a surgeon to query in modern surgical terms and receive classical Sushruta references, or to query in classical Ayurvedic terms and receive modern anatomical correlates.

---

## PART VI-A — BRIEF DESCRIPTION OF DRAWINGS

The following drawings are referred to in the detailed description and are to be prepared for Annexure A before complete specification filing:

**Figure 1 — System Architecture Overview:** Block diagram showing the complete ShalyaMitra architecture, including the TriVision camera subsystem, the dual-path audio architecture, the eleven-agent orchestration subsystem, the knowledge retrieval subsystem, the Surgical Memory Cortex, and the theatre display, with interconnections through the event bus.

**Figure 2 — TriVision Camera Configuration:** Schematic diagram of the operating theatre showing the physical positioning of all three TriVision cameras — the head-mounted Surgeon's Eye camera, the fixed Monitor Sentinel camera, and the overhead Sentinel camera — with their respective fields of view, the target surfaces observed, and the vision pipeline assigned to each.

**Figure 3 — TriVision Vision Pipeline Architecture:** Detailed block diagram of all three camera vision pipelines operating in parallel within the shared GPU computation graph, showing the processing stages of each pipeline and the TriVision contextual fusion model that aggregates their outputs.

**Figure 4 — Dual-Path Audio Architecture:** Signal flow diagram contrasting the critical alert path (classifier → alert generator → audio output, sub-500ms) with the conversational path (audio input → ASR → wake-word gate → intent classifier → LLM inference → TTS → audio output), showing the independence of the two paths and the priority preemption mechanism.

**Figure 5 — Eleven-Agent Orchestration Architecture:** Block diagram of all eleven intelligence agents, their event subscriptions, their memory scopes, their output channels, and their interconnection through the shared event bus and the Surgical Memory Cortex.

**Figure 6 — Marma Vigyana Proximity Detection System:** Diagram illustrating the Marma proximity detection algorithm, showing the mapping from the TriVision anatomical structure recognition output to the Marma anatomical coordinate database, the proximity score computation, and the Oracle guidance delivery flow. Includes a representative Marma body-region distribution diagram based on the Sushruta Samhita Sharirasthana classification.

**Figure 7 — Session Lifecycle Architecture:** Timeline diagram of the complete session lifecycle from pre-operative Scholar analysis initialisation through session startup, intraoperative execution, and post-operative Chronicler output, showing the continuous Surgical Memory Cortex accumulation and the session termination sequence.

**Figure 8 — PHI Redaction and Privacy Routing Architecture:** Data flow diagram showing the PHI redaction engine processing transcripts and documents, the privacy routing decision logic for local versus cloud language model selection, and the agent security sandbox boundaries.

---

## PART VI — DETAILED DESCRIPTION OF THE INVENTION

### 6.1 System Overview and Operating Environment

The invention is deployed in an operating theatre environment and operates continuously for the duration of a surgical procedure. The physical environment comprises:

- one or more voice input devices (Bluetooth audio neckbands with active noise cancellation) worn by the surgeon and/or anaesthesiologist;
- three cameras with distinct observational roles: a head-mounted camera worn by the surgeon (the Surgeon's Eye), a fixed camera directed at the patient monitoring station (the Monitor Sentinel), and an overhead camera observing the overall theatre environment (the Sentinel);
- one or more audio output channels (Bluetooth earpiece and/or operating theatre speakers) through which the system delivers spoken guidance and alerts;
- a theatre display device (smart television, large monitor, or tablet) positioned for visibility to the surgical team;
- a compute environment comprising a central processing unit, a graphics processing unit, a vector database instance, an in-memory data store, and network connectivity.

The compute environment is configured as a surgery-time provision: a GPU instance is spun up prior to the surgical session, all services are deployed and health-checked, the session runs, and the instance is terminated at session close, with all session data encrypted and archived to persistent cloud storage. This per-surgery provisioning model enables cost-efficient deployment across a range of hospital resource levels.

All audio and video streams are transported between physical devices and the compute environment using a WebRTC selective forwarding protocol with encrypted transport (DTLS-SRTP). The real-time transport subsystem manages all stream connections, handles automatic reconnection on network interruption, and coordinates participant roles within the session.

### 6.2 Session Lifecycle Architecture

The session lifecycle is structured as a continuous, unbroken computational thread from pre-operative initialisation to post-operative closure. The lifecycle proceeds as follows:

**Pre-operative phase:** The clinical team uploads the patient's investigation portfolio — comprising imaging reports, laboratory results, operative history, comorbidity documentation, current medication lists, allergy records, and any specialist consultation summaries — through a secure web interface. The Scholar agent processes this portfolio, synthesising it into a structured Master Pre-Operative Analysis. This analysis identifies anatomical deviation flags, critical pre-operative risk markers, drug interaction concerns, calculated surgical risk scores (including ASA classification, Revised Cardiac Risk Index, and renal and pulmonary risk indices), and a classical Ayurvedic clinical assessment including Prakriti constitution and Dosha analysis where applicable. The Scholar agent's output becomes the shared clinical foundation for all other agents during the surgery.

**Session initialisation:** All service containers are started and health-checked. The event bus is initialised. All eleven agents are registered and their session contexts are reset to empty. The Surgical Memory Cortex — a session-scoped persistent memory object — is instantiated. Devices join the session: cameras and audio neckbands connect through the real-time transport layer, and the theatre display joins as a subscriber. When all devices are confirmed connected, the system announces readiness through the primary audio channel.

**Intraoperative phase:** All agents operate concurrently. Events flow through the shared event bus with type, source, session identifier, priority, and data payload. Agents subscribe to relevant event types and dispatch response events. The Surgical Memory Cortex accumulates a complete timestamped log of all significant events. The session operates without pause or reset for the entire surgical duration, which may range from thirty minutes to eight hours.

**Closure and post-operative phase:** When the surgeon indicates session completion, the Chronicler agent synthesises the complete session memory into a structured Intraoperative Chronicle and a Handover Brief. These documents are finalised, stored, and made available before the patient leaves the operating theatre. The GPU session is then terminated.

### 6.3 The Eleven Agent Architecture

The multi-agent orchestration subsystem comprises eleven software agents, each implemented as a class inheriting from a common base agent abstraction. Each agent registers its event subscriptions with the orchestrator at startup, is invoked asynchronously when matching events arrive, maintains its own session-scoped memory, and publishes output events back to the bus. The agents are:

**Agent 1 — The Voice (Nael):** The primary conversational agent. Receives transcribed speech after wake-word detection. Performs intent classification to distinguish direct questions, display commands, session control commands, and drug logging instructions. Routes queries to appropriate specialist agents and synthesises responses. Delivers spoken responses through the conversational text-to-speech path. Maintains a continuous contextual memory of the full conversation history. Builds a persistent Surgeon Profile across successive sessions, adapting its interaction style, detail level, and proactive behaviour to the individual surgeon over time.

**Agent 2 — The Monitor Sentinel:** Processes vital sign readings extracted from the patient monitoring display camera. Maintains a continuous time-series of all vital parameters since session start. Computes trend trajectories and rate-of-change derivatives. Runs a forward-prediction model projecting parameter trajectories over an eight to twelve minute window. Issues predictive alerts through the critical path when a trajectory is projected to breach clinically significant thresholds, providing the surgical team with anticipatory awareness rather than reactive threshold-crossing notifications.

**Agent 3 — The Haemorrhage Sentinel:** Processes the operative field camera stream through a dedicated bleeding pattern classifier. Analyses field colour distribution, pulsatility patterns, and rate of field filling. On detection of a bleeding pattern inconsistent with the current operative phase, immediately dispatches a critical alert to the critical audio path. This agent's alert path bypasses all language model processing. The time from classifier trigger to audio delivery is designed to fall within the range of human pre-conscious visual registration, providing detection that complements rather than lags visual awareness.

**Agent 4 — The Sentinel (Overhead):** Processes the overhead camera stream. Maintains a running inventory of all surgical instruments and swabs from first deployment to current frame, using object detection and multi-object tracking. At the commencement of wound closure, performs a final reconciliation and announces the count result — either confirming all instruments and swabs are accounted for, or issuing a count discrepancy alert through the critical path. Additionally monitors team positioning relative to the sterile field, patient positioning shifts during prolonged procedures, and overall operative environment safety.

**Agent 5 — The Surgeon's Eye:** Processes the head-mounted camera stream. Performs anatomical structure recognition on the operative field, identifying visible structures and their relationships. When operating in anatomical regions of Marma significance, queries the Oracle agent for relevant classical guidance. Detects operative phase from visual observation alone, allowing all other agents to contextualise their behaviour without explicit phase announcements from the surgical team. Supports point-and-query interactions where the surgeon identifies a structure by pointing or spatial description.

**Agent 6 — The Scholar:** Pre-operative intelligence agent. Processes the uploaded patient investigation portfolio using deep language model reasoning. Generates the Master Pre-Operative Analysis described above. During the surgical session, remains as a shared reference: any agent may query the Scholar for patient-specific clinical facts, and the Voice agent exposes Scholar data to the surgeon through conversational queries.

**Agent 7 — The Pharmacist:** Anaesthesia-dedicated intelligence agent operating on a separate communication channel directed to the anaesthesiologist. Passively listens to the anaesthesiologist's voice channel and logs drug administration events — drug name, dose, route, and timestamp — from natural speech without requiring structured input. Runs population pharmacokinetic models for anaesthetic agents in real time, computing predicted plasma concentration and effect-site concentration. Delivers pharmacological guidance, dose calculation, drug interaction alerts, and timing intelligence to the anaesthesiologist through a dedicated voice profile distinct from the primary Voice agent. The anaesthesiologist's communication channel and the surgeon's conversation are parallel, simultaneous, and non-interfering.

**Agent 8 — The Oracle:** Classical Ayurvedic surgical knowledge intelligence. Maintains structured access to the complete encoded Shalyatantra corpus — including the Sushruta Samhita, Ashtanga Hridayam, Charaka Samhita surgical sections, Sharangadhara Samhita, and the commentaries of Vagbhata and Dhanvantari — through a vector-indexed knowledge graph with citation-preserving retrieval. The Marma knowledge base encodes all 107 classical Marma points with their Sanskrit names, anatomical extents, injury classifications (Sadya Pranahara, Kalantara Pranahara, Vishalyaghna, Vaikalyakara, and Rujakara), operative consequences, and protective doctrines. Every Oracle output carries a specific shloka citation with chapter and verse reference. The Oracle operates bidirectionally: a classical query receives a modern anatomical correlate; a modern surgical query receives the closest classical parallel from the corpus. This bidirectional mapping capability is unique to the present invention.

**Agent 9 — The Consultant:** Deep clinical knowledge agent. Provides access to modern surgical anatomy, pharmacology, emergency management protocols, and evidence-based guidelines through retrieval-augmented generation over a broad medical knowledge base. The Consultant responds to complex clinical queries that require knowledge beyond the scope of any single specialist agent.

**Agent 10 — The Devil's Advocate:** Cross-agent safety challenge agent. Operates with no external network access. Continuously monitors the state of all other agents — the Scholar's pre-operative risk flags, the Pharmacist's drug record, the Monitor Sentinel's physiological trend, and the conversational context in the Voice agent. When the Voice agent is processing a clinical decision — a request to proceed with a surgical step, a drug dose confirmation, or a management decision — the Devil's Advocate checks that decision against all current agent states for logical conflicts. If no conflict is present, the decision proceeds without comment. If a meaningful conflict is identified, the Devil's Advocate generates a single, factual, non-obstructing confirmation query that is delivered alongside the normal response. The agent never argues, never repeats, and accepts the surgeon's confirmation as final. This mechanism is designed to prevent the category of surgical harm caused by intraoperative cognitive groupthink: the most dangerous surgical moments are not those of alarm, but those of unchallenged consensus at decision points.

**Agent 11 — The Chronicler:** Session memory and documentation agent. Operates continuously throughout the session, accumulating the full event log, timestamped conversation history, vital trends, drug record, vision events, alert history, and Oracle consultation records. At session closure, synthesises this accumulated record into two documents: an Intraoperative Chronicle (a complete structured operative record) and a Handover Brief (a receiving-team-oriented summary calibrated to the clinical role of the recipient — recovery nurse, intensive care team, or ward team). The Handover Brief is generated and available before the patient leaves the operating theatre, eliminating human memory as a variable in post-operative information transmission. The Chronicler's records also form the basis of an optional research archive, governed by patient and surgeon consent frameworks.

### 6.4 Dual-Path Audio Architecture

This is the most architecturally significant innovation of the present disclosure.

All prior art conversational medical AI systems route all audio output through the same pipeline: speech recognition, language model inference, and speech synthesis. In safety-critical environments, this creates a hazard: if the system is processing a conversational query when a safety-critical event occurs, the safety alert may be queued behind the conversational response, delaying its delivery by one to three seconds.

The present invention implements two entirely separate, simultaneously operating audio output paths:

**Critical Alert Path:** This path is activated by direct classifier outputs — the haemorrhage classification model, the vital sign trend engine, the retraction timer, and the instrument count reconciliation. It never enters the language model inference queue. Alerts are either pre-generated audio files stored at session initialisation and played back on trigger, or synthesised in real time using a lightweight neural text-to-speech engine operating on CPU with sub-fifty millisecond synthesis latency. The end-to-end time from classifier output to audio delivery through this path is designed to fall below five hundred milliseconds.

**Conversational Path:** This path processes wake-word-activated queries from the surgeon. It routes through speech recognition, intent classification, language model reasoning with retrieval augmentation, and neural text-to-speech synthesis. The end-to-end latency of this path, which encompasses transcription, reasoning, and speech synthesis, is designed to fall below two seconds for short clinical responses.

A critical architectural rule governs these two paths: critical alerts are never blocked or delayed by conversational path activity. If the surgeon is mid-conversation with the Oracle about a classical Marma doctrine, and the Haemorrhage Sentinel simultaneously detects a bleeding pattern, the haemorrhage alert interrupts without queue and is delivered within its latency budget. Both paths operate simultaneously and independently in all system states.

### 6.5 Wake-Word Architecture

The conversational path is activated by the wake word "Nael", which is the given name of the primary Voice agent. This design reflects the surgical social environment: in an operating theatre, the surgeon speaks continuously to team members by name. A wake-word-based system eliminates the need for intent classification to distinguish AI-addressed speech from team-addressed speech. When the surgeon addresses the team, they use human names. When they address the AI, they say "Nael".

Wake word detection is implemented across three tiers:

- Tier one: hardware-level keyword spotting on the GPU audio inference pipeline, operating on the raw audio stream with detection latency below one hundred milliseconds;
- Tier two: lightweight neural keyword detection on CPU as a backup, operating in parallel with sub-two-hundred millisecond detection latency;
- Tier three: text-pattern matching on the speech recognition transcript as a universal fallback with high precision at the cost of the full speech recognition latency.

Upon wake-word detection, the system captures the following speech phrase and routes it to the conversational path. The system returns to wake-word-only listening after the response is delivered. Safety alerts are never gated by the wake word and fire immediately on classifier trigger, regardless of the conversational state.

A secondary channel for the anaesthesiologist operates in a passive always-on mode, capturing drug administration events from natural speech without requiring wake-word invocation, since drug logging is a passive recording function rather than a query-response interaction.

### 6.6 TriVision Three-Camera Operative Environment Perception System

The TriVision system is the primary perceptual architecture of the invention and constitutes one of its most significant technical novelties. It provides a complete three-dimensional environmental model of the operating theatre by simultaneously processing three role-differentiated camera streams, each assigned a distinct observational vantage point, a distinct computer vision pipeline, and a distinct set of intelligence consumers. All three streams are processed concurrently within a shared GPU computation graph using memory-mapped frame buffers to avoid redundant data copies between processes.

The three cameras are designated: the Surgeon's Eye (head-mounted operative field camera), the Monitor Sentinel (physiological display camera), and the Overhead Sentinel (theatre-wide overhead camera). Together they provide a perceptual coverage that no single-camera surgical AI system achieves: the intimate operative field, the patient's physiological state as displayed on monitoring equipment, and the complete theatre environment including all personnel, instruments, and sterile field boundaries.

#### 6.6.1 The Surgeon's Eye — Head-Mounted Operative Field Camera

The first TriVision camera is a compact wide-angle camera mounted on the surgeon's headwear or loupes, oriented to capture the operative field from the surgeon's first-person perspective. This mounting position ensures that the camera sees exactly what the surgeon's eyes see, with minimal parallax, providing the most clinically accurate view of the anatomical structures being operated upon.

The Surgeon's Eye vision pipeline comprises the following sequential and parallel stages:

**Surgical Scene Segmentation:** Each incoming frame undergoes semantic segmentation to partition the visible scene into tissue classes, instrument classes, and background regions. The segmentation model is trained on annotated surgical video data and is capable of distinguishing different tissue types (fascia, muscle, fat, nerve, vessel, organ capsule), active versus idle instruments, and the boundary of the operative field.

**Anatomical Structure Recognition:** An open-set anatomical recognition module applies region-level classification across the segmented frame to identify named anatomical structures where they are visible, and to track their positions across frames. The output is a spatial map of recognised anatomical entities within the current field of view.

**Haemorrhage Pattern Classifier:** A dedicated bleeding pattern classification model operates on every frame, analysing colour distribution shifts toward the haemorrhage spectrum (dark red, arterial red, venous dark), spatial distribution patterns of colour change (localised versus field-flooding), and temporal dynamics of colour change rate. This classifier is trained to distinguish active bleeding from the normal appearance of incised tissue. On positive detection above a configurable confidence threshold, a haemorrhage event is immediately dispatched to the critical alert path without any language model involvement.

**Tissue Stress Monitor:** A retractor detection and tissue stress monitoring module operates concurrently with the haemorrhage classifier. This module detects the presence and position of tissue retractors in the frame, determines which tissue structures are being retracted, and initiates a duration timer from the moment of retractor engagement. Prolonged retraction of vascular, neural, or visceral tissue beyond established ischaemia thresholds triggers a progressive alert sequence: a first advisory alert at the approach of the safe retraction window, and a critical alert at the boundary of the window. The alert text specifies the retracted structure and the elapsed retraction duration, enabling the surgeon to either release retraction or make a conscious informed decision to continue.

**Marma Proximity Detection:** The Marma proximity detection module continuously evaluates the anatomical structure map against the Marma anatomical coordinate database. Each of the 107 classical Marma points is encoded with an anatomical region descriptor, a depth profile from surface landmarks, and a proximity radius within which operative activity should trigger a Marma advisory. When the instrument position or the active dissection zone enters the proximity radius of a Marma point, the module queries the Oracle agent for the relevant Marma guidance package, which is then delivered to the surgeon through the conversational path with simultaneous display on the theatre screen.

**Operative Phase Detection:** A phase classification model analyses the cumulative frame sequence and the visible instrumentation to classify the current operative phase — incision, exposure, dissection, haemostasis, anastomosis or repair, closure, or wound management. This phase estimate is broadcast on the event bus and is used by all agents to contextualise their outputs and suppress out-of-phase proactive messaging.

#### 6.6.2 The Monitor Sentinel — Physiological Display Camera

The second TriVision camera is a fixed camera positioned with a direct, unobstructed view of the primary patient physiological monitoring display used by the anaesthetic team. This design choice is a key architectural innovation: rather than requiring hardware-level integration with proprietary monitoring equipment (which varies by manufacturer, hospital, and vintage), the system instead reads the monitoring display visually — the same way a human clinician reads it — through optical character recognition applied to the camera feed. This approach is compatible with any monitoring equipment in any operating theatre with no integration requirements.

The Monitor Sentinel vision pipeline operates as follows:

**Perspective Correction and Stabilisation:** On session initialisation, the pipeline performs automatic perspective calibration on the first frames, correcting for the angle and distance of the camera relative to the display surface. A projective transform is computed and applied to all subsequent frames, producing a rectified, screen-parallel view of the monitoring display.

**Region-of-Interest Detection:** The rectified display frame is analysed to automatically identify the positions of individual parameter readout panels — heart rate, non-invasive blood pressure, arterial line pressure, peripheral oxygen saturation, end-tidal carbon dioxide, respiratory rate, temperature, and anaesthetic agent concentration. Region-of-interest boundaries are established at session start and tracked with adaptive boundary adjustment as the display layout changes.

**Optical Character Recognition and Value Extraction:** Within each identified region of interest, a high-accuracy OCR pipeline extracts the numerical value and its associated unit label, applying digit-pattern correction specific to seven-segment LED and LCD display fonts. Values are validated against physiological plausibility ranges and flagged if extracted values are outside those ranges, triggering a re-read from the following frame.

**Time-Series Construction:** Validated numerical values are timestamped and appended to the Monitor Sentinel agent's per-parameter time-series data structure at approximately thirty readings per second. This produces a continuously updated, high-frequency vital sign record from camera vision alone, without any equipment integration.

**Trend Prediction:** The Monitor Sentinel agent applies a forward-projection model to each parameter's time-series, computing the first and second derivatives of the trend and projecting the parameter trajectory over an eight to twelve minute horizon. When a trajectory is projected to breach a clinically significant threshold before it actually reaches it, a predictive advisory is issued through the critical alert path, giving the anaesthetic team anticipatory awareness. This predictive alerting — warning of a trend before it becomes a threshold violation — distinguishes this system from all prior art threshold-alarm systems.

#### 6.6.3 The Overhead Sentinel — Theatre-Wide Environmental Camera

The third TriVision camera is mounted overhead, typically on the operating theatre light track or ceiling, oriented downward and outward to capture the entire operative theatre floor, table, and instrument trolley arrangement in a single wide-field frame.

The Overhead Sentinel vision pipeline operates as follows:

**Instrument and Swab Detection and Tracking:** A surgical instrument and swab detection model applies frame-by-frame object detection followed by multi-object tracking across successive frames. Each instrument is detected, classified by type (scalpel, forceps, retractor, haemostat, needle holder, suction, diathermy pen, and others), and assigned a persistent tracking identity. Each swab (gauze, pack, and laparotomy pad) is detected and tracked. From the moment a new instrument or swab enters the frame for the first time — typically at deployment from the instrument trolley — it is added to the session inventory with a timestamp. Instruments and swabs are removed from the active count when the tracker confirms they have left the operative field and been returned to the trolley count.

**Instrument Count Reconciliation at Closure:** When the operative phase classifier signals the commencement of wound closure, the Overhead Sentinel performs a final reconciliation of all instruments and swabs against the session inventory. If all items are accounted for, the system announces through the critical alert path: "Instrument and swab count confirmed correct." If a discrepancy is detected, an immediate critical alert is issued specifying the missing item type and the last known frame in which it was tracked, providing the surgical team with actionable information for retrieval.

**Sterile Field Monitoring:** The Overhead Sentinel applies a sterile field boundary model that delineates the drape-defined sterile zone from the non-sterile zone. Incursions of un-gowned personnel or unsterile items into the sterile zone trigger an advisory alert. This monitoring is particularly relevant for teaching cases involving trainees and observers.

**Patient Positioning Monitoring:** During prolonged surgical procedures, the patient's position on the table may shift under the forces of retraction and manipulation. The Overhead Sentinel monitors the patient's positional landmarks at intervals and issues an advisory if a significant position shift is detected, enabling the team to reassess table position before it causes unintended anatomical distortion.

#### 6.6.4 TriVision Contextual Fusion

The outputs of all three TriVision pipelines are continuously fused into a Unified Theatre Context Model that is available to all agents on the event bus. The context model provides:

- the current anatomical structure map and instrument position from the Surgeon's Eye;
- the current vital sign values, trends, and projections from the Monitor Sentinel;
- the current instrument and swab inventory, sterile field status, and patient positioning data from the Overhead Sentinel;
- the current operative phase estimate, updated by both the Surgeon's Eye phase classifier and anatomical context;
- the active Marma proximity state for the current operative region.

This fused context model is the shared situational awareness substrate on which all eleven agents reason. Each agent queries the aspect of the context model relevant to its clinical role. No agent receives raw camera frames; all agents receive structured, processed, semantically labelled contextual data. This architecture ensures that camera processing and agent reasoning are cleanly separated, and that camera pipeline failures are contained without affecting agent operation.

### 6.7 Tissue Stress Monitor

The Tissue Stress Monitor is a dedicated safety subsystem operating on the Surgeon's Eye stream, focused specifically on the risk of tissue injury from sustained mechanical stress during retraction, the most common cause of inadvertent intraoperative tissue damage that does not involve direct cutting or cauterisation.

Tissue retraction is a necessary part of all open and laparoscopic surgery — structures must be moved aside to expose the operative target. However, sustained retraction of neural, vascular, and visceral structures beyond established physiological tolerance windows causes ischaemia, neuropraxia, avulsion, and other preventable injuries. In current practice, tracking retraction duration is entirely dependent on the surgeon's unaided memory, which is simultaneously occupied with the primary operative task.

The Tissue Stress Monitor implements the following logic:

**Retractor Detection:** On first appearance of a retractor instrument engaging tissue in the Surgeon's Eye frame, the module identifies the tissue class being retracted from the segmentation output, the retractor type (blunt, sharp, self-retaining, handheld), and the anatomical region of retraction.

**Duration Timer:** A per-retractor timer is initiated from the moment of engagement. If a retractor is repositioned and re-engaged, the timer records cumulative engagement time for that tissue region within the session.

**Progressive Alert Cascade:** The alert cascade is calibrated to the identified tissue class. For neural structures, the primary advisory fires at four minutes of continuous retraction, and the critical alert fires at eight minutes. For bowel and visceral structures, the advisory fires at fifteen minutes and the critical alert at thirty minutes. For vascular pedicles, shorter windows apply. These thresholds are configurable and based on published operative safety literature.

**Alert Content:** All Tissue Stress Monitor alerts carry: the tissue class being retracted, the retraction duration, and a brief protective doctrine ("Consider releasing neural retraction and allowing perfusion recovery before continuing.").

### 6.8 Pharmacokinetic Engine

The invention implements a deterministic, CPU-resident pharmacokinetic modelling engine operating in real time alongside the anaesthetic documentation function. The engine is not implemented using machine learning inference but through established population pharmacokinetic model mathematics:

For propofol: the Marsh three-compartment model and the Schnider three-compartment model are implemented as selectable options. The Schnider model incorporates patient weight, height, age, and lean body mass. Both models compute predicted plasma concentration and predicted effect-site concentration at every simulation step.

For remifentanil: the Minto model is implemented, incorporating patient age and lean body mass.

For other anaesthetic infusion agents: appropriate published population pharmacokinetic models are implemented where clinical consensus models exist.

The engine receives patient demographic data from the Scholar agent's pre-operative record and drug administration events from the Pharmacist agent's voice-logged record. It outputs continuously updated plasma and effect-site concentration curves to the theatre display and provides verbal alerts through the Pharmacist agent when infusion parameters approach pharmacologically significant thresholds, including projected time to emergence from anaesthesia.

This pharmacokinetic intelligence function makes available to anaesthesiologists in district-level hospitals the same real-time pharmacokinetic modelling that is otherwise accessible only through proprietary target-controlled infusion workstations costing several million rupees.

### 6.9 Shalyatantra and Marma Vigyana Intelligence System

This subsystem constitutes the most historically and intellectually distinctive component of the present invention. It is, to the inventors' best knowledge, the first real-time computational implementation of classical Ayurvedic surgical intelligence within an intraoperative clinical system.

#### 6.9.1 The Classical Corpus

The Shalyatantra corpus encoded in the present invention is a structured, citation-preserving, vector-indexed knowledge base encompassing the following primary and secondary classical sources:

- the complete Sushruta Samhita, all six Sthanas (Sutrasthana, Nidanasthana, Sharirasthana, Chikitsasthana, Kalpasthana, and Uttarasthana), with all shloka texts preserved in Sanskrit with Devanagari script, Roman transliteration, and clinical commentary;
- the Ashtanga Hridayam (Vagbhata), surgical and anatomical sections;
- the Charaka Samhita, Sharirasthana and Chikitsasthana, surgical passages;
- the Sharangadhara Samhita, surgical instrument and material sections;
- the Dhanvantari Nighantu, materia medica and operative plant preparations;
- the commentaries of Dalhana on the Sushruta Samhita;
- and modern scholarly annotations from classical studies literature mapping classical terminology to contemporary anatomical nomenclature.

Every piece of content in this corpus is stored with full citation metadata: source text, Sthana, Adhyaya (chapter) number, Shloka number, and the name of the commentary where applicable. This citation-preserving architecture means that every Oracle agent output is traceable to a specific verse in a specific classical text. The system never generates classical guidance from paraphrase; it retrieves encoded shlokas and their vetted commentary. This design decision was made deliberately to prevent the system from generating pseudo-classical content and to ensure scholarly accuracy and intellectual honesty in every Oracle output.

#### 6.9.2 The Marma Knowledge Database

The Marma knowledge database is a structured relational record encoding all 107 classical Marma points as defined in the Sushruta Samhita Sharirasthana. Each record contains:

**Sanskrit Identity:** The classical Sanskrit name of the Marma point in Devanagari and Roman transliteration, alternate names as used in different classical sources, and the etymological meaning of the name where relevant to clinical understanding.

**Anatomical Description:** The classical anatomical location description as given in the Sushruta Samhita, expressed in classical topographic terms (measured in Angulas from named surface landmarks), alongside the modern anatomical correlate expressed in contemporary nomenclature — the equivalent anatomical structure, approximate vertebral level or surface landmark reference, and the relevant regional anatomy.

**Dimensional Extent:** The classical measurement of the Marma's extent (Angula measurements from the Sushruta description) alongside a millimetre-range estimate based on the best available modern anatomical mapping.

**Injury Classification:** The fivefold Sushruta injury classification:
- *Sadya Pranahara* (immediately life-threatening): injury causes immediate death. Nineteen Marma points fall in this category, corresponding anatomically to structures whose acute injury is universally fatal — major intracranial vessels, cervical cord, major thoracic vessels.
- *Kalantara Pranahara* (delayed life-threatening): injury causes death within a defined period (described in classical texts in terms of days to a fortnight). Thirty-three Marma points are in this category, corresponding anatomically to structures whose injury causes progressive, fatal secondary complications.
- *Vishalyaghna* (fatal on instrument withdrawal): the injury itself is compatible with survival, but removal of a lodged instrument from the Marma causes immediate death. Three Marma points are in this category, correlating with anatomical regions where instrument extraction before haemorrhage control is catastrophic.
- *Vaikalyakara* (permanently disabling): injury does not kill but causes permanent functional disability. Forty-four Marma points are in this category, corresponding to major peripheral nerves, joints, and sensory organs.
- *Rujakara* (painful only): injury causes severe pain without permanent consequence. Eight Marma points are in this category.

**Body Region Distribution:** The 107 Marma points are distributed anatomically as follows: eleven in each arm and leg (forty-four in the four limbs), twelve in the trunk, fourteen in the back, thirty-seven in the head and neck. The Marma knowledge database encodes the regional groupings for both classical reference and operative proximity detection purposes.

**Operative Consequence:** A structured clinical description of the consequences of surgical injury to each Marma, translated from the classical description into contemporary clinical language, specifying the presenting signs, the timeline of consequence, and the clinical severity.

**Protective Doctrine:** The classical operative guidance for each Marma — the surgical approach modifications, instrument orientation, dissection technique adjustments, and post-operative monitoring requirements that classical Shalyatantra prescribes for operating in proximity to that Marma.

**Shloka Citations:** The primary shloka references from the Sushruta Samhita describing the Marma, stored with full chapter and verse citation, Sanskrit text, transliteration, and vetted translation.

#### 6.9.3 Real-Time Marma Proximity Detection

The Marma proximity detection algorithm operates as a continuously running module within the Surgeon's Eye vision pipeline. The algorithm functions as follows:

1. The anatomical structure recognition output from the Surgeon's Eye provides the system with an estimate of the anatomical region currently in the operative field — expressed as a body region (neck, upper abdomen, retroperitoneum, pelvis, and so on) refined to specific named structures where they are visible (common carotid, hepatoduodenal ligament, sciatic notch, and so on).

2. This anatomical context is matched against the Marma anatomical region catalogue. For each Marma whose anatomical region or neighbouring structures overlap with the currently identified operative anatomical context, a Marma candidate set is constructed.

3. For each Marma in the candidate set, the system evaluates the operative depth and direction of dissection against the Marma's dimensional extent and depth profile from surface landmarks. Marma points that are in the anatomical vicinity but at substantially different depths from the current dissection plane are weighted lower. Marma points within the active dissection depth range are prioritised.

4. When a Marma candidate's proximity score exceeds a configurable threshold, the Oracle agent is queried for the full Marma guidance package. The guidance is delivered through the following output channels simultaneously:
   - the theatre display shows the Marma's anatomical diagram with the current operative region highlighted, the Sanskrit name rendered in Devanagari, the injury classification category in both Sanskrit and English, and the protective doctrine;
   - the Voice agent announces the Marma name, its injury classification, and the one-sentence protective doctrine in a quiet, advisory tone through the conversational path (not the critical alert path, since Marma proximity is an advisory, not an emergency);
   - the full Marma record including the shloka is available on demand through a verbal query: "Nael, tell me about this Marma."

5. If the surgeon's dissection moves away from the proximity zone, the Marma advisory is quietly dismissed from the display. If the dissection moves toward a higher-classification Marma (Sadya Pranahara or Kalantara Pranahara class), the delivery tone escalates.

#### 6.9.4 Bidirectional Classical-Modern Knowledge Bridge

The Oracle agent implements a bidirectional semantic translation capability between classical Shalyatantra and contemporary surgical terminology:

**Classical to Modern:** A query in Shalyatantra terminology — "What is the modern equivalent of Tundikeri?" or "Where is the Stanamula Marma in modern anatomy?" — retrieves the classical description from the corpus and returns the modern anatomical correlate with references.

**Modern to Classical:** A query in modern surgical terminology — "What does Sushruta say about dissection in the carotid triangle?" or "Is there a classical surgical doctrine for portal dissection?" — retrieves relevant corpus content through semantic search against the full Shalyatantra vector index and returns the closest classical parallel with full shloka citation.

**Eight Shastra Karma Operations:** The Oracle encodes the eight classical surgical operations of Sushruta — *Chedana* (excision), *Bhedana* (incision), *Lekhana* (scraping), *Visravana* (drainage), *Esana* (probing), *Aharana* (extraction), *Sivana* (suturing), and *Tundikeri* (puncturing) — with their classical descriptions, indications, contraindications, and post-operative management protocols from the Sushruta Samhita, mapped to their modern surgical equivalents.

**Vrana Management:** Classical wound management doctrine from the Sushruta Vrana (wound) chapters is encoded, covering the Shodhana (wound cleansing) and Ropana (wound healing promotion) protocols, with their modern pharmacological equivalents and the evidence-based basis for their contemporary use where available.

#### 6.9.5 Research and Teaching Mode

The system implements an optional Research and Teaching Mode activated by institutional consent. In this mode, the complete session data — vision events, conversation transcripts, vital trends, pharmacokinetic records, Oracle consultation records, and Chronicler output — is anonymised by the PHI redaction engine and structured into a research dataset conforming to standard medical data interchange formats. These anonymised, structured datasets are made available for post-operative analysis, AI model improvement, surgical curriculum development, and classical knowledge validation studies. This mode is governed by patient and surgeon consent frameworks and by the institutional ethics requirements of the deploying institution.

### 6.10 PHI/PII Redaction Engine

The invention implements a protected health information redaction engine specifically designed for the Indian regulatory context, supporting the Digital Personal Data Protection Act, 2023 and the National Digital Health Mission framework.

The engine applies rule-based pattern matching for the following Indian-specific identifier categories:

- Aadhaar number: twelve-digit national identity number, with and without grouping separators;
- PAN card: ten-character alphanumeric tax identifier;
- ABHA (Ayushman Bharat Health Account): fourteen-digit health account identifier;
- Voter identification card number;
- Hospital registration and medical record identifiers, including MRN, UHID, and IP/OP number formats;
- Insurance policy and claim reference numbers;
- Indian mobile phone numbers with and without country code prefix.

Universal PII patterns are also supported, including email addresses, dates of birth in contextual setting, postal addresses, and IP addresses.

The engine operates in three configurable redaction modes: MASK (replacing PHI with a type label in square brackets), HASH (replacing PHI with a type label and a short deterministic hash for audit linkage without re-identification), and PARTIAL (preserving first and last characters with internal masking for operational continuity).

A surgical terminology whitelist prevents inadvertent redaction of clinical terms that share surface similarity with name patterns, including anatomical eponyms, procedure names, and system-specific terms.

Redaction is applied at three points in the data pipeline: on transcripts before storage, on Chronicler reports before finalisation, and on WebSocket events before transmission to the theatre display.

### 6.11 Theatre Display System

The theatre display system is a web application served within a browser on a smart television or large monitor positioned in the operating theatre for visibility to the surgical team from the operating table distance.

The display receives instructions from the multi-agent system through the real-time communication layer and adapts its content dynamically based on the current surgical context, active agent outputs, and verbal commands from the surgeon.

Display content is voice-commanded by the surgeon through the Voice agent. Commands demonstrated in the implemented system include: showing the patient's vital signs with trend indicators and trajectory projections, displaying three-dimensional anatomical renderings of the current operative region, showing the classical Marma diagram for the operative region with Sanskrit nomenclature in Devanagari script and the fivefold classification labels, displaying the patient's pre-uploaded imaging with AI-generated segmentation overlays, presenting the current anaesthetic drug record and pharmacokinetic plasma and effect-site concentration curves, displaying the surgical timeline with timestamped key events, presenting the instrument and swab count status from the Overhead Sentinel, showing reference incision diagrams for the current surgical approach, and rendering Sanskrit shlokas from Oracle consultations in Devanagari with Roman transliteration and English clinical commentary.

The display operates proactively when safety-relevant events occur without requiring verbal commands: vital sign alerts cause immediate prominent display of the flagged parameters with trend arrows, haemorrhage events trigger operative field region highlighting and haemostasis reference display, Tissue Stress Monitor alerts display a retraction duration counter alongside the tissue protection advisory, Marma proximity events display the Marma anatomical diagram and protective doctrine, and instrument count discrepancies at closure trigger a prominent count status display.

The display design adheres to operating theatre visual ergonomics: absolute black background optimised for dark-adapted vision, high-contrast text rendered at minimum fourteen point size (seventy-two point minimum for vital values), and a colour language system where each intelligence agent has a distinct accent colour enabling the surgical team to identify which intelligence is communicating without reading labels, through pre-attentive colour recognition.

### 6.12 Multi-Voice Conversational Architecture

The Voice agent implements a distinct voice persona for each communication channel within the operative environment. The surgeon and the anaesthesiologist interact with the system simultaneously but through separate voice identities and separate audio channels, preventing cross-channel confusion in the high-noise operating theatre environment.

The surgeon's channel employs a calm, measured voice profile designed for brief, precise clinical communication. The anaesthesiologist's channel employs a distinct voice identity with pharmacological language patterns appropriate to the anaesthetic domain. When the Pharmacist agent communicates a drug alert, it speaks in the anaesthesiologist's channel with a voice profile that signals anaesthetic rather than surgical content.

This multi-voice architecture is implemented through a neural text-to-speech engine supporting multiple simultaneous voice profiles. Voice assignment is persistent across the session — the surgeon will always hear the same voice for the same agent, building audio-cognitive association over time.

### 6.13 Agent Security Sandbox and Privacy Routing

Each of the eleven intelligence agents operates within an explicitly defined security sandbox that specifies: which network endpoints the agent is permitted to access, which internal system services it may call, what data categories it may receive, and what data categories it may transmit externally. These sandbox definitions are enforced at the container orchestration level, not merely at application code level.

The privacy routing mechanism is the enforcement logic for this agent-level data governance. It evaluates each inference request for PHI content markers before routing: requests carrying patient-identifiable content — vital sign values, drug administration records, surgical event descriptions containing age and demographic context — are routed to a local language model running within the secure session environment. General medical knowledge queries without patient-identifiable context may be routed to cloud inference endpoints. This routing decision is made programmatically and consistently, and cannot be overridden by agent logic.

The Devil's Advocate agent is configured with the most restrictive sandbox: zero external network access. Its operation is entirely local, operating only on in-memory agent state data. This ensures that the cross-agent safety challenge function, which has access to the most comprehensive patient context of any single agent, can never become a pathway for data exfiltration.

### 6.14 Surgical Memory Cortex

The Surgical Memory Cortex is the session-scoped persistent memory object that accumulates the complete history of a surgical session. It is not a simple event log; it is a structured, semantically indexed accumulation of all significant session events, designed to support both real-time agent queries during the session and post-operative synthesis by the Chronicler agent.

The Cortex accumulates: all transcribed speech with speaker attribution and timestamps; all vision events (anatomical recognitions, phase transitions, haemorrhage events, Marma proximity events, Tissue Stress Monitor events); all vital sign time-series from the Monitor Sentinel; all drug administration events and pharmacokinetic state snapshots from the Pharmacist; all instrument and swab count states from the Overhead Sentinel; all Oracle consultation queries and responses with shloka citations; all Devil's Advocate challenge events and surgeon responses; all system alerts by category, time, and resolution.

During the session, any agent may query the Cortex for historical context — "What was the patient's heart rate during the last haemorrhage event?" or "When was the last time we logged ephedrine?" — and receive a structured, time-referenced response. At session closure, the Chronicler agent reads the complete Cortex to generate the Intraoperative Chronicle.

### 6.15 Deployment Architecture and Compute Profiles

The invention is designed to operate across multiple deployment profiles without requiring architectural changes:

**Cloud per-surgery profile:** A GPU compute instance is provisioned immediately prior to the surgical session, all services are deployed through container orchestration, the session runs, and the instance is terminated at session close. Billing is incurred only for surgical hours. This profile enables cost-efficient deployment accessible to lower-resource hospitals.

**Hybrid cloud profile:** Speech and vision inference are performed locally on a modest GPU (a single twenty-four gigabyte accelerator is sufficient), while deep language model reasoning for pre-operative analysis and post-operative documentation routes to cloud inference endpoints.

**Local on-premises profile:** All services run on a local GPU server within the hospital network, with no patient data leaving the premises. This profile meets the most stringent data residency requirements.

**Demo and validation profile:** A full demonstration session operates without any live GPU, using a scripted deterministic session with realistic physiological simulation, enabling evaluation and training without live compute cost.

All profiles share an identical API surface and event bus contract. The compute profile is configured through environment variables, and the system's core control architecture — agent behaviour, event routing, safety paths, and knowledge retrieval — is identical across all profiles.

### 6.16 Surgeon Profile and Adaptive Personalisation

The Voice agent implements a persistent surgeon personalisation system that builds a profile for each individual surgeon across successive surgical sessions. The profile captures:

- linguistic fingerprint: the surgeon's preferred anatomical terminology, clinical shorthand, eponym versus descriptive preferences, and language mixing patterns;
- interaction rhythm: how frequently the surgeon requests proactive information versus preferring to speak first;
- informational preferences: how much context is desired per response, preferred level of detail;
- alert acceptance patterns: which categories of proactive advisory the surgeon has consistently accepted versus dismissed, with profile-level suppression of consistently unwanted notification categories;
- decision tempo: the characteristic pace at which the surgeon moves through operative phases, enabling the system to anticipate informational needs by staged pre-loading.

This profile renders the system increasingly personalised to the individual surgeon over time, converting a generic AI assistant into that surgeon's specific AI assistant after approximately ten sessions. This progressive personalisation creates system utility that deepens through continued use and constitutes a compounding asset for the surgeon that cannot be replicated from a fresh deployment.

---

## PART VII — CLAIMS (PROVISIONAL DRAFT SKELETON)

The following claims are provisional in nature and intended to define the scope of protection sought. Final claim language is subject to revision by qualified patent counsel.

### Independent Claims

**Claim 1.** A computer-implemented intraoperative surgical intelligence system comprising:
a TriVision three-camera operative environment perception subsystem comprising a first head-mounted operative field camera, a second physiological monitoring display camera, and a third overhead theatre-wide camera, wherein all three camera streams are processed concurrently within a shared GPU computation graph and their structured outputs are fused into a unified contextual model of the operative environment;
a multi-agent orchestration subsystem comprising a plurality of concurrently operating software agents each assigned to a distinct clinical intelligence function, wherein each agent subscribes to events on a shared event bus, maintains session-scoped memory, and publishes outputs to the event bus;
a dual-path audio output subsystem comprising a first critical alert path configured to deliver safety alerts from classifier outputs to audio output without language model inference involvement within a latency budget below five hundred milliseconds, and a second conversational path configured to process voice queries through speech recognition, language model inference, and speech synthesis;
wherein the system maintains operational continuity from pre-operative patient analysis through intraoperative session to post-operative handover generation as a single uninterrupted session context.

**Claim 2.** The system of Claim 1, wherein the TriVision subsystem assigns to the first camera: a surgical scene segmentation pipeline, an anatomical structure recognition pipeline, a haemorrhage pattern classifier, a tissue stress and retraction duration monitoring module, a Marma proximity detection module, and an operative phase classifier; assigns to the second camera: a perspective correction pipeline, a region-of-interest detection pipeline, and an optical character recognition pipeline for extraction of numerical vital sign values from physiological monitoring equipment without hardware-level integration; and assigns to the third camera: a surgical instrument and swab object detection and multi-object tracking pipeline, a sterile field boundary monitoring module, and a patient positioning monitoring module.

**Claim 3.** The system of Claim 1, further comprising a Marma Vigyana intelligence subsystem configured to: detect operative proximity of the current dissection zone to classical Ayurvedic Marma anatomical points through analysis of the first TriVision camera stream; query a structured citation-preserving classical Shalyatantra corpus; and deliver to the surgeon a guidance package comprising the Marma's Sanskrit name, its injury classification under the fivefold Sushruta system, the clinical consequences of injury to that Marma, the classical protective operative doctrine, and the specific shloka citation with chapter and verse reference from the Sushruta Samhita.

**Claim 4.** The system of Claim 3, wherein the Marma intelligence subsystem encodes all 107 classical Marma anatomical points as defined in the Sushruta Samhita Sharirasthana, each record comprising a Sanskrit identity with Devanagari script rendering, a modern anatomical correlate in contemporary nomenclature, a dimensional extent in classical Angula measurement and modern millimetre range, an injury classification under the categories of Sadya Pranahara, Kalantara Pranahara, Vishalyaghna, Vaikalyakara, and Rujakara, a structured operative consequence description, a protective doctrine, and at least one primary shloka citation.

**Claim 5.** The system of Claim 3, further comprising a bidirectional classical-modern surgical knowledge bridge configured to translate a query expressed in contemporary surgical anatomical terminology into a corresponding classical Shalyatantra reference with shloka citation, and to translate a query expressed in classical Shalyatantra terminology into a corresponding modern anatomical and surgical description.

**Claim 6.** The system of Claim 1, wherein the multi-agent orchestration subsystem comprises at minimum eleven agents covering the clinical roles of: primary voice interaction and surgeon profiling, predictive physiological monitoring and trend projection, haemorrhage pattern detection, overhead environmental safety and instrument and swab reconciliation, operative field vision analysis and phase detection, pre-operative patient analysis and risk scoring, anaesthetic pharmacology management and real-time pharmacokinetic modelling, classical Ayurvedic surgical knowledge and Marma intelligence, general contemporary clinical knowledge, cross-agent safety challenge with no external network permissions, and post-operative chronicle and handover documentation.

**Claim 7.** The system of Claim 1, wherein the critical alert path delivers at minimum: haemorrhage detection alerts from a dedicated bleeding pattern classifier, predictive physiological deterioration alerts from a trajectory projection model applied to vital sign time-series, tissue retraction duration alerts from a retractor engagement timer module, and instrument or swab count discrepancy alerts from an overhead tracking reconciliation module, without any of said alerts entering a language model inference queue.

**Claim 8.** The system of Claim 1, further comprising a pharmacokinetic modelling engine implementing one or more deterministic population compartmental pharmacokinetic models for anaesthetic agents, configured to receive drug administration events parsed from natural speech by passive listening, and compute real-time predicted plasma and effect-site concentration values.

**Claim 9.** The system of Claim 1, further comprising a protected health information redaction engine configured to identify and redact Indian-specific personal data categories from transcribed speech and generated documents, including Aadhaar number, PAN card identifier, ABHA health account identifier, voter identification number, and hospital medical record identifiers, prior to storage or external transmission.

**Claim 10.** The system of Claim 1, further comprising a cross-agent safety challenge agent configured to monitor for logical conflicts between the states of concurrently operating agents at clinical decision points, to generate a single non-blocking confirmatory query upon detection of conflict, and to accept the clinician's response as final without repetition, wherein said agent operates with no external network access.

**Claim 11.** A computer-implemented method for intraoperative surgical intelligence comprising:
concurrently processing camera streams from three role-differentiated cameras in a TriVision configuration, including an operative field camera, a physiological monitoring display camera, and an overhead theatre-wide camera;
fusing the structured outputs of all three camera pipelines into a unified contextual model of the operative environment;
continuously evaluating the operative field camera output for proximity to classical Ayurvedic Marma anatomical regions and delivering cited Sushruta Samhita guidance on detection;
routing safety-critical event signals through a first low-latency audio output path that bypasses language model inference;
routing conversational queries through a second audio path involving speech recognition, language model inference, and speech synthesis;
maintaining session-level continuity across pre-operative preparation, intraoperative execution, and post-operative documentation phases within a Surgical Memory Cortex; and
generating structured post-operative chronicle and handover artifacts from the accumulated Surgical Memory Cortex at session closure.

**Claim 12.** The method of Claim 11, further comprising: receiving drug administration events from natural speech monitoring of the anaesthesiologist's voice channel without requiring structured input; computing real-time pharmacokinetic concentration profiles using deterministic population pharmacokinetic models; and delivering pharmacological guidance through a dedicated anaesthesiologist voice channel distinct from the surgeon's voice channel.

**Claim 13.** The method of Claim 11, further comprising: applying Indian-specific protected health information pattern detection to speech transcripts and generated documents; and redacting identified personal data categories prior to storage or transmission in compliance with the Digital Personal Data Protection Act, 2023.

**Claim 14.** The method of Claim 11, further comprising: extracting numerical vital sign values from the physiological monitoring display camera through perspective correction, region-of-interest detection, and optical character recognition without requiring hardware integration with monitoring equipment; computing forward-projection trend models from the extracted vital sign time-series; and issuing predictive alerts when projected parameter trajectories are estimated to breach clinically significant thresholds before they actually do so.

**Claim 15.** A non-transitory computer-readable medium storing machine-executable instructions which, when executed by one or more processors, cause the processors to implement the method of Claim 11.

### Dependent Claim Themes for Elaboration in Complete Specification

- wake-word three-tier detection architecture and the "Nael" agent identity design rationale;
- surgeon profile construction methodology and adaptive behaviour calibration across sessions;
- deployment profile configuration across cloud per-surgery, hybrid, and on-premises compute environments;
- privacy routing logic for local versus cloud language model selection by PHI content detection;
- TriVision contextual fusion model structure and agent access protocol;
- Marma fivefold classification system and proximity detection algorithm in detail;
- tissue stress monitor retraction duration thresholds by tissue class;
- multi-voice TTS architecture and channel assignment logic;
- agent security sandbox specification and NemoClaw governance integration;
- research and teaching mode consent framework and anonymisation pipeline.

---

## PART VIII — ABSTRACT

The present invention discloses a computer-implemented intraoperative surgical intelligence system designated ShalyaMitra, which operates as a continuous AI presence in the operating theatre from pre-operative preparation through post-operative handover. The system's primary perceptual architecture is the TriVision three-camera operative environment perception system, which simultaneously processes three role-differentiated camera streams: a head-mounted operative field camera running anatomical recognition, haemorrhage detection, tissue stress monitoring, and Marma proximity detection pipelines; a fixed camera directed at the physiological monitoring display running optical character recognition for real-time vital sign extraction without equipment integration; and an overhead theatre-wide camera running instrument and swab multi-object tracking and sterile field monitoring. All three streams are processed concurrently and their outputs are fused into a unified contextual model of the operative environment. The system employs eleven concurrent specialised software agents communicating through a shared event bus, coordinated by a session orchestrator and a Surgical Memory Cortex maintaining full contextual memory throughout the session. A novel dual-path audio architecture separates safety-critical alerts — delivered in under five hundred milliseconds directly from classifier outputs — from a conversational voice path involving speech recognition, language model reasoning, and neural speech synthesis. The invention is the first known intraoperative system to implement real-time Marma Vigyana proximity detection, delivering cited Sushruta Samhita shloka guidance when the operative dissection zone approaches any of 107 encoded classical Marma anatomical points, with bidirectional classical-modern knowledge mapping through the Oracle agent. Additional features include a deterministic pharmacokinetic modelling engine for total intravenous anaesthesia, an Indian-context PHI redaction engine covering Aadhaar, PAN, ABHA, and hospital identifier categories, a cross-agent safety challenge mechanism, multi-voice channel architecture, and agent-level security sandboxing with privacy-aware inference routing.

---

## PART IX — REGULATORY CONTEXT AND DEVELOPMENT PATHWAY

The invention is designed with the regulatory pathway for Software as a Medical Device (SaMD) classification under the Central Drugs Standard Control Organisation (CDSCO) in India, and the international IMDRF SaMD guidance framework. The technical architecture incorporates:

- auditable reasoning chains through a text-intermediate pipeline (every AI output is traceable to a specific transcript input and a stored reasoning record);
- structured AI intervention logging within the session chronicle for regulatory review;
- configurable clinical decision support disclaimer mechanisms on all AI outputs;
- an audit logging subsystem recording all clinically significant AI actions with timestamps and session context;
- data export formats supportive of regulatory documentation workflows.

The system is developed under NVIDIA Inception Programme membership and NVIDIA Digital Health Programme membership, utilising the NVIDIA healthcare AI platform stack including Holoscan SDK for surgical video processing (designed to the SaMD certification standard from its architectural foundations), Riva for speech AI, NIM for language model inference, NeMo for model training and fine-tuning, MONAI for medical vision, and NemoClaw for enterprise-grade agent security and governance.

---

## PART X — CLASSICAL KNOWLEDGE HERITAGE STATEMENT

The inventors wish to formally acknowledge that the Shalyatantra and Marma Vigyana doctrines encoded in this system originate in the ancient Indian knowledge tradition, authored within the Sushruta Samhita and the related Ayurvedic corpus. The present invention is an act of technological stewardship — applying computation to make this living wisdom present in the modern operating theatre, accessible in real time to surgeons of both classical and modern training, with full citation and attribution preserved in every output.

The Samarangana Sutradhara, the classical text on architecture and mechanical arts attributed to King Bhoja of the Paramara dynasty (approximately eleventh century CE), contains descriptions of mechanical automata and intelligently responsive systems. Its conceptual framework — of a system that perceives its environment and responds in service of human purpose — provides philosophical grounding for the present invention's design philosophy. The inventors intend to formally develop and document the mapping between Samarangana Sutradhara principles and the architectural design of the present system as an annexure to the complete specification.

---

## PART XI — BEST METHOD OF PERFORMANCE

The best method of performing the invention, based on the inventors' current knowledge:

1. **Hardware configuration:** Mount a compact wide-angle camera (minimum 1080p at 30fps) on the surgeon's headwear or loupes, oriented to the operative field (Surgeon's Eye). Fix a second wide-angle camera (minimum 1080p at 30fps) on a flexible arm positioned to view the patient physiological monitoring display without obstruction (Monitor Sentinel). Mount a third wide-angle camera (minimum 1080p at 30fps) on the operating theatre overhead light track or ceiling, oriented downward to cover the full operative theatre floor and instrument trolley (Overhead Sentinel). Configure Bluetooth audio neckbands with active noise cancellation on the surgeon and anaesthesiologist, each connecting to a separate audio channel on the session server.

2. **Compute provisioning:** Deploy on a GPU compute instance (minimum 40 GB GPU memory recommended for full concurrent three-stream TriVision processing with language model inference) provisioned at surgical session start. Deploy: a WebRTC selective forwarding unit for media transport; a GPU-accelerated speech recognition pipeline for low-latency continuous transcription on both audio channels; a GPU-accelerated surgical video processing framework with the TriVision pipeline configuration; a language model inference server for conversational reasoning; a neural text-to-speech engine for multi-voice conversational output with distinct surgeon and anaesthesiologist voice profiles; a CPU-resident lightweight text-to-speech engine for critical alert audio output; a vector database hosting both Shalyatantra corpus and medical knowledge embeddings; and an in-memory data store for session state and the Surgical Memory Cortex.

3. Register all eleven intelligence agents with the orchestrator at session startup. Configure agent security sandbox rules before registration.

4. Initialise the session with patient demographics and pre-operative analysis from the Scholar agent.

5. Connect all physical devices through the real-time transport layer and confirm health status of all three TriVision camera streams before announcing session readiness.

6. Operate both audio paths simultaneously and independently throughout the surgical session.

7. Generate and deliver Chronicler outputs at session closure before patient transport.

8. Terminate the compute instance and archive encrypted session data and surgeon profile updates.

---

## PART XII — ANNEXURES TO BE ATTACHED BEFORE COMPLETE SPECIFICATION

The following annexures are to be prepared and attached prior to complete specification filing:

**Annexure A:** System architecture block diagrams as described in Part VI-A (Figures 1 through 8), with particular emphasis on the TriVision camera configuration diagram (Figure 2) and the Marma proximity detection diagram (Figure 6).

**Annexure B:** Inventor declaration and contribution mapping.

**Annexure C:** Conception timeline evidence (design records, development logs, version history).

**Annexure D:** Third-party component attribution and licence matrix (LiveKit, PaddleOCR, OpenCV, MONAI, Fish Speech, Piper, Qdrant, PyTCI, OpenWakeWord, YOLOv11, SAM2, Cornerstone.js and others).

**Annexure E:** Clinical pilot documentation (institutional ethics approvals, consent templates, pilot outcome records — when available).

**Annexure F:** IMA endorsement or validation evidence (when available).

**Annexure G:** CDSCO SaMD classification filing reference (when filed).

**Annexure H:** Samarangana Sutradhara doctrine-to-architecture mapping note.

**Annexure I:** Marma database schema with sample records demonstrating the complete structured encoding for at minimum ten representative Marma points, including examples from each of the five Sushruta injury classification categories.

**Annexure J:** Pharmacokinetic model parameter tables and validation references for Marsh, Schnider, and Minto models.

**Annexure K:** TriVision camera hardware specification and mounting configuration documentation.

**Annexure L:** Agent security sandbox specification table showing network permissions, data access scope, and output channel restrictions for each of the eleven agents.

---

## PART XIII — DECLARATION

I/We, the applicant(s), declare that:

1. The invention described in this provisional specification is, to the best of my/our knowledge and belief, genuinely novel and has not been disclosed publicly prior to the date of this filing.
2. I/We am/are the true and first inventor(s) or have acquired the right to apply.
3. The particulars provided are true and correct.

[Signature, name, date, and place to be completed by the Applicant/Authorised agent]

---

*This document is a provisional patent specification input prepared for Indian Patent Office filing under The Patents Act, 1970 and The Patents Rules, 2003. It is not a substitute for review and finalisation by qualified Indian patent counsel. The inventors are advised to engage a registered patent agent licensed before the Indian Patent Office for formal filing, prosecution, and legal strategy.*

*Document classification: Confidential — Patent Preparation Material*
