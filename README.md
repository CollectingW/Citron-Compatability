# 🍋 Citron Compatibility Database

Welcome to the official compatibility tracking repository for the **Citron Emulator**. This project serves as a centralized, community-driven database to document how well games perform on Citron. 

By leveraging GitHub’s Issue Forms and automated CI/CD pipelines, we ensure that compatibility data is always up-to-date and accessible directly within the emulator.

---

## 🚀 How It Works: The Lifecycle of a Report

We have designed a seamless bridge between the Citron Emulator and this GitHub Repository. Here is the step-by-step process:

### 1. In the Emulator
* **Action:** A user right-clicks a game in their Citron game list and selects **"Submit Compatibility Report."**
* **Handshake:** The emulator checks the game's Title ID and Name. 
* **User Confirmation:** A dialog appears, reminding the user that a GitHub account is required to submit the report. 

### 2. The Browser Hand-off
* Once confirmed, Citron generates a specialized URL that points to this repository’s Issue Form.
* **Auto-fill:** Using the `compat.yml` template, the URL automatically populates the **Game Name** in the title and the **Title ID** in the form field.
* **User Input:** The user only needs to select the **Status** (Perfect, Playable, etc.) and type their hardware specs or any glitches they encountered in the **User Notes** section.

### 3. Verification & Automation
* **Submission:** Once the user hits "Submit," a new issue is created in this repository.
* **Triage:** Maintainers review the report. Once it is confirmed to be accurate, the label `verified` is added to the issue.
* **The Script:** A background Python script (`generate_list.py`) runs via GitHub Actions. It scans all issues with the `verified` label and compiles them into `compatibility_list.json`.

### 4. Full Circle: Syncing back to Citron
* **Auto-Update:** Every time a user launches Citron, the emulator checks this repository for an updated `compatibility_list.json`.
* **UI Feedback:** The "Compatibility" column in the Citron game list updates instantly, showing the community-reported status icon for every game in the user's library.

---

## 📊 Compatibility Ratings Defined

To keep reports consistent, we use the following standard ratings:

| Rating | Description |
| :--- | :--- |
| **Perfect** | The game plays exactly as it does on original hardware with no noticeable glitches. |
| **Playable** | The game can be finished from start to finish with minor graphical or audio bugs. |
| **Ingame** | The game boots and goes past the menus, but crashes or has major issues that prevent completion. |
| **Intro/Menu** | The game boots but hangs or crashes at the title screen or main menu. |
| **Won't Boot** | The game crashes immediately upon launching or results in a black screen. |

---

## 🛠️ For Developers & Contributors

### Repository Structure
- **`.github/ISSUE_TEMPLATE/compat.yml`**: The form configuration that defines the submission layout.
- **`generate_list.py`**: The logic engine that converts GitHub issues into machine-readable JSON.
- **`compatibility_list.json`**: The final output consumed by the Citron Emulator.
