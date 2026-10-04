# Kestrel Freightworks — On-call Runbook

Owner: Platform Reliability team (lead: Tomasz Wierzbicki)
Last reviewed: 12 August 2026

## 1. Rota

- On-call shifts run **Friday 18:00 IST to Friday 18:00 IST** (one week).
- Each shift has a **primary** and a **secondary** engineer.
- The rota is published in the Perch portal under "Rota > Platform".
- Swaps must be agreed by both engineers and posted in the `#heron-oncall` Slack channel at least 48 hours before the shift starts.

## 2. Allowance

| Item | Amount |
|---|---|
| Weekday on-call (per night, primary) | ₹1,150 |
| Weekend on-call (Saturday + Sunday, primary) | ₹3,450 |
| Secondary on-call | 50% of the primary amount |
| Each call-out answered between 00:00 and 06:00 | ₹900 extra |
| Public holiday on-call | Double the weekend amount |

Allowances are paid with the next month's salary. Claim them in Perch under "Claims > On-call".

## 3. Severity levels

| Severity | Meaning | Acknowledge within | Who to wake up |
|---|---|---|---|
| SEV-1 | Customer shipments not moving, or data loss | 5 minutes | Primary, secondary and the Duty Manager |
| SEV-2 | One region or one major feature degraded | 15 minutes | Primary |
| SEV-3 | Minor bug, workaround exists | Next working day | Nobody, raise a ticket |

## 4. First steps for any page

1. Acknowledge the page in PagerTree.
2. Open an incident channel named `#inc-<yyyymmdd>-<short-name>`.
3. Check the **Heron dashboard** (Grafana, folder "Heron / Core") for the failing service.
4. If the problem started within 30 minutes of a deployment, roll back first and investigate later.
5. For SEV-1, call the Duty Manager on the bridge number **+91 80 4719 2266**.

## 5. Known issues

- **Heron sorter queue backlog:** if `heron_sorter_queue_depth` goes above 40,000 messages, restart the `sorter-consumer` pods one at a time. Never restart all of them together, as this caused the March 2026 incident.
- **Gannet label printer timeouts:** usually caused by the warehouse Wi-Fi, not by our code. Raise it with the Warehouse IT desk (extension 4402).

## 6. Quiet Week

The rota continues during Quiet Week. Allowances during Quiet Week are paid at the public holiday rate.
