# Data dictionary

## `ЦД1` source data

### Деньги

| Field | Meaning |
|---|---|
| Дата | Observation date |
| Расходы | Expenses |
| Объем продаж | Sales volume |

### Сотрудники

| Field | Meaning |
|---|---|
| Дата | Observation timestamp |
| Количество работающих сотрудников | Active staff count |
| Количество звонков в час | Incoming calls per hour |

### Клиенты (historical)

| Field | Meaning |
|---|---|
| Дата | Observation date |
| Количество завершенных договоров | Completed contracts |
| Количество новых договоров | New contracts |

### Клиенты_компании

| Field | Meaning |
|---|---|
| ID клиента | Client identifier |
| Тип компании | Client company segment |
| Прибыль компании-клиента | Client-company profit |
| Постоянный или новый клиент | Customer status |
| Стадия работы с клиентом | Sales / contract stage |
| Потребность клиента в товаре | Product need level |

## Analytical outputs

### Data Mart

The sample Data Mart contains `ID клиента` and `Вероятность заключения договора`.

### SМО

The sample output contains staffing and service metrics such as current staff, calls per hour, utilization, waiting time, waiting probability, abandonment probability, lost calls, average queue length, recommended staff and management recommendation.
