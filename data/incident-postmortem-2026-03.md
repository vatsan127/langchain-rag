# Postmortem — Heron Sorter Outage, 17 March 2026

Severity: **SEV-1**
Incident channel: `#inc-20260317-sorter-outage`
Incident commander: Tomasz Wierzbicki
Author: Anjali Mukherjee (Platform Reliability)

## Summary

On 17 March 2026, shipments stopped moving through Heron for **2 hours 47 minutes** (14:12 to 16:59 IST). About **31,800 shipments** were delayed for 22 customers.

## Timeline (IST)

| Time | Event |
|---|---|
| 13:55 | Heron 7.1.4 deployed with a change to the sorter retry logic |
| 14:12 | `heron_sorter_queue_depth` crosses 40,000; SEV-2 page sent |
| 14:20 | On-call engineer restarts **all** `sorter-consumer` pods together |
| 14:23 | All consumers try to rebalance at once; the queue stops being consumed completely. Upgraded to SEV-1 |
| 15:10 | Duty Manager joins the bridge |
| 16:40 | Deployment 7.1.4 rolled back to 7.1.3 |
| 16:59 | Queue drained, shipments moving again |

## Root cause

1. The retry change in 7.1.4 re-queued failed messages without a delay, so the queue grew quickly.
2. Restarting all `sorter-consumer` pods at the same time caused a rebalance storm, which turned a slowdown into a full outage.

## What went well

- The page fired within 1 minute of the threshold being crossed.
- Customers were informed within 25 minutes.

## What went badly

- The rollback happened **2 hours 45 minutes** after the deployment. The runbook rule "roll back first if the problem started within 30 minutes of a deployment" was not followed.

## Actions

| Action | Owner | Status |
|---|---|---|
| Add "restart pods one at a time" to the runbook | Tomasz Wierzbicki | Done |
| Add a delay of 30 seconds to sorter retries | Anjali Mukherjee | Done in Heron 7.2 |
| Customer credit of 10% for March for the 22 affected customers | Meenakshi Duraisamy | Done |
| Automatic rollback when queue depth doubles within 15 minutes of a deployment | Platform Reliability | Open, target Heron 7.4 |
