# 🤖 Agentic Demo

**A Minimal Demonstration of Agentic Frameworks**

**Agentic Demo** is a lightweight demonstration project showcasing **agentic system design** using a simple, concrete business case:
an **automated shirt customization service**.

Built as a collaborative project by **David & Ethan**, this repo illustrates how multiple specialized agents can collaborate to validate user input and compute business outcomes autonomously.

---

## 🧠 Concept

The demo models a small agentic workflow where each agent is responsible for a clearly defined domain of reasoning:

* One agent focuses on **correctness & constraints**
* Another focuses on **pricing & computation**

Despite the simplicity of the example, the structure mirrors real-world agentic systems used in product configuration, pricing engines, and automated decision pipelines.

---

## 🧩 Agents

### 🧑‍🎨 Agent A — Customization Agent

Responsible for validating all user selections:

* Shirt size
* Color
* Design style
* Custom text

Ensures:

* Inputs are valid and supported
* Selections comply with business rules
* Requests are internally consistent before pricing

---

### 💰 Agent B — Pricing Agent

Computes the final price dynamically based on:

* Base shirt price
* Size-based multiplier
* Design complexity cost
* Additional custom text cost

Outputs a deterministic price once customization has been approved.

---

## 🔄 Example Flow

1. User submits shirt customization request
2. **Agent A** validates all inputs
3. If valid, request is passed to **Agent B**
4. **Agent B** computes and returns a final price
5. System responds with a completed order summary

---

## 🖼️ Visual Overview

![Agent Flow Diagram](https://github.com/user-attachments/assets/158d57c6-48eb-4591-b9c9-67e19a6e600a)

> *Yes — basically this, but 🦮 coded.*

---

## 🎯 Purpose

This project is intentionally minimal and designed to:

* Demonstrate **agent separation of concerns**
* Show how agents can **coordinate without monolithic logic**
* Provide a clear, teachable example of agentic frameworks in practice

It is not intended to be production-ready, but rather **educational and illustrative**.

---

## 👥 Contributors

* **Ethan Leigh-Fellows**
* **David Fellows**

---

## 📜 License

This repository is provided for demonstration and educational purposes.
Refer to the LICENSE file for full terms.

---
