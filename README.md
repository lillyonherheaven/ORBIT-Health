ORBIT Health OS v3.0

Offline-First Astronaut Health Monitoring & Decision-Support System



NASA Space Apps Challenge 2026
Challenge: Create Health Monitoring Software for Astronauts on Space
Missions

ORBIT Health is an offline-first prototype designed to help astronauts
monitor health-related observations and make more informed onboard
decisions during long-duration and deep-space missions, especially when
communication with Earth is delayed or unavailable.

The system brings health observations, crew check-ins, exercise and
performance records, and spacecraft-environment information into one
operational view. It checks data quality, compares observations with
personal baselines, analyzes trends and configured safety rules, and
presents explainable risk states with relevant next-step guidance.

ORBIT Health supports medical decision-making; it does not replace
medical professionals, diagnose conditions, or prescribe treatment.

Contents





The problem



Our solution



Core capabilities



How it works



Risk states



Demonstration scenarios



Data and scientific references



Architecture



Technology stack



Evaluation and reliability



Safety, ethics, and limitations



Repository structure



Running the project

The problem

During deep-space missions, astronauts may experience communication
delays or temporary loss of contact with Earth. Health information can
also be distributed across physiological measurements, exercise records,
sleep and fatigue reports, crew check-ins, and spacecraft environmental
sensors. Without a unified onboard view, meaningful changes may be
difficult to recognize and interpret quickly.

Our solution

ORBIT Health provides a unified, local-first health monitoring and
decision-support experience built around five stages:





Collect observations from supported sources, crew check-ins,

exercise records, and environmental inputs.



Understand data quality, personal baselines, and longitudinal

trends.



Assess risk using transparent safety rules and trend analysis.



Act by presenting relevant guidance and pathways to approved

procedures.



Learn & synchronize by preserving records and synchronizing

queued information when communication returns.

The core assessment and guidance workflow is designed to continue
locally without requiring a live connection to Earth.

Core capabilities

Unified crew dashboard

A consolidated interface brings crew status, health-related indicators,
mission context, alerts, and communication status into one view.

Interactive 2D body map

The body map is a navigation aid. Selecting a region can expose related
monitoring domains, indicators, trends, active alerts, and linked
guidance. It does not diagnose or localize disease.

Explainable risk assessment

The assessment approach combines data-quality checks, comparison with an
individual's reference baseline, trend and persistence analysis,
configured critical safety overrides, and evidence-based explanations.
Alerts are designed to communicate what changed, why it may matter,
and what to do next, while showing data quality and uncertainty.

Offline-first operation

Local monitoring, assessment, records, and guidance are designed to
remain available during communication outages. A durable
store-and-forward queue preserves outbound records for later
synchronization.

Judge demonstration controls

The demonstration panel is designed to let reviewers trigger scenarios,
interrupt communications, introduce sensor faults, and inspect system
responses.

Adherence-focused engagement

Engagement features may recognize check-ins and completion of approved
exercise activities. Symptom reporting is never scored or penalized, and
the design avoids competitive health leaderboards.

How it works

Data sources
    |
    v
DataSource adapter
    |
    v
Ingestion + quality checks
    |
    v
Local health store
    |
    v
Personal baseline + trend analysis
    |
    v
Risk assessment + explanation
    |
    v
Decision-support guidance
    |
    v
Astronaut dashboard + local outbox
    |
    v
Synchronization when connectivity returns

The DataSource adapter separates input formats from the assessment
engine. The blueprint defines synthetic, CSV, and replay source patterns
so new data sources can be connected without rewriting the risk engine
or interface.

Risk states



  State                               Meaning



  GREEN                           No configured alert is currently
                                      active for available, sufficiently
                                      reliable data.

  AMBER                           A pattern warrants attention or
                                      monitoring.

  ORANGE                          A significant warning requires
                                      review and the relevant next step.

  RED                             A critical configured trigger
                                      requires urgent attention and the
                                      applicable escalation pathway.

  GRAY                            Data are missing, unreliable,
                                      stale, or unavailable; a healthy
                                  state cannot safely be assumed.



