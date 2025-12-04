# 🩺 Acute Appendicitis – Prototype Simulation Story  
**Use case:** Demonstration scenario for the *Medication Stock Tracking in Anaesthesia* prototype.  

---

## 0. Scenario Setup

We simulate an **acute appendicitis** case that should start in **15–25 minutes** in **OR 3** as emergency case.

**Initial data in system:**

- Case: `Case ID: 456 – Acute Appendicitis – OR 3`
- Anaesthesia Storage:
  - Storage Room A: enough standard drugs, but **no** *Antibiotic "Ertapenem"* 
  - Storage Rooms B & C: also **do not have** *"Ertapenem"*  
- Other departments:
  - Intensive care unit (ICU): **2 vials** of *Antibiotic "Ertapenem"*  
  - Emergency Department (ED): **10 vials** of **Na Bicarbonate**  
- Cart for this case: `Cart OR 3` is available and linked to OR 3.

---

## 1️⃣ T-25 to T-20 min: Start Case & Prepare Standard Medications

### 1.1 Login & Case Selection

**User (Assistant Doctor):**

1. Walks into **Storage Room A**.
2. Opens the **Stock App** on the wall-mounted tablet.
3. Logs in as `Anaesthesia Staff`.
4. Navigates:  
   `Start Case Preparation → Storage Room A → OR 3 → Case 456 (Acute Appendicitis)`

**System:**

- Shows a **“Case Preparation”** screen with:
  - Case ID: 456 (with anonymised patient ID) 
  - OR: 3  
  - Prepared cart: `Cart OR 3`
- Displays a **standard medication checklist** for general anaesthesia, as "std_med_list" in `story_1.json`:
  - Propofol  
  - Lidocain  
  - Rocuronium (fridge)  
  - Ephedrin, Phenylephrin  
  - Ringer
  - Fentanyl, Remifentanil (locked opioid box)

---

### 1.2 Take Standard Medications (Smart Shelf Weighing System)

**System (Smart Shelves with Integrated Scales):**

- Each storage position (for standard, frequently used medications) is placed on a **weighing scale** that is connected to the system.
- When the user removes an ampoule/vial:
  - The scale detects a sudden **weight change**.
  - The system translates the weight difference into a **number of items taken** (e.g. 1 ampoule).
  - Automatically creates a **Movement/Transaction**, e.g.:
    - `from_location: Storage Room A`  
    - `to_location: Cart OR 3`  
    - `quantity: 1`  
    - `user: Assistant Doctor` (current logged-in user)  
    - `reason: prepare_cart`
- The system then:
  - Updates the **stock level** for the corresponding storage location.
- For opioids (if also placed on smart scales or still scanned separately, depending on prototype):
  - Every detected removal from the **Locked Opioid Box** is additionally logged as a **“Controlled Substance”** movement in the **Audit Log**.

**Visual needs for frontend:**

- A **checklist view** where medications automatically change state as items are taken:
  - “Not prepared” → “Prepared” (e.g. when the expected quantity for that case has been reached).
- For each medication row:
  - Live **stock count** and **earliest expiry date**.
  - Optional small status icon:
    - ✔ Prepared  

---

## 2️⃣ T-20 min: Need a Specific Antibiotic (as "add_med_list" in `story_1.json`:)

The patient requires a **specific antibiotic** (*Antibiotic "Ertapenem"*) that is not part of the standard set.

### 2.1 Search for the Antibiotic

**User:**

1. On the Case Preparation screen, taps `+ Add Medication`.
2. Types **"Ertapenem"”** into a search field.

**System:**

- Displays **search results** for “"Ertapenem"” with stock by location:

  - Anaesthesia:
    - Storage Room A: 0  
    - Storage Room B: 0  
    - Storage Room C: 0  
  - Other departments:
    - ICU: 2 vials  
    - ED: 0

- Shows actions:
  - `Request from ICU`
  - `Show ICU contact`

---

### 2.2 Request Help from Storage Worker

**User:**

1. Taps `Request from ICU`.
2. System suggests responsible storage worker for Room A (e.g. **Alex**).
3. Confirms the request.

**System:**

- Creates a **Help Request**:

  - Medication: *"Ertapenem"*  
  - Needed for: `Case 456, OR 3, Storage Room A`  
  - Suggested source: ICU  
  - Priority: *Urgent*

- Sends notification to **Alex (Storage Worker)**:

  > “Urgent request: Antibiotic "Ertapenem" needed for OR 3 (Case 456). ICU has 2 vials. Please coordinate transfer.”

---

### 2.3 Storage Worker Handles the Request

**User (Storage Worker Alex):**

1. Opens **Pharmacist/Storage Worker Dashboard**.
2. Sees a tile:  
   `New Urgent Request – Antibiotic "Ertapenem" – OR 3`
3. Opens the request and sees:
   - Anaesthesia stock = 0 (all rooms).
   - ICU stock = 2 vials.
4. Taps `Contact ICU` or `Send Borrow Request`.

**System:**

- Logs a **planned movement**:

  - `from_location: ICU stock`  
  - `to_location: Storage Room A`  
  - `quantity: 1`  
  - `status: waiting_for_confirmation`

- After ICU confirmation:
  - Updates status to `in_transit`.
  - Sets an ETA (e.g. **10 minutes**).

**User (Assistant Doctor) view:**

- On the Case Preparation screen, next to *Antibiotic "Ertapenem"*:

  - Shows:  
    `Borrowed from ICU – 1 vial – ETA ≈ 10 minutes`  
    and a small progress/clock icon.

---

## 3️⃣ Intra-Op: Na Bicarbonate Needed Mid-Surgery

