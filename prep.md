# Instawork Interview Prep

## Stack
- **Backend:** Django + FastAPI + Python
- **Frontend:** React
- **Domain:** Two-sided labor marketplace (businesses post shifts, workers apply/get matched)
- **Interview:** 3 hours, Claude Code allowed

---

## Instawork's Current AI Features (Research)

### Core Matching Engine
- 600M+ matches using signals: ratings, shift history, certifications, reliability scores
- Trained on 8M+ worker onboardings and 8M shifts
- Fills 97% of shifts within 24 hours

### "Hiring" Product (Jan 2025)
- Extended AI matching from gig work into permanent placement
- Uses verified work histories + AI-assessed skills instead of resumes
- Single platform covering temp, long-term temp, and permanent roles

### Conversational AI & Vetting
- 24/7 conversational AI for worker screening
- Automated background/document verification
- Video-based skill assessments (Project Horizon)
- Predictive no-show risk + auto-fill with backup workers

### Robotics Division (newer)
- Instawork Lens — data collection platform for robotics training data
- Instacore (June 2026) — wearable rig workers use to capture physical AI training data
- 20,000+ workers enrolled in robotics certification

---

## Practice Projects

### Project 1: Shift Posting & Application Flow
**The core of their entire business.**

**What to build:**
- Business can create a shift (title, pay rate, start time, end time, required skills, location)
- Workers can browse open shifts and apply
- Business reviews applicants and accepts or rejects
- Accepted worker sees their confirmed shift

**Backend (FastAPI + SQLAlchemy):**
- Models: `Business`, `Worker`, `Shift`, `Application`
- Endpoints: `POST /shifts`, `GET /shifts`, `POST /shifts/{id}/apply`, `PATCH /applications/{id}` (accept/reject)

**Frontend (React):**
- Business view: shift creation form + applicant list per shift
- Worker view: shift feed + apply button + my applications tab

**Practice goal:** Get this working end-to-end including auth (JWT) in under 3 hours.

---

### Project 2: Worker Profile & Reliability Score
**Their matching engine depends entirely on worker signals.**

**What to build:**
- Worker fills out profile (skills, certifications, years of experience, availability by day)
- After each shift, business rates the worker (1-5 stars, punctuality, professionalism)
- System calculates a reliability score (average rating + attendance rate)
- Score is visible to businesses when they view applicants

**Backend:**
- Models: `WorkerProfile`, `ShiftRating`, computed `reliability_score`
- Endpoints: `PUT /workers/profile`, `POST /ratings`, `GET /workers/{id}/score`

**Frontend:**
- Worker: profile edit page
- Business: applicant card showing score + badge (Excellent / Good / Fair)

**Practice goal:** Think about how to weight the score — this shows product instinct.

---

### Project 3: Shift Recommendation Feed
**Their "AI" matching is fundamentally a ranking/filtering problem.**

**What to build:**
- Worker logs in and sees a personalized feed of shifts
- Ranking logic: shifts matching their skills rank higher, closer location ranks higher, higher pay ranks higher
- Filter bar: by date, pay rate, skill required
- "Not interested" button that removes a shift from feed

**Backend:**
- `GET /shifts/recommended` — takes worker ID, returns ranked list
- Scoring function: `score = skill_match * 0.5 + pay_normalized * 0.3 + distance_score * 0.2`

**Frontend:**
- Feed with shift cards (title, pay, time, match %)
- Filter sidebar
- Skeleton loading state

**Practice goal:** This is the most interview-likely feature. Know how to build a simple scoring function fast.

---

### Project 4: Business Dashboard
**Businesses need operational visibility into their shifts.**

**What to build:**
- Dashboard with 3 tabs: Upcoming, Active, Past
- Each shift card shows: time, worker name, reliability score, status
- No-show flagging — if shift start time passes and worker hasn't checked in, flag it red
- Simple stats: total shifts this month, avg fill time, avg worker rating

**Backend:**
- `GET /businesses/{id}/shifts?status=upcoming|active|past`
- `POST /shifts/{id}/flag-noshow`
- `GET /businesses/{id}/stats`

**Frontend:**
- Tab-based layout
- Color-coded status badges
- Stats cards at top

**Practice goal:** Build a clean, usable dashboard UI fast. Shows product instinct.

---

### Project 5: Two-Sided Rating System
**Ratings are the data that powers everything else.**

**What to build:**
- After a shift ends, both worker and business get a rating prompt
- Business rates worker: stars + tags (On Time, Professional, Skilled, No Show)
- Worker rates business: stars + tags (Good Environment, Fair Pay, Well Organized)
- Ratings are locked after 48 hours
- Ratings are public on profiles

**Backend:**
- `POST /ratings/worker` and `POST /ratings/business`
- Validation: shift must be completed, rating window must be open, can only rate once
- `GET /workers/{id}/ratings` and `GET /businesses/{id}/ratings`

**Frontend:**
- Post-shift rating modal (star selector + tag chips)
- Rating history on profile pages

**Practice goal:** Practice business logic validation on the backend — this is where bugs hide.

---

### Project 6: LLM-Powered Worker Screening
**Their newest AI feature area — conversational vetting.**

**What to build:**
- When a worker applies for a shift, they go through a 3-question AI screening
- Questions are generated based on the shift requirements (e.g. "This shift requires forklift experience. Describe your experience.")
- Worker types responses
- LLM scores the responses and returns: fit score (1-10) + one-line summary
- Business sees the AI summary next to the applicant

**Backend (FastAPI):**
- `POST /screening/generate-questions` — takes shift requirements, returns 3 questions via Claude API
- `POST /screening/evaluate` — takes worker answers, returns score + summary

**Frontend:**
- Step-by-step question flow (one question at a time)
- Business applicant view: "AI Assessment: 8/10 — Strong forklift background, 3 years warehouse experience"

**Practice goal:** Integrating an LLM call into a real product flow, not just a chatbot.

---

## Practice Order

| Order | Project | Why |
|---|---|---|
| 1st | Shift Posting & Application | Foundation — everything else depends on it |
| 2nd | Worker Profile & Reliability Score | Adds depth to worker side |
| 3rd | Shift Recommendation Feed | Most likely interview ask |
| 4th | Business Dashboard | Shows product thinking |
| 5th | Two-Sided Rating | Solidifies backend validation skills |
| 6th | LLM Screening | Advanced — do last |