Risk is communicated using color together with icons and text labels.
Missing or unreliable information must never silently become GREEN.

Demonstration scenarios

All numeric values in the scenarios are illustrative demonstration
values, not clinical thresholds.

Scenario A --- Muscle, metabolic, and fatigue trend

A simulated combination of reduced exercise performance or completion,
shorter sleep, and increased fatigue demonstrates baseline comparison,
persistence analysis, and an explainable ORANGE warning.

Scenario B --- Radiation event and vigilance change

A declared radiation-related event or dosimeter trend is combined with a
seeded change in a sustained-attention task or fatigue report. It
demonstrates evidence combination and critical-rule behavior. A
vigilance change alone is not intended to create a RED state.

Scenario C --- Cabin hazard during communication loss

A simulated cabin-environment hazard is introduced while communications
are unavailable. The demonstration shows local monitoring, unavailable
visual/eye data represented as GRAY where applicable, and queued
synchronization after reconnection.

Additional fault demonstrations include disabling or corrupting a
sensor, injecting noisy or invalid data, and showing uncertainty rather
than treating faulty data as healthy.

Data and scientific references

NASA Open Science Data Repository (OSDR)



  Study                                                              Research context         Project relevance and
                                                                                              limitation



  OSD-684     Human skeletal muscle    Muscle-health research
                                                                     tissue-chip research on  context; not a wearable
                                                                     spaceflight-related      feed or clinical
                                                                     changes in fiber type    predictor.
                                                                     and metabolic gene
                                                                     expression.              

  OSD-816     Ex vivo human ocular     Ocular/SANS context;
                                                                     model investigating      not a live astronaut
                                                                     mechanisms related to    eye measurement or
                                                                     spaceflight-associated   cabin sensor feed.
                                                                     neuro-ocular syndrome
                                                                     (SANS).                  

  OSD-939     Rodent                   Cautious
                                                                     sustained-attention and  vigilance-scenario
                                                                     dopaminergic-protein     context; not proof of
                                                                     research following       human astronaut
                                                                     proton-radiation         outcomes or a human
                                                                     exposure.                prediction model.

  OSD-1010   Human gut-on-chip        Gastrointestinal
                                                                     research on epithelial   mechanism context; not
                                                                     responses to             a radiation dosimeter
                                                                     space-relevant heavy-ion feed.
                                                                 irradiation.             



Data interpretation: These studies are research evidence, not
real-time astronaut vital-sign streams. Molecular, tissue-chip, ex vivo,
and rodent measurements must not be converted into astronaut
observations without an approved, scientifically valid mapping.
Provenance should preserve study/version, model, sample, assay, source
file/column, original unit, transformation, and access/license status.

BRSMPT Campaign 1 Ares

The project materials identify BRSMPT Campaign 1 Ares
cognitive-performance records, including subject records and
task-related materials such as Simple Reaction Time, Running Memory,
Matching to Sample, and mRTC-related records. These materials provide
cognitive-performance research context; they should not be represented
as live physiological sensor data or as measurements from the named demo
crew members.

Architecture

The master blueprint describes an eight-layer, offline-first
architecture:





Data sources --- wearables, medical devices, crew check-ins,

exercise equipment, cabin sensors, or simulation inputs.



DataSource adapter --- isolates source formats from the rest of

the system.



Ingestion and quality control --- normalizes units and

timestamps; checks quality; handles missing, stale, duplicate, and
  out-of-order records.



Onboard health store --- local persistence for observations,

baselines, event history, audit records, and outbound queue.



Safety and analysis --- configured rules, baseline and trend

analysis, anomaly handling, confidence, and uncertainty.



Decision support --- risk state, explanation, relevant procedure

pathway, and escalation.



