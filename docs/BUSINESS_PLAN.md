# Project Fitness business plan

Version 0.1 · 20 September 2026 · Working decisions, with explicit validation gaps.

## The business to test

Build a trusted explanation-and-application business for recreational lifters whose plans run into time, schedule or equipment constraints. Use the existing **Project Fitness** brand and **DEX** host to help someone understand a decision, preserve the limits of the evidence and apply a simple tool.

The channel is the discovery layer. Useful worksheets begin an owned relationship. A paid decision toolkit is the first commercial hypothesis. A subscription is a later option if customers repeatedly need the service and actually renew.

Success means useful decisions and sustainable customer economics, including founder time. Follower count, publishing volume and AI output volume are intermediate observations.

## Customer and problem

The initial audience hypothesis is adults already attempting resistance training who face recurring practical friction. Their problem is not simply a lack of workout PDFs. They may struggle to adapt an existing plan without losing its purpose, or to interpret conflicting advice without restarting everything.

| Segment | Trigger | Existing alternatives | What to investigate |
| --- | --- | --- | --- |
| Time-constrained recreational lifter | Sessions regularly exceed available time | Shorter plans, supersets, dropping exercises | Actual time loss, acceptable tradeoffs and current workarounds |
| Equipment-constrained lifter | Busy gym, travel or changing access | Apps, substitutions, asking a coach | What must be preserved and where they need qualified help |
| Research-curious lifter | A confident new study headline | Creators, research subscriptions, forums | Whether interpretation changes a meaningful decision |

Do not target rehabilitation, individualized medical treatment, children, or automated injury assessment in this pilot. The brand can eventually serve broader START / BUILD / DEEP audiences, but the initial acquisition message should describe one recognizable problem.

Interview 12–15 target viewers about recent events and workarounds. Recruit across varied training experience and budgets; document convenience-sample bias. Interview scripts are in research/CUSTOMER_RESEARCH.md. No interviews have been conducted.

## Competition and differentiation

The review includes five channels and eleven channel/product businesses. Thirty public video listings are recorded separately; those listings are not full-video or transcript analysis.

