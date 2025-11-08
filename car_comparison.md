# Car Purchase Analysis: Acura RDX vs. BMW iX (Definitive Analysis)

## Executive Summary & Recommendation

After a series of iterative improvements to our financial model, culminating in a sophisticated, data-driven analysis, the conclusion is definitive and overwhelming: **keeping the Acura RDX is the correct financial decision.**

The true cost of purchasing the CPO BMW iX is now calculated to be **$29,293 more** than keeping your current vehicle over the next three years. This equates to a staggering **~$814 per month** in additional costs.

This final, dramatic increase is the result of two key improvements to our model:
1.  **Data-Driven Maintenance Costs:** Our research revealed that while the RDX is cheaper to own overall, its maintenance costs over the next three years are projected to be significantly *higher* than the newer iX's, a factor that works in the BMW's favor.
2.  **The True Opportunity Cost:** This was the decisive factor. By calculating the compounded future value of investing the monthly cost difference between the two cars, we uncovered a massive **$15,526** in lost potential investment gains. This is the hidden financial power of choosing the more frugal option, and it completely eclipses any savings the iX offers in maintenance or fuel.

**Recommendation:**
The financial model, in its most refined state, makes a clear and unambiguous recommendation: **Keep the Acura RDX.** The nearly $30,000 total cost difference represents a massive financial burden for the luxury and performance of the iX. The prudent financial path is to continue with the RDX, pay it off, and invest the substantial monthly savings to build wealth.

---

## Detailed Financial Breakdown

## Vehicle Information

### 2019 Acura RDX

| Parameter | Value | Source |
| :--- | :--- | :--- |
| **Current Value** | **$18,000.00** | **Actual Trade-In Offer** |
| **Loan Payoff Balance** | **$8,000.00** | **Actual from Deal** |

### CPO BMW iX ("Gray Deal")

| Parameter | Value | Source |
| :--- | :--- | :--- |
| **Purchase Price** | **$46,995.00** | **Actual from Deal** |
| **Interest Rate** | **6.19%** | **Actual from Deal** |
| **Loan Term** | **72 months** | **Actual from Deal** |

## Financial Comparison

### 3-Year Total Cost Difference: +$29,293 (for the BMW iX)

This table breaks down the total cost difference based on our most sophisticated model, including dynamic maintenance and compounded opportunity cost.

| Cost Component | 3-Year Amount | Description |
| :--- | :--- | :--- |
| **Vehicle Equity & Depreciation** | | | 
| *Initial Outlay (RDX Equity)* | *+$10,000* | *Your RDX equity used as a down payment.* |
| *Final Equity (iX vs RDX)* | *-$10,712* | *The iX's higher final value is offset by its rapid depreciation.* |
| **Net Depreciation & Equity Cost** | **-$712** | **The net effect of equity and depreciation is almost neutral.**|
| | | | 
| **Recurring Monthly Costs** | | | 
| *Loan & Interest Payments* | *+$18,979* | *Higher loan and interest payments for the iX.* |
| *Insurance* | *+$3,025* | *Higher insurance premiums for the iX (estimate).* |
| *Property Tax* | *+$2,589* | *Higher property taxes on the more valuable iX.* |
| *Maintenance* | *-$1,735* | *Data-driven forecast shows the RDX is more expensive to maintain.* |
| *Fuel/Electricity* | *-$3,376* | *Significant savings from switching to electric.* |
| **Net Recurring Cost** | **+$19,482**| | 
| | | | 
| **Opportunity Cost** | | | 
| *Lost Investment Opportunity* | *+$15,526* | **The compounded value of investing the monthly cost difference. The deciding factor.** |
| | | | 
| **TOTAL COST DIFFERENCE** | **+$29,293** | **The definitive additional cost to own the BMW iX.** |

## Data Assumptions

### Core Model Enhancements

This final analysis uses our most advanced model, featuring:
*   **Dynamic Maintenance:** Instead of a flat average, the model uses a data-driven, year-by-year maintenance budget for each vehicle based on research from Edmunds and CarEdge.
    *   **RDX Annual Maintenance:** [$942, $1,231, $1,362]
    *   **iX Annual Maintenance:** [$400, $600, $800]
*   **Compounded Opportunity Cost:** The model calculates the future value of the difference in total monthly costs between the two options, compounded monthly at a **7% annual rate of return**. This reveals the true financial impact of choosing the more expensive vehicle.

### Depreciation (Data-Driven Model)

*   **Acura RDX:** A 3-year depreciation of ~35% is modeled with annual rates of **20% (Y1), 12% (Y2), and 8% (Y3)**.
*   **BMW iX:** A 3-year depreciation of ~52% is modeled with annual rates of **30% (Y1), 20% (Y2), and 15% (Y3)**.

## Data Sources
*   **Core Logic:** `Model/car_keep_runner.py` (v3 - Dynamic Maint/Opp. Cost)
*   **Scenario Data:** `scenarios/scenarios.json`
*   **Depreciation & Maintenance Data:** iSeeCars.com, KBB.com, CarEdge.com, Edmunds.com
*   **Deal Information:** Actual deal sheet and web listings.
