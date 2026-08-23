# Architecture and analytical logic

## End-to-end flow

1. Generate or receive operational data.
2. Store operational data in Google Sheets / Excel.
3. Aggregate business KPIs into a Data Mart.
4. Run queueing simulation for service capacity.
5. Run linear optimization for modeled sales / profit constraints.
6. Run leakage-free Random Forest scoring for client prioritization.
7. Publish results in Power BI.
8. Use outputs for management decisions.

## Decision map

| Management question | Analytical component | Main output |
|---|---|---|
| What is happening with sales and contracts? | Data Mart / KPI logic | Profit, sales, contracts |
| Is the call-center capacity sufficient? | M/M/m simulation | Utilization, queue, waiting, abandonment |
| How many employees are needed? | Queueing + recommendation loop | Recommended staff |
| What sales volume is optimal under assumptions? | Linear programming | Optimal sales / modeled profit |
| Which clients should be prioritized? | Leakage-free Random Forest | Contract propensity score |
| How should the results be consumed? | Power BI | Management dashboards |

## Queueing model

The notebook implements an M/M/m-style simulation with a finite patience threshold. Main parameters include arrival intensity, service intensity, number of service channels, maximum waiting time, simulation horizon and replications.

## Optimization block

The notebook contains a linear-programming block using `scipy.optimize.linprog`. The modeled objective is to maximize profit from sales subject to the project constraints.

## ML block

The corrected ML module deliberately excludes post-outcome `Стадия работы с клиентом` from the feature matrix. The benchmark target is generated from pre-outcome client attributes, and evaluation uses a hold-out split plus out-of-fold predictions.
