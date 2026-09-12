# Supply Prescript - Data Quality Report

## Dataset Overview

| Metric | Value |
|---|---:|
| Rows | 10,324 |
| Columns | 47 |
| Duplicate Rows | 0 |
| Duplicate Shipment IDs | 0 |
| Missing Cells | 34,948 |
| Missing Percentage | 7.20% |

## Delay Target

| Metric | Value |
|---|---:|
| Delay Rate | 11.49% |
| Average Delay | -6.02 days |
| Maximum Delay | 192 days |

## Shipment Modes

- **Air**: 6,113
- **Truck**: 2,830
- **Air Charter**: 650
- **Ocean**: 371
- **Unknown**: 360

## Product Groups

- **ARV**: 8,550
- **HRDT**: 1,728
- **ANTM**: 22
- **ACT**: 16
- **MRDT**: 8

## Top Countries

- **South Africa**: 1,406
- **Nigeria**: 1,194
- **Côte d'Ivoire**: 1,083
- **Uganda**: 779
- **Vietnam**: 688
- **Zambia**: 683
- **Haiti**: 655
- **Mozambique**: 631
- **Zimbabwe**: 538
- **Tanzania**: 519

## Numerical Statistics

|       |   line item quantity |   line item value |   weight (kilograms) |   freight cost (usd) |   actual_delay_days |
|:------|---------------------:|------------------:|---------------------:|---------------------:|--------------------:|
| count |              10324   |   10324           |              6372    |              6198    |            10324    |
| mean  |              18332.5 |  157651           |              3424.44 |             11103.2  |               -6.02 |
| std   |              40035.3 |  345292           |             13527    |             15813    |               27.23 |
| min   |                  1   |       0           |                 0    |                 0.75 |             -372    |
| 25%   |                408   |    4314.59        |               206.75 |              2131.12 |               -3    |
| 50%   |               3000   |   30471.5         |              1047    |              5869.66 |                0    |
| 75%   |              17039.8 |  166447           |              3334    |             14406.6  |                0    |
| max   |             619999   |       5.95199e+06 |            857354    |            289653    |              192    |

## ML Target Definition

### delay_flag

A shipment is classified as delayed when:

`actual delivery date > scheduled delivery date`

`delay_flag = 1` means delayed.
`delay_flag = 0` means on-time.

## Target Leakage Prevention

The following outcome columns must NOT be used as model input features:

- `actual_delay_days`
- `delay_flag`
- `delivered to client date`

These values are only known after the shipment outcome.

## Data Pipeline

Kaggle Dataset -> Data Cleaning -> Feature Engineering -> Quality Validation -> PostgreSQL

## Status

Dataset preparation is complete and ready for the Day 3 machine-learning pipeline.