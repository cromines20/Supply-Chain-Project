# DataCo Supply Chain EDA: Sales, Fulfillment, and Digital Demand

## Executive Stakeholder Write-Up

DataCo generated meaningful sales and profit across the period analyzed, but the business shows two clear management priorities: fulfillment reliability and concentrated revenue exposure. Across **180,519 order lines**, representing **65,752 distinct orders** and **20,652 customers**, DataCo recorded **$36.8M in gross sales** and **$4.0M in profit**, producing an overall **10.8% profit margin**. At a high level, this suggests the company is profitable and has a sizable operating base. However, more than half of order lines are flagged as late-delivery risk, which creates a material customer experience issue that could weaken repeat purchase behavior, increase support burden, and reduce trust in premium delivery promises.

The most important executive takeaway is that fulfillment risk appears to be systemic, but it is most severe in expedited shipping modes. Overall, **54.8% of order lines** are marked as late delivery risk. First Class has the highest risk at **95.3%**, followed by Second Class at **76.6%**. This pattern is especially important because these shipping modes imply a faster promise to the customer. First Class averages **2.0 actual shipping days** against a **1.0-day scheduled promise**, and Second Class averages **4.0 actual shipping days** against a **2.0-day scheduled promise**. In plain terms, the company is not just occasionally missing delivery expectations; it appears to be offering delivery speeds that the operation often cannot meet. Standard Class performs better, with a late-delivery rate of **38.1%**, but even that level is still high enough to warrant attention. The recommended next step for Operations is to review carrier performance, fulfillment cutoffs, warehouse routing, and the published delivery promise for First Class and Second Class before pushing those options more aggressively.

The second major takeaway is that revenue and profit are highly concentrated in a relatively small part of the assortment. The top eight categories generate **84.9% of total sales** and **84.9% of total profit**. Fishing is the largest category at **$6.9M in sales**, or **18.8% of total sales**, followed by Cleats at **$4.4M**, Camping & Hiking at **$4.1M**, and Cardio Equipment at **$3.7M**. This concentration is useful because it gives Finance and Merchandising a clear place to focus planning work, but it also creates risk. If customer demand, vendor availability, pricing, or fulfillment reliability changes in these categories, the impact on total company performance would be outsized. A reasonable finance follow-up would be to create a core-category watchlist that tracks sales, margin, late-delivery rate, order volume, and discounting for the top categories on a recurring basis.

Sales are geographically diversified across markets, but Europe and LATAM are the largest contributors. Europe generated **$10.9M**, or **29.6% of sales**, while LATAM generated **$10.3M**, or **27.9% of sales**. Pacific Asia followed with **$8.3M**, then USCA with **$5.1M**, and Africa with **$2.3M**. The regional picture does not point to one isolated market causing the fulfillment issue. Late-delivery rates are elevated across every major market, ranging from roughly **54.4% to 55.2%**. This is a contextual insight: regional teams should be aware of their local performance, but the late-delivery problem likely requires a broader operating review rather than a fix in only one geography.

The time trend adds an important caveat. Sales were relatively stable through 2015 and 2016, at about **$12.3M per year**, then declined to **$11.8M in 2017**, a **4.0% year-over-year decrease**. January 2018 is present in the dataset but should not be interpreted as a full-year trend because the data only covers one month. A more granular monthly view shows that sales remained near the $1.0M monthly range for much of the period, then dropped sharply late in 2017. Sales moved from **$1.14M in September 2017** to **$1.07M in October**, then down to **$626.9K in November**, **$503.9K in December**, and **$331.7K in January 2018**. This shift deserves follow-up because it may reflect assortment changes, seasonality, data extraction boundaries, demand changes, or operational constraints. The analysis should not overstate the cause from EDA alone, but the decline is large enough that Finance should validate whether it is real business movement or a data coverage artifact.

The digital demand data creates a third area of opportunity. The product access logs cover **469,977 pageview records** from **September 2017 through January 2018**. When joined to product sales, the log data covers **92.1% of pageviews** and **91.9% of sales**, which is strong enough for directional e-commerce analysis. Several product pages received high traffic but produced low sales per 1,000 pageviews. For example, Nike Men's Fingertrap Max Training Shoe had more than **12K pageviews** but only about **$8.0K in sales**, producing a weak sales-per-view proxy compared with top-performing products. This does not prove conversion rate problems because the dataset does not include sessions, carts, inventory availability, or true attribution. However, it is a practical starting point for the E-commerce team to audit product detail pages, pricing, product availability, promotion placement, and checkout friction.

Before this analysis becomes a production dashboard, the Data and Finance teams should confirm reporting definitions. Canceled and suspected-fraud orders are present in the raw data and represent **4.3% of recorded sales**. Pending, pending-payment, processing, and payment-review statuses also appear in the sales fields. This does not make the exploratory analysis invalid, but it means stakeholder reporting needs a clear revenue definition. Executives should decide whether gross sales should include all order statuses for demand analysis or only completed/closed orders for financial reporting. That decision will affect KPI definitions, dashboard trust, and comparisons to accounting reports.