Illustrated explanations, research interpretation, transformation stories, training plans, apps and human coaching already exist. Stronger by Science currently offers a substantial free program bundle. Generic information alone is therefore a weak paid-offer hypothesis. [SBS program bundle](https://www.strongerbyscience.com/program-bundle/), [competitor observations](../research/competitors.csv).

DEX's proposed distinction is **a clear decision, the evidence that informs it, the limits that matter, and a reusable application tool**. This is a positioning hypothesis, not a demonstrated market gap.

The advantages to build are original explainers, accurate source-to-claim records, owned production assets, customer relationships and measured knowledge about what works. Shared access to image or language models is not sufficient differentiation.

## Brand and editorial product

Retain the user's DEX guide: navy, lime and cream; the promise “Evidence you can actually use”; the line “Know why. Train better.” The host is a fictional editorial character, with real human accountability for the content.

The initial prototypes use a DEX label and clear cards, not the finished character rig. Complete the owned character design only after the explanation direction is useful. Avoid imitation of Trainer Winny's mascot or specific compositions.

Voice: plain language, specific questions, calibrated conclusions and humor directed at inflated claims. Do not attach an evidence badge solely because a review contains many studies. Confidence and applicability vary by outcome.

The current decision cluster:

1. Where does session time go?
2. What should a useful exercise substitution preserve?
3. When should a new study change a decision?

These are preparation tools for reasoning, not individualized training prescriptions.

## Acquisition and go-to-market

Use one primary discovery channel initially: YouTube. Pair each topic with a directly relevant free worksheet. Offer an email relationship with clear consent and reliable delivery. Publish one complete, reviewed topic first; the three-topic pilot preparation can run concurrently without launching three separate channels.

Pilot distribution sequence:

- Calibrate the scripts and comprehension instrument with a small separate group.
- Run the randomized sequence screening described in docs/EXPERIMENTS.md.
- Choose a supervised release direction using comprehension, observed caveats and practical feedback.
- Publish one body version per topic. Test packaging within the same eligible YouTube video when the native tool is available.
- Use a short derivative only when it remains accurate on its own and has a working destination.
- Observe source, view window, resource use and email engagement; review a batch before increasing cadence.

No paid acquisition is assumed. No Reddit promotion or unsolicited outreach has been sent. Forums inform problem discovery; any participation should fit the actual community and provide useful, transparent contributions.

A tentative one-episode-per-week cadence becomes a commitment only after measured research, review, recording and editing time fit the founder's available hours. The backlog is a sequence of candidates, not twelve production promises.

YouTube's native title/thumbnail testing chooses on watch time and can be inconclusive. It is not the same experiment as comparing two body scripts. [Official test guidance](https://support.google.com/youtube/answer/16391400?hl=en).

## Offer ladder and recurring revenue

| Stage | Concrete deliverable | What it must prove |
| --- | --- | --- |
| Free resource | Session audit, substitution questions, or study-to-decision card | A viewer can complete one useful decision |
| One-time paid pilot | A guided toolkit with examples, worksheets and a bounded group walkthrough | Someone pays for a clearly scoped application benefit |
| Optional recurring service | Reviewed decision updates, application sessions and a maintained case library | Customers need the service again, use it and renew |
| Later adjacent income | Appropriate sponsors, affiliates, ads, additional products | Editorial independence, fit and actual net contribution |

The free worksheet files exist in offers/. The paid service is scoped in offers/PAID_PILOT.md and has not been built or sold.

Earlier planning examples of $29 one-time and $19/month remain **price hypotheses**. Do not launch both simultaneously and call a small self-selected cohort a price elasticity experiment. First verify scope and fulfillment, then test a concrete offer with explicit terms. A waitlist click is not payment, and a purchase is not retention.

Do not charge monthly for a one-off download unless a real continuing service is being provided. Build a one-time purchase route if the value is naturally episodic. One-time sales, sponsorships and ad income do not count as MRR.

## Activation, retention and service

Activation is the first completed useful decision artifact, measured with the customer's consent. Recurrence is a second relevant use on another occasion. Record the problem, resource version and event date without collecting unnecessary health data.

A proposed paid pilot has a maximum of ten customers so support load can be measured. This is an operating choice, not a market sample-size claim. Observe setup, questions, repeat use, refund reasons and any actual renewal. Define access, response windows, cancellation and failure handling before checkout.

Use a short onboarding route: receive resource → choose current problem → complete one example → make the next question concrete. The draft emails in offers/EMAILS.md need a real sender, domain, address, unsubscribe mechanism and checked links before use.

## Economics and constraints

The founder has not supplied a weekly time budget, maximum acceptable loss, launch geography, professional reviewer or target owner income. These remain null in config/business.json. Local prototype production spends no paid generation credits.

A planning example uses 100 members at $19/month, a 6% fees/refunds reserve, $4 variable cost per member, $600 fixed cost and 40 founder hours valued at $50/hour. It gives $1,900 gross MRR, $786 contribution before founder time and **-$1,214** after that time. Cash breakeven is 44 members; labor-inclusive breakeven is 188. These are arithmetic assumptions, not predictions or actual vendor fees.

Recalculate with:

~~~bash
python -m fitness_os economics config/economics.example.json
~~~

Track actual cash cost per accepted episode and per useful customer outcome. Include failed generations, rework, tools, review, storage, support and acquisition. Reserve uncertain provider spend until reconciled. Confirm pricing, taxes and payment requirements for the actual business before sales.

RevenueCat's subscription report can inform which cohort questions to ask; its selected subscription-app population is not a forecast for a creator membership. [Report](https://www.revenuecat.com/state-of-subscription-apps/).

## Decision gates

These gates are business judgments; none turns a small convenience sample into representative validation.

| Gate | Evidence needed | Continue / revise |
| --- | --- | --- |
| Problem | Several independent recent examples of the same costly friction and observable workarounds | Narrow the problem if interest is abstract or infrequent |
| Explanation | Reviewed stimuli, calibrated instrument, target-viewer comprehension and caveat retention | Repair systematic misunderstanding before release |
| Acquisition | Actual eligible impressions, watch time and relevant resource actions over fixed windows | Diagnose packaging, topic and offer separately |
| Paid value | A concrete delivered offer, actual payments, activation and support time | Revise if sales depend on a promise the product does not fulfill |
| Recurrence | Repeated use, reasons for staying, actual renewals and sustainable support | Prefer one-time products when ongoing service has little use |
| Expansion | Repeatable first-brand economics, maintainable operations and a second-domain reviewer | Reuse the core only after supplying new domain evidence |

No commercial gate has passed. At the current stage the useful outcome is a reviewable prototype and clear next observation, not an asserted winner.

## Operating ownership and expansion

Initially the founder owns editorial decisions, audience contact, budget and product promises. AI assists with retrieval, extraction, drafts, comparisons and code. Deterministic code owns calculations, artifact identity and local state changes. A qualified reviewer is still needed for material fitness interpretation.

Keep the core reusable through stable content, claim, asset, experiment and release contracts. Start another domain in a separate project root with its own evidence, accounts, reviews and data. Do not clone fitness credibility into unrelated advice. The current implementation is a local foundation; hosted access, customer fulfillment and unattended operations are future integration work.
