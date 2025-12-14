# Medication Preparation & Stock Management System

### **Team: Gotthard Panorama Express**

![V8](Camunda/Archive/5.jpg)

## Table of Contents

- [Project Members](#project-members)
- [Abstract & Project Overview](#abstract--project-overview)
- [AS-IS Process](#as-is-process)
  - [Key Limitations of the AS-IS Process](#key-limitations-of-the-as-is-process)
  - [AS-IS BPMN Diagram](#as-is-bpmn-diagram)
  - [Project Goal](#project-goal)
- [TO-BE Process](#to-be-process)
  - [TO-BE BPMN Diagram](#to-be-bpmn-diagram)
  - [Challenges and Requirements](#challenges-and-requirements-addressed-by-the-to-be-process)
  - [Users and Stakeholders](#users-and-stakeholders)
- [Technologies Used](#technologies-used)
  - [Frontend Mockups](#frontend-mockups)
- [Limitations](#limitations)

---

# Project members

## Project Team / Authors

| Name      | Role                      | Email                                    |
| --------- | ------------------------- | ---------------------------------------- |
| Janosh    | BPMN and Backend          | janosh.werlen@students.fhnw.ch           |
| Dj        | Data Specialist / Backend | djordji.pavloski@students.fhnw.ch        |
| Merel     | APIs and Frontend         | annemerel.dejong@students.fhnw.ch       |
| Donna     | Medical Expert            | donna.tennigkeit@students.fhnw.ch        |
| Viktorija | Medical Expert            | viktorija.kenstaviciute@students.fhnw.ch |

## Supervisors

| Name               | Email                      |
| ------------------ | -------------------------- |
| Andreas Martin     | andreas.martin@fhnw.ch     |
| Charuta Pande      | charuta.pande@fhnw.ch      |
| Devid Montecchiari | devid.montecchiari@fhnw.ch |

---

## Abstract & Project Overview

In large anaesthesia departments, medication preparation and stock management are still largely **manual**, fragmented, and poorly documented. Every day, medications are prepared, partially used, stored for reuse, or discarded — yet these steps are often **not digitally tracked**. As a result, hospitals face unnecessary medication waste, high operational costs, inefficient workflows, and limited transparency.

This project designs and prototypes a **digital medication preparation and stock management system** for anaesthesia department. Using **process modeling (AS-IS / TO-BE)** and a prototype system design, the project aims to standardize workflows (e.g. order/preparation process steps), improve traceability, and support automation of daily clinical and storage activities. The solution focuses on making medication handling more transparent,and efficient without disrupting existing clinical routines.

[⬆️ Back to Top](#table-of-contents)

---

# AS-IS Process

## Key Limitations of the AS-IS Process

Anaesthesia teams handle large volumes of **high-value, time-critical medications** under strict safety and availability requirements. However, current workflows suffer from several structural limitations:

### No Digital Tracking of Medication Usage

Prepared syringes or vials may be partially used, reused later, or discarded, but these actions are rarely documented, resulting in:

- unnecessary disposal of usable medication (unnecessary costs)
- no structured second-use management
- consumption data is incomplete or inaccurate

### Manual Storage and Medication Location

Medication storage is managed manually, and large storage areas make it difficult to quickly locate specific medications. As a result:

- high dependency on storage workers for information
- no real-time overview of stock levels
- risk of overlooked expiry dates
- manual reordering
- frequent interruptions of storage staff
- delays in clinical procedures
- lack of transparency across departments

Together, these issues cause significant **time loss, medication waste, and avoidable costs**, while preventing reliable planning and optimization of anaesthesia medication supply.

## AS-IS BPMN Diagram

![V2](Camunda/Archive/Updated_As_Is_BPMN.png)

---

## Project Goal

The goal of this project is to **digitalize and streamline medication preparation and stock management in anaesthesia** through an integrated Medication Preparation & Management System.

The system aims to:

- provide real-time visibility into medication preparation, usage, reuse, return, and disposal with up-to-date available quantities
- reduce medication waste and expiry-related losses
- enable fast medication search, location, and restocking
- improve coordination between clinical staff and storage personnel and also departments
- increase transparency and traceability through a digital checklist for medication preparation workflows

[⬆️ Back to Top](#table-of-contents)

---

# TO-BE Process

This chapter describes the redesigned and digitalized **medication preparation and stock management process** for anaesthesia department.  
The TO-BE process replaces fragmented, manual activities with a **standardized, transparent, and partially automated workflow** that supports both clinical staff and storage personnel.

The process is modeled using **BPMN (TO-BE)** and serves as the foundation for a prototype system architecture consisting of a frontend interface, backend services, a workflow engine, and a central database.  
The overall goal is to improve traceability, reduce waste, and provide better guidance for locating and restocking medications, without disrupting established clinical routines.

## TO-BE BPMN Diagram

![V3](Camunda/Update_3.0.png)
_Figure: TO-BE BPMN model of the digital medication preparation and stock management process._

## Challenges and Requirements Addressed by the TO-BE Process

| Challenge                                           | Requirement                                                   |
| --------------------------------------------------- | ------------------------------------------------------------- |
| Medication usage is **not tracked**                 | Automated tracking of preparation, usage, reuse, and disposal |
| Stock levels are **managed manually**               | Real-time inventory visibility                                |
| Expiry dates are **checked late or inconsistently** | Automated expiry monitoring and alerts                        |
| Medication is **hard to locate**                    | Digital search and location guidance                          |
| High **time and cost overhead**                     | Workflow automation and reduced manual coordination           |

---

## Users and Stakeholders

### AS-IS Stakeholders

- Storage Worker
- Nurse
- Doctor
- Pharmacist
- Administrator

### TO-BE Stakeholders (SHOULD-BE)

- Storage Worker _(automated ordering support)_
- Nurse _(digital ordering interface)_
- Doctor _(prescription system integration)_
- Pharmacist _(inventory + preparation management)_
- Administrator _(system oversight)_

---

## Data Objects

### Medication Data Template (JSON)

The project uses structured medication objects to ensure consistent storage and API communication.

```json
See medication_data_template.json

```

---

## TO-BE Workflow (Conceptual Step Overview)

The TO-BE workflow follows a structured sequence:

1. **Medication preparation**  
   Medication is prepared according to standardized steps and documented digitally to ensure clarity and traceability.
   After the procedure, the medication status is explicitly evaluated: - fully used - partially used and eligible for storage - or discarded

   This decision is captured in the workflow and determines the subsequent process path.

2. **Medication Usage and Post-Procedure Handling**  
   If medication is **fully used**, the process continues with documentation and closes the preparation cycle.
   If medication is **partially used**, the workflow guides the user to: - document remaining quantity - decide on storage eligibility - and assign a storage location

   Discarded medication is recorded accordingly to maintain transparency and accountability.

3. **Storage and availability Management**  
   Stored medication becomes visible within the system as available stock.  
   The TO-BE process ensures that: - storage locations are documented - available quantities are updated

4. **Restocking and coordination**  
   The TO-BE process explicitly models interactions between: - anaesthesia staff (preparation and usage), - storage workers (availability and restocking), - and system-supported documentation steps.

By making responsibilities and handovers explicit, the process reduces ambiguity, interruptions, and information loss.

---

### Scope Clarification

The TO-BE model focuses on **process structure, documentation, and coordination**.
Advanced features such as automated alerts, predictive analytics, or forecasting are intentionally **out of scope** and not represented in the BPMN model.

The BPMN serves as a **conceptual and prototype-level design**, providing a solid foundation for future digital extensions.

[⬆️ Back to Top](#table-of-contents)

---

# Technologies Used🛠

- Frontend: Vue.js
- Backend: FastAPI
- Database: SQLite (to be specified)
- Business Logic: Python
- Workflow Engine: Langflow

## Frontend Mockups

### Proposed Screens

- <del>[ ] Login Screen</del> -> waiting time
- [ ] Dashboard (orders & inventory overview)
- [ ] Order Creation Form
- [ ] Inventory Management View
- <del>[ ] User Profile/Settings<del> -> wasting time
- [ ] Reports and Analytics

[⬆️ Back to Top](#table-of-contents)

---

# Limitations

- **Prototype-level implementation:** The project demonstrates the concept and workflow design, not a production-ready system.
- **No hospital system integration:** Interfaces to real clinical systems (e.g., HIS/EMR, pharmacy systems, barcode/RFID, procurement) are out of scope.
- **No analytics/forecasting features:** Automated alerts, and predictive planning are not implemented in this version.
- **Manual demo input:** For demonstration purposes, some data entries and status updates are performed manually.

[⬆️ Back to Top](#table-of-contents)

---

# LEFTOVERS from old README.md

## Next Steps TILL 20.11:

| Done? | What                                                                                                                                                                                                                                               | Who                        |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| [X]   | Update Businessplan and Readme                                                                                                                                                                                                                     | Janosh                     |
| [X]   | Define all the Users and Stakeholders of the System (eg. All the People who will interact with the System like "Storage Worker", "Nurse", "Doctor"... etc.) -> Define for "AS-IS" so we can then adapt to "SHOULD-BE"                              | Donna and Viktorija        |
| [X]   | Define Data Objects (Checklist, Communication between Storage Worker, What info is needed to make an order, what should be stored about the medication in the Database (e.g. Name, Formula, Exp. data, producer, dosage...) Idealy in JSON format) | Viktorija and Donna        |
| [ ]   | Design the Frontend Elements, how would Doctors, Nurses etc want to interact with the System, how sould it look like (e.g. as a Mockup)                                                                                                            | Donna, Viktorija and Merel |
| [X]   | Define Teckstack used (e.g. Frontend (Vuejs) Backend(express?), DB (Postgresql), logic (Python), Workflow (Camunda or N8n?))                                                                                                                       | All                        |

## Next Steps TILL 27.11:

| Done? | What                                          | Who               | % Done |
| ----- | --------------------------------------------- | ----------------- | ------ |
| [X]   | Set up Database                               | Djordji           |        |
| [X]   | Design Backend APIS                           | Djorgdi , Merel   |        |
| [X]   | Setup frontend with mockup for main views     | Merel             | 99%    |
| [ ]   | Finalize Data elements in JSON                | Donna & Viktorija |        |
| [ ]   | Update Projectplan and Summarize Developement | Janosh            |        |
| [ ]   | Start Modeling Flow in Camunda / Langflow     | Janosh            |        |

## Next Steps TILL 06.12:

| Done? | What                                                     | Who | % Done |
| ----- | -------------------------------------------------------- | --- | ------ |
| [ ]   | Couple backend with Camundo (Orders internal+ external ) |     |        |
| [ ]   | Demo user story                                          |     |        |
| [ ]   | Transform Demo user story into Frontend/Backend/Camunda  |     |        |
| [ ]   | Think about AI possibilities                             |     |        |