Overall, the recommendation is to prioritize the work in this order. First, Operations should address shipping promise reliability, especially First Class and Second Class. Second, Finance and Merchandising should focus planning around the top eight categories because they drive most of the business. Third, E-commerce should audit high-traffic product pages with low sales-per-view performance. Fourth, Data and Finance should formalize order-status rules before recurring reporting. These actions connect directly to the data and give each stakeholder team a concrete next step.

## Business Question

How are sales, profit, fulfillment performance, and product-page demand trending across categories, markets, shipping modes, and customer segments, and what should stakeholder teams prioritize next?

## Stakeholders

- **Finance:** understand sales concentration, margin, trend movement, and reporting caveats.
- **Operations:** identify fulfillment risk by shipping mode and region.
- **E-commerce:** identify high-interest product pages that may not be translating into sales.
- **Data / Analytics:** document assumptions, data quality issues, and required KPI definitions.

### Stakeholder Goals

The analysis supports prioritization for Finance, Operations, E-commerce, and Data teams. The North Star metrics are gross sales, profit, profit margin, order volume, late-delivery rate, and sales per 1,000 product pageviews. The North Star dimensions are time, category, product, market, order region, shipping mode, customer segment, order status, and product-page traffic.

### Columns and Coverage

The orders dataset spans **2015-01-01 through 2018-01-31**. The access logs span **2017-09-01 through 2018-01-31**. The order data is broad enough for sales, margin, category, region, customer segment, and shipping analysis. The access-log data is useful for directional digital demand analysis, but it should not be treated as a full conversion funnel because it does not include sessions, add-to-cart events, inventory snapshots, marketing spend, or completed checkout attribution.

Key caveats:

- Product description is fully missing and was excluded from analysis.
- Order zipcode is **86.2% missing**, so market and order region are more reliable geographic dimensions.
- January 2018 is a partial-year view and should not be compared to full-year 2015, 2016, or 2017 totals.
- Canceled and suspected-fraud orders account for **4.3% of sales**, so production reporting needs a stakeholder-approved revenue definition.

### Aggregates and Anomalies

The main aggregate finding is that DataCo is profitable but operationally exposed. Overall profit margin is **10.8%**, and negative-profit order lines represent **18.7%** of records. The biggest anomaly is fulfillment: **54.8%** of order lines are flagged late. Shipping mode is the most obvious explanatory dimension because expedited modes show the worst late-delivery rates.

### Notable Segments

The most important notable segments are shipping mode, category, market/region, time, and digital product demand. Shipping mode explains delivery risk. Category explains revenue concentration. Market and region show that fulfillment risk is broad rather than isolated. Time highlights a late-2017 sales decline that requires follow-up. Product access logs identify pages where customer interest may be higher than realized sales.

## Deep Dive Insights by Dimension

### Time Trend

Annual sales were stable from 2015 to 2016, moving from **$12.34M** to **$12.30M**, then declined to **$11.81M** in 2017. Monthly sales were mostly near or above $1.0M until late 2017. The sharp drop after September 2017 is the largest time-based finding: **$1.14M in September**, **$1.07M in October**, **$626.9K in November**, **$503.9K in December**, and **$331.7K in January 2018**. Because access logs start in September 2017 and average order value also shifts late in the period, this trend should be investigated before being treated as a pure demand decline.

**Recommendation:** Finance should validate the late-2017 decline against source-system extracts, order-status definitions, and assortment changes.

### Product Category

Sales are concentrated in the top categories. Fishing leads with **$6.93M** in sales and **$756.2K** in profit. Cleats follows with **$4.43M** in sales and **$494.6K** in profit. Camping & Hiking, Cardio Equipment, Women's Apparel, Water Sports, Men's Footwear, and Indoor/Outdoor Games complete the top eight. Together, those eight categories drive nearly **85%** of sales and profit, which makes them the most important categories for planning.

Some smaller categories have stronger margins, but their total contribution is too small to change the company-level story. For example, Garden shows a higher margin than many larger categories, but it represents less than 1% of sales. This is a classic portfolio tradeoff: small high-margin categories may be worth growing, but the immediate business impact is still concentrated in the core categories.

**Recommendation:** Build a category scorecard for the top eight categories and separately identify small categories with high margin that could be tested for growth.

### Shipping Mode

Shipping mode is the most actionable operational dimension. Standard Class accounts for the most volume and sales, with **$22.0M** in sales and **39,324 orders**, but its late rate is **38.1%**. First Class has **$5.7M** in sales and the highest late rate at **95.3%**. Second Class has **$7.1M** in sales and a **76.6%** late rate. Same Day has a **45.7%** late rate, which is also high given the promise implied by the name.

The practical interpretation is that customers choosing faster shipping may be more likely to experience missed expectations. This is a higher-severity issue than late delivery in standard shipping because the customer likely paid for or selected speed.

