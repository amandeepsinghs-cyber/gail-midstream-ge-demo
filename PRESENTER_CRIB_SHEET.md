# Presenter Crib Sheet: "The Winter Call" (V4, extended)
*One page. Print it or keep it on a second screen.*

---

## 1. Your opening (say this first)
> "Every critical decision at GAIL needs data from many systems: our contracts, our tanks, our customers, SAP, and the market outside.
> Today I'll show how Gemini Enterprise gathers that **data**, **analyses** it, helps our experts **decide**, and **acts** on it, in one conversation."

## 2. The business problem (memorise)
> "Qatar LNG is under force majeure, so GAIL is short of gas this winter. Prices are near record highs and nobody knows where they go next.
> **The call: do we lock in replacement cargoes now, or wait for prices to fall?**"

## 3. The one message to repeat
**Market data alone can't make this call, and neither can our internal data alone. Gemini Enterprise brings them together, and then acts.**
- 🏢 **GAIL data:** contract book, customer demand, Dahej inventory, SAP orders and budget, risk policy, approval rules.
- 🌐 **Outside data:** live prices (Yahoo Finance), news (Google Search), analyst forecasts.
- *"Bloomberg knows the market. SAP knows GAIL. Only Gemini Enterprise puts them in one decision."*

---

## 4. The seven prompts (paste in order, same chat)

> [!IMPORTANT]
> Prices are **live** and change daily. The numbers below are from the 24 Sep rehearsal. **Read them off the screen.**

| # | Stage | Paste | Point at | Say |
|---|---|---|---|---|
| 1 | **Data:** the problem | What is the impact of the Qatar force majeure on our winter gas supply? | **6 cargoes short**, **₹184 Cr per $1** | "It read our contract book and today's news together. We are six cargoes short this winter." |
| 2 | **Data:** our own books | Check our own position: inventory, customer commitments. | ⏱️ **Deadline: 17 Oct (23 days)**, tanks can't cover a missed month | "Now our own systems: tanks, customers, open orders, budget. No market terminal has this. And there's a deadline: we can only wait 23 days for the December cargoes." |
| 3 | **Data:** the market | What is gas costing today, and what does that mean for our contracts and our budget? | US cargo **~$10.9** vs spot **~$24.9**; lock-in **₹540 Cr over budget** | "Live prices, applied to **our** contracts and **our** SAP budget. Locking in today costs more than we budgeted." |
| 4 | **Analysis:** context | How have gas prices moved over the last 5 years, and what drove them? | The 2022 and 2026 spikes | "This market swings hard. That is what makes waiting risky." |
| 5 | **Analysis:** outlook | What do the experts expect? | Consensus below today, wide spread | "Experts expect prices to fall, but they disagree by how much. So waiting is a bet." |
| 6 | **Analysis → Decision** | Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend? | **10,000 simulated futures**, **lock in 6 of 6**, worst case vs **₹800 Cr limit** | "This isn't gut feel. It simulated 10,000 possible winters and tested each option against our risk limit and deadlines. Waiting might save a little, but the downside breaks our limit. Recommendation: lock in now. The Director still decides." |
| 7 | **Action** | Prepare the approval and stage it in SAP. | Approver, memo link, **SAP: AWAITING APPROVAL** | "It picked the right approver from our delegation rules, wrote the memo and staged the order in SAP. Nothing moves until a human approves." |

**Close:**
> "Seven questions, one conversation: our data and the market's, then analysis, then a decision, then action.
> Bloomberg knows the market. SAP knows GAIL. **Only Gemini Enterprise puts them in one decision.**"

*Optional 8th prompt if asked:* **Why do we need Gemini Enterprise for this?** (the agent answers in its own words)

---

## 5. Plain-English words
- **TTF / Henry Hub / Brent** → "European, US and oil benchmark prices."
- **Force majeure** → "Qatar legally can't deliver."
- **Monte Carlo** → "we simulate 10,000 possible winters and see how each option does." **Worst case (P95)** → "the worst 1 in 20."
- **Lead time** → "you have to order a cargo about six weeks before it arrives."
- **Delegation of authority** → "who is allowed to sign for a purchase of this size."

## 6. Safe answers to likely questions

| If they ask… | Say |
|---|---|
| Is this real GAIL data? | "Market data is live. The contracts, inventory, SAP orders and policy are sample data in a data lake. Plug in the real systems and the same flow runs." |
| News says Qatar restarts in November | "Maybe. We can't plan a winter on maybe, and the December deadline is in 23 days. That's why we size the risk." |
| Is it always 'lock in'? | "No. It depends on today's prices, our risk limit and our deadlines. Change the limit and it can say 'lock in half'." |
| Why not ChatGPT or Bloomberg? | Ask the agent: **"Why do we need Gemini Enterprise for this?"** |
| Will it act on its own? | "No. It stages the SAP order; a human approves." |
| Something technical you don't know | "Great question for your traders and our engineers. Let's take it offline." |

## 7. If something breaks
- Card doesn't show → type **"Show that as a chart."**
- It stalls → open a **new chat** and restart from prompt 1.
- Memo link slow → **"Summarise the approval in three bullets."**

**Before you go on:** warm up with prompts 1–2 in a separate chat 15 minutes before, note today's numbers and the deadline, check today's Qatar news, then open a fresh chat for the stage.