Astronaut interface --- dashboard, alerts, trends, check-ins,

body map, and guidance.



Communications --- prioritized store-and-forward synchronization

with Mission Control.

Offline synchronization

Transmission, delivery, and acknowledgement are separate states. A
transmission attempt is not proof that Mission Control received or
acknowledged a record. Reconnection should synchronize queued records
without duplication or loss.

Technology stack

The master blueprint specifies the following intended stack. Confirm the
final repository before treating every item as part of the delivered
build.

  Area                Technology in blueprint



  Backend             Python 3.11, FastAPI
  Data contracts      Pydantic
  Data processing     pandas, NumPy
  Local storage       SQLite
  Frontend            React with Vite
  Charts              Chart.js
  Offline interface   Service worker / Progressive Web App approach
  Testing             pytest

Evaluation and reliability

The blueprint defines an evaluation approach based on seeded simulations
and fault injection. Measures include:





Detection latency: time from simulated event onset to the first
alert at or above the expected state.



Detection rate: proportion of seeded runs in which the expected
pattern is detected at the expected state.



False-alert count: alerts above GREEN per simulated mission-day
in no-anomaly runs.



Fault robustness: behavior with noisy, missing, duplicated, or
out-of-order observations.



Synchronization integrity: records sent, received, duplicated,
or lost through outage and reconnection cycles.

Results must be measured from actual runs, not hard-coded or presented
as clinical performance. If an evaluation report exists in the submitted
repository, link it here.

Safety, ethics, and limitations

ORBIT Health is a software prototype for demonstration and research
exploration.





Prototype thresholds, trigger windows, and scenario values are
illustrative.



The prototype is not a clinically validated or operationally
approved medical device.



It does not diagnose, prescribe, or replace qualified medical or
mission personnel.



Procedures and countermeasures must be supplied and validated by
responsible mission authorities.



Research datasets are not treated as direct astronaut sensor feeds.



Missing, stale, invalid, or unreliable data are surfaced explicitly.



Passive data are not used to infer psychiatric conditions.



Symptom reporting is not penalized or used as a negative
gamification score.



Prototype security controls do not establish operational security
certification.

Repository structure

The following is the logical structure proposed in the master blueprint.
Update it to match the final submitted repository.

orbit-health/
├── backend/
│   ├── app/
│   │   ├── contracts/
│   │   ├── sources/
│   │   ├── ingestion/
│   │   ├── store/
│   │   ├── baseline/
│   │   ├── risk/
│   │   ├── guidance/
│   │   ├── sync/
│   │   ├── scenarios/
│   │   └── api/
│   ├── config/
│   ├── tests/
│   └── eval/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── charts/
│   │   └── bodymap/
│   └── public/
├── docs/
│   ├── architecture.md
│   ├── demo_script.md
│   ├── judge_qa.md
│   └── eval_results.md
└── README.md

Running the project

Use the setup and run commands documented in the submitted repository's
actual backend and frontend configuration files. The master blueprint
specifies the technology stack and logical modules, but does not
establish final executable entry-point names, package scripts,
environment variables, or deployment configuration.

Before publishing, add and verify the commands for: 1. Installing
backend dependencies. 2. Starting the backend API. 3. Installing
frontend dependencies. 4. Starting the frontend dashboard. 5. Running
automated tests. 6. Launching demonstration scenarios and the
offline/reconnection flow.

Do not publish guessed commands. Verify them against the final
repository so reviewers can reproduce the demo.

Project information





Project: ORBIT Health OS v3.0



Challenge: NASA Space Apps Challenge 2026



Team: [Add team name]



Repository: [Add public repository URL]



Demo video: [Add public demo URL]

Acknowledgements

We acknowledge NASA's Open Science Data Repository and the researchers
whose published studies provide scientific context for this prototype.
The cited studies are used within their stated research scope and
limitations.

Built for a future where space exploration goes farther --- and
astronaut health remains a priority.