**Recommendation:** Operations should review whether expedited delivery promises are realistic by market, warehouse, and carrier. If the promise cannot be met consistently, DataCo should adjust messaging or routing before promoting those options.

### Market and Region

Europe is the largest market at **$10.87M** in sales, followed by LATAM at **$10.28M**, Pacific Asia at **$8.27M**, USCA at **$5.07M**, and Africa at **$2.29M**. Western Europe and Central America are the top regions, contributing **$5.89M** and **$5.67M** in sales respectively. These regions should receive close attention because changes there will be visible at the company level.

Late-delivery rates are high across markets, which suggests the issue is not isolated to one geography. South Asia, Western Europe, East of USA, Eastern Europe, and South of USA all show elevated rates among meaningful-volume regions. Since the problem appears broad, regional analysis should be used to prioritize where to start, not to explain away the issue as a single-market problem.

**Recommendation:** Start fulfillment diagnostics in large, high-late-rate regions such as Western Europe and South Asia, then compare carrier mix and warehouse distance against better-performing regions.

### Customer Segment

Consumer customers represent the largest segment with **$19.1M in sales**, or **51.9%** of total sales. Corporate customers represent **30.4%**, and Home Office represents **17.7%**. Profit margins and late-delivery rates are similar across segments, which means customer segment is not the strongest explanation for performance differences in this EDA.

This is still useful because it tells stakeholders where not to overfocus. The delivery issue does not appear to be caused by one customer segment behaving differently. Consumer is the largest segment, so it should be watched closely, but the root-cause analysis should start with shipping mode and region.

**Recommendation:** Use customer segment as a reporting filter, but prioritize shipping mode, geography, and category for root-cause work.

### Order Status

Only **32.9% of recorded sales** are in Complete status. Pending Payment, Processing, Pending, Closed, On Hold, Suspected Fraud, Canceled, and Payment Review statuses are also present in the dataset. Canceled and suspected-fraud orders together account for **4.3%** of sales. This is not necessarily wrong for exploratory analysis, but it is a major reporting-definition issue.

The analytical question is whether the company wants to measure gross demand, booked sales, fulfilled sales, or accounting-recognized revenue. Each version would use different status filters.

**Recommendation:** Data and Finance should define at least two metrics: gross demand including all submitted orders, and recognized sales excluding canceled, suspected-fraud, and unresolved payment statuses.

### Digital Demand

Product access logs show which product pages attracted attention from September 2017 through January 2018. The join between access logs and order products covers more than **90%** of both pageviews and sales, making it useful for directional analysis. High-performing products such as Field & Stream Sportsman 16 Gun Fire Safe and the Diamondback Women's Serene Classic Comfort line generate strong sales per 1,000 pageviews. Other products receive substantial traffic but much lower sales per 1,000 pageviews.

This creates a practical e-commerce opportunity: high pageviews plus weak sales proxy suggests possible friction. The reason could be price, product detail page content, poor imagery, stockouts, shipping concerns, or customers using the page for research but buying elsewhere. The current data cannot prove the cause, but it identifies the right product list for a conversion audit.

**Recommendation:** E-commerce should audit high-view / low-sales products for page content, pricing, availability, reviews, promotion placement, and checkout path issues.

## Insight Types and Recommendations

| Insight | Type | Stakeholder | Recommended Action |
|---|---|---|---|
| First Class and Second Class have the highest late-delivery rates. | Actionable | Operations | Review carrier routing, fulfillment cutoffs, and delivery promises for expedited shipping. |
| Top eight categories drive 84.9% of sales and profit. | Directional | Finance / Merchandising | Build a recurring core-category watchlist for sales, margin, orders, discounts, and late rate. |
| Late-delivery risk is high across major markets. | Contextual | Operations | Treat fulfillment as a systemic issue, then prioritize large regions with high late rates. |
| Late-2017 sales decline is large but may reflect data or assortment changes. | Directional | Finance / Data | Validate source coverage, order statuses, and category mix before interpreting as demand decline. |
| High-pageview products with low sales per 1,000 views may have conversion friction. | Actionable | E-commerce | Audit product pages, price, inventory, imagery, reviews, and checkout path. |
| Order statuses change KPI interpretation. | Directional | Data / Finance | Define gross demand and recognized sales separately for production reporting. |

## Deliverables

- SQL EDA queries: `sql/dataco_eda_queries.sql`
- Excel-style analyst workbook: `outputs/supply_chain_eda/dataco_supply_chain_eda_workbook.xlsx`
- SQLite database generated from the source CSVs: `outputs/supply_chain_eda/dataco_supply_chain_eda.sqlite`

## Tools Used

- **SQL / SQLite:** profiling, aggregation, segmentation, product-demand joins
- **Excel-style analysis:** pivot-style summaries, conditional formatting, charts, insights log
- **Python:** repeatable data preparation and summary-table generation