Surgery has started. During the case, lab results are bad.  
Together with the **Oberarzt**, you decide the patient needs **Na Bicarbonate**.

### 3.1 Quick Mobile Search

**User (Assistant Doctor or Oberarzt):**

1. Opens the **System** of the Stock.
2. Taps `Search Medication`.
3. Types **“Na Bicarbonate”**.

**System:**

- Shows a simple result list:

  - Anaesthesia:
    - Storage Room A: 0  
    - Storage Room B: 0  
    - Storage Room C: 0  
  - Other departments:
    - Emergency Department (ED): 10 vials

- Shows possible actions:

  - `Call ED charge nurse`
  - `Send emergency request`

---

### 3.2 Contact ED

**User (Oberarzt):**

- Taps `Call ED charge nurse`.

**System:**

- Opens the phone dialer with the **correct ED number** from the database.
- (Optional) Logs that an **emergency contact** was initiated for Na Bicarbonate.

**Outcome in scenario:**

- ED agrees to send Na Bicarbonate.
- Delivery time in story: about **8 minutes**.

**Optional system behaviour:**

- If `Send emergency request` is used:
  - Creates an **Emergency Transfer Request** with:
    - Medication: Na Bicarbonate  
    - From: ED  
    - To: OR 3 / Anaesthesia  
    - Priority: *High*  
  - Logs request time and short note (“Case 456, unstable lab results”).

---

## 4️⃣ During Surgery: Extra Medications & Fluids Used (as "extra_used_med_list" in `story_1.json`)

The patient is unstable and bleeding. You use extra drugs and fluids from:

- **Storage Room A**
- The **anaesthesia cart**

### 4.1 Ongoing Usage Logging (Simple Prototype)

**System:**

- For each extra med:
  - Creates a **Movement**:
    - `from_location: Storage Room A`  
    - `to_location: Cart OR 3`  
    - `reason: `use_for_case`
  - Links the movement to:
    - `Case ID: 456`  
    - `OR: 3`

**Frontend requirement:**

- A **Cart View** showing:
  - What is currently on Cart OR 3.
  - What has been logged as used for this case.

(For the prototype, detailed intra-op timing can be simplified.)

---

## 5️⃣ After Surgery: Cart Return & Refill

Surgery ends. Cart OR 3 is **half empty** and needs to be refilled.

### 5.1 End Case & Process Cart

**User (Assistant Doctor or Nurse):**

1. Brings `Cart OR 3` back to **Storage Room A**.
2. On the tablet, taps:  
   `End Case → Cart OR 3 → Case 456`

**System:**

- Shows a **Post-Case Processing** screen with 3 sections:

  1. **Unopened ampoules**  (as "amount_left_unopened" from section "leftover_used_med_list" in `story_1.json`)
     - Can be marked as `Return to Storage`.
  2. **Full, unused syringes**  (as "amount_left_opened" from section "leftover_used_med_list" in `story_1.json`)
     - Can be marked as `Move to Second-Chance Tray A`.


**User:**

- Scans:
  - 2 unopened ampoules → action: `Return to Storage`.
  - 1 full syringe of stable drug (e.g. Ephedrin) → action: `Second-Chance Tray`.

**System:**

- For ampoules:
  - Movement: `Cart OR 3 → Storage Room A`
  - Increases stock at main shelf.
- For syringe:
  - Movement: `Cart OR 3 → Second-Chance Tray A`
  - Starts **timer** (e.g. valid 6–24 hours).
  - Shows syringe on **Second-Chance overview** for all staff.
- Marks `Cart OR 3` as:  
  `Status: Needs refill`.

---

## 6️⃣ Refill by Storage Worker

### 6.1 Refill Task

**User (Storage Worker Alex):**

1. On his dashboard, sees a task:  
   `Cart OR 3 – Refill needed`
2. Opens the task and sees:
   - List of medications on the cart that are **below standard quantity**.
   - Suggested refill amount per medication.

**For the prototype:**

- Alex can simply tap `Mark as refilled` once he physically restocks the cart.

**System:**

- Resets `Cart OR 3` to its **standard template**.
- Logs a **refill movement summary**, e.g.:
  - `Storage Room A → Cart OR 3 – standard refill`
- Updates cart status to:  
  `Status: Ready for next case`.

---

## 7️⃣ What This Scenario Lets You Test in the Prototype

This single story allows you to test if the prototype supports:

1. **Case-based preparation**
   - Start from `Case + OR + Storage Room`.
   - Display standard medication checklist with stock + expiry.

2. **Smart shelves & stock movement**
   - Smart weighing shelves automatically detect when medications are taken and record movements from **Storage → Cart**.
   - For opioids, every removal from the locked box is logged as an audit-relevant **controlled substance** movement (via connected scale and/or scanner).

3. **Search & cross-department visibility**
   - Searching *Antibiotic Ertapenem* or Na Bicarbonate shows:
     - Anaesthesia: 0  
     - Other departments: where it exists
   - One-click contact or request: ICU, ED.

4. **Help requests to storage worker**
   - Create, display, and update **Help Requests**.
   - Show ETA updates (e.g. ICU → Anaesthesia in 10 minutes).

5. **Post-case cart handling**
   - Return unopened ampoules to storage.
   - Move full syringes to **Second-Chance Tray** with a timer.
   - Flag cart as **Needs refill**.

6. **Refill workflow**
   - Storage worker sees carts waiting for refill.
   - Can confirm refill and set status back to **Ready**.

If your frontend can “play through” this entire story using the prototype, step by step, you will have a realistic and understandable demo of the **Medication Stock Tracking in Anaesthesia** system.
