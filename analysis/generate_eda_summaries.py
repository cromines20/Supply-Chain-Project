from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs" / "supply_chain_eda"
SUMMARY_DIR = OUT_DIR / "summary_tables"


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def pct(value: float) -> float:
    return round(float(value), 4)


def money(value: float) -> float:
    return round(float(value), 2)


def load_orders() -> pd.DataFrame:
    orders = pd.read_csv(DATA_DIR / "DataCoSupplyChainDataset.csv", encoding="latin1")
    orders["order_dt"] = pd.to_datetime(orders["order date (DateOrders)"], errors="coerce")
    orders["ship_dt"] = pd.to_datetime(orders["shipping date (DateOrders)"], errors="coerce")
    orders["order_month"] = orders["order_dt"].dt.to_period("M").dt.to_timestamp()
    orders["order_month_label"] = orders["order_month"].dt.strftime("%Y-%m")
    orders["order_year"] = orders["order_dt"].dt.year
    orders["ship_delay_days"] = (
        orders["Days for shipping (real)"] - orders["Days for shipment (scheduled)"]
    )
    orders["is_negative_profit"] = orders["Order Profit Per Order"] < 0
    orders["is_problem_status"] = orders["Order Status"].isin(["CANCELED", "SUSPECTED_FRAUD"])
    orders["discount_bin"] = pd.cut(
        orders["Order Item Discount Rate"],
        [-0.001, 0.05, 0.10, 0.15, 0.20, 0.25],
        labels=["0-5%", "5-10%", "10-15%", "15-20%", "20-25%"],
    )
    return orders


def load_logs() -> pd.DataFrame:
    logs = pd.read_csv(DATA_DIR / "tokenized_access_logs.csv", encoding="latin1")
    logs["log_dt"] = pd.to_datetime(logs["Date"], errors="coerce")
    logs["log_month"] = logs["log_dt"].dt.to_period("M").dt.to_timestamp()
    logs["log_month_label"] = logs["log_month"].dt.strftime("%Y-%m")
    logs["product_key"] = logs["Product"].str.lower().str.strip()
    return logs


def summarize() -> dict[str, pd.DataFrame | dict]:
    orders = load_orders()
    logs = load_logs()

    monthly = (
        orders.groupby(["order_month", "order_month_label"], dropna=False)
        .agg(
            sales=("Sales", "sum"),
            net_sales=("Order Item Total", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            order_lines=("Order Id", "size"),
            avg_order_value=("Sales", lambda s: s.sum() / orders.loc[s.index, "Order Id"].nunique()),
            late_rate=("Late_delivery_risk", "mean"),
            avg_discount_rate=("Order Item Discount Rate", "mean"),
        )
        .reset_index()
        .sort_values("order_month")
    )
    monthly["profit_margin"] = monthly["profit"] / monthly["sales"]
    monthly["yoy_sales_pct"] = monthly["sales"].pct_change(12)
    monthly["mom_sales_pct"] = monthly["sales"].pct_change()

    year = (
        orders.groupby("order_year")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
        .sort_values("order_year")
    )
    year["profit_margin"] = year["profit"] / year["sales"]
    year["yoy_sales_pct"] = year["sales"].pct_change()

    category = (
        orders.groupby("Category Name")
        .agg(
            sales=("Sales", "sum"),
            net_sales=("Order Item Total", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            quantity=("Order Item Quantity", "sum"),
            late_rate=("Late_delivery_risk", "mean"),
            avg_discount_rate=("Order Item Discount Rate", "mean"),
            negative_profit_rate=("is_negative_profit", "mean"),
        )
        .reset_index()
    )
    category["profit_margin"] = category["profit"] / category["sales"]
    category["sales_share"] = category["sales"] / category["sales"].sum()
    category = category.sort_values("sales", ascending=False)

    product = (
        orders.groupby(["Product Name", "Category Name"])
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            quantity=("Order Item Quantity", "sum"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    product["profit_margin"] = product["profit"] / product["sales"]
    product["sales_share"] = product["sales"] / product["sales"].sum()
    product["product_key"] = product["Product Name"].str.lower().str.strip()
    product = product.sort_values("sales", ascending=False)

    market = (
        orders.groupby("Market")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    market["profit_margin"] = market["profit"] / market["sales"]
    market["sales_share"] = market["sales"] / market["sales"].sum()
    market = market.sort_values("sales", ascending=False)

    region = (
        orders.groupby("Order Region")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    region["profit_margin"] = region["profit"] / region["sales"]
    region["sales_share"] = region["sales"] / region["sales"].sum()
    region = region.sort_values("sales", ascending=False)

    shipping = (
        orders.groupby("Shipping Mode")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            order_lines=("Order Id", "size"),
            late_orders=("Late_delivery_risk", "sum"),
            late_rate=("Late_delivery_risk", "mean"),
            avg_real_days=("Days for shipping (real)", "mean"),
            avg_scheduled_days=("Days for shipment (scheduled)", "mean"),
            avg_delay_days=("ship_delay_days", "mean"),
        )
        .reset_index()
    )
    shipping["profit_margin"] = shipping["profit"] / shipping["sales"]
    shipping["late_order_share"] = shipping["late_orders"] / shipping["late_orders"].sum()
    shipping = shipping.sort_values("sales", ascending=False)

    segment = (
        orders.groupby("Customer Segment")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    segment["profit_margin"] = segment["profit"] / segment["sales"]
    segment["sales_share"] = segment["sales"] / segment["sales"].sum()
    segment = segment.sort_values("sales", ascending=False)

    status = (
        orders.groupby("Order Status")
        .agg(
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            orders=("Order Id", "nunique"),
            order_lines=("Order Id", "size"),
        )
        .reset_index()
    )
    status["sales_share"] = status["sales"] / status["sales"].sum()
    status = status.sort_values("sales", ascending=False)

    discount = (
        orders.groupby("discount_bin", observed=True)
        .agg(
            order_lines=("Order Id", "size"),
            sales=("Sales", "sum"),
            profit=("Order Profit Per Order", "sum"),
            avg_profit_ratio=("Order Item Profit Ratio", "mean"),
            late_rate=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    discount["profit_margin"] = discount["profit"] / discount["sales"]

    access_month = (
        logs.groupby(["log_month", "log_month_label"])
        .agg(pageviews=("url", "size"), unique_ips=("ip", "nunique"))
        .reset_index()
        .sort_values("log_month")
    )

    access_hour = (
        logs.groupby("Hour")
        .agg(pageviews=("url", "size"), unique_ips=("ip", "nunique"))
        .reset_index()
        .sort_values("Hour")
    )

    access_product = (
        logs.groupby(["Product", "Category", "Department", "product_key"])
        .agg(pageviews=("url", "size"), unique_ips=("ip", "nunique"))
        .reset_index()
        .sort_values("pageviews", ascending=False)
    )

    product_demand = access_product.merge(product, on="product_key", how="inner")
    product_demand["sales_per_1k_views"] = product_demand["sales"] / (
        product_demand["pageviews"] / 1000
    )
    product_demand = product_demand.sort_values("pageviews", ascending=False)

    coverage = pd.DataFrame(
        [
            {
                "check": "Order rows",
                "value": len(orders),
                "note": "Line-level order records in DataCoSupplyChainDataset.csv",
            },
            {
                "check": "Distinct orders",
                "value": orders["Order Id"].nunique(),
                "note": "Order IDs can appear on multiple product lines",
            },
            {
                "check": "Distinct customers",
                "value": orders["Customer Id"].nunique(),
                "note": "Customer IDs after masking names/email/password",
            },
            {
                "check": "Order date range",
                "value": f"{orders['order_dt'].min():%Y-%m-%d} to {orders['order_dt'].max():%Y-%m-%d}",
                "note": "2018 contains January only",
            },
            {
                "check": "Access log rows",
                "value": len(logs),
                "note": "Product pageview records in tokenized_access_logs.csv",
            },
            {
                "check": "Access log date range",
                "value": f"{logs['log_dt'].min():%Y-%m-%d} to {logs['log_dt'].max():%Y-%m-%d}",
                "note": "Access logs cover only Sep 2017-Jan 2018",
            },
            {
                "check": "Product description missing",
                "value": f"{orders['Product Description'].isna().mean():.1%}",
                "note": "Field is not useful for analysis",
            },
            {
                "check": "Order zipcode missing",
                "value": f"{orders['Order Zipcode'].isna().mean():.1%}",
                "note": "Use Market / Order Region instead of zipcode",
            },
            {
                "check": "Canceled/fraud sales share",
                "value": f"{orders.loc[orders['is_problem_status'], 'Sales'].sum() / orders['Sales'].sum():.1%}",
                "note": "Potential caveat: status handling should be confirmed with stakeholders",
            },
        ]
    )

    total_sales = orders["Sales"].sum()
    total_profit = orders["Order Profit Per Order"].sum()
    top8 = category.head(8)
    metrics = {
        "rows": int(len(orders)),
        "orders": int(orders["Order Id"].nunique()),
        "customers": int(orders["Customer Id"].nunique()),
        "products": int(orders["Product Name"].nunique()),
        "categories": int(orders["Category Name"].nunique()),
        "date_min": f"{orders['order_dt'].min():%Y-%m-%d}",
        "date_max": f"{orders['order_dt'].max():%Y-%m-%d}",
        "sales": money(total_sales),
        "net_sales": money(orders["Order Item Total"].sum()),
        "profit": money(total_profit),
        "profit_margin": pct(total_profit / total_sales),
        "late_rate": pct(orders["Late_delivery_risk"].mean()),
        "negative_profit_rate": pct(orders["is_negative_profit"].mean()),
        "top_category": category.iloc[0]["Category Name"],
        "top_category_sales_share": pct(category.iloc[0]["sales_share"]),
        "top_8_category_sales_share": pct(top8["sales"].sum() / total_sales),
        "top_8_category_profit_share": pct(top8["profit"].sum() / total_profit),
        "highest_late_shipping_mode": shipping.sort_values("late_rate", ascending=False).iloc[0][
            "Shipping Mode"
        ],
        "highest_late_shipping_rate": pct(shipping["late_rate"].max()),
        "direct_problem_status_sales_share": pct(
            orders.loc[orders["is_problem_status"], "Sales"].sum() / total_sales
        ),
        "access_log_rows": int(len(logs)),
        "access_log_date_min": f"{logs['log_dt'].min():%Y-%m-%d}",
        "access_log_date_max": f"{logs['log_dt'].max():%Y-%m-%d}",
        "joined_product_log_coverage": pct(product_demand["pageviews"].sum() / len(logs)),
        "joined_product_sales_coverage": pct(product_demand["sales"].sum() / total_sales),
    }

    return {
        "metrics": metrics,
        "coverage": coverage,
        "monthly": monthly,
        "year": year,
        "category": category,
        "product": product,
        "market": market,
        "region": region,
        "shipping": shipping,
        "segment": segment,
        "status": status,
        "discount": discount,
        "access_month": access_month,
        "access_hour": access_hour,
        "access_product": access_product,
        "product_demand": product_demand,
    }


def write_outputs(summaries: dict[str, pd.DataFrame | dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    for name, value in summaries.items():
        if isinstance(value, pd.DataFrame):
            clean = value.copy()
            for col in clean.columns:
                if pd.api.types.is_datetime64_any_dtype(clean[col]):
                    clean[col] = clean[col].dt.strftime("%Y-%m-%d")
            clean.to_csv(SUMMARY_DIR / f"{name}.csv", index=False)
            clean.to_json(SUMMARY_DIR / f"{name}.json", orient="records", indent=2)

    with open(OUT_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(summaries["metrics"], f, indent=2)


def write_sqlite_db() -> None:
    orders = load_orders()
    logs = load_logs()

    order_cols = {
        "Type": "payment_type",
        "Days for shipping (real)": "days_for_shipping_real",
        "Days for shipment (scheduled)": "days_for_shipment_scheduled",
        "Benefit per order": "benefit_per_order",
        "Sales per customer": "sales_per_customer",
        "Delivery Status": "delivery_status",
        "Late_delivery_risk": "late_delivery_risk",
        "Category Id": "category_id",
        "Category Name": "category_name",
        "Customer Id": "customer_id",
        "Customer Segment": "customer_segment",
        "Market": "market",
        "Order City": "order_city",
        "Order Country": "order_country",
        "order date (DateOrders)": "order_date_raw",
        "Order Id": "order_id",
        "Order Item Discount": "order_item_discount",
        "Order Item Discount Rate": "order_item_discount_rate",
        "Order Item Product Price": "order_item_product_price",
        "Order Item Profit Ratio": "order_item_profit_ratio",
        "Order Item Quantity": "order_item_quantity",
        "Sales": "sales",
        "Order Item Total": "order_item_total",
        "Order Profit Per Order": "order_profit_per_order",
        "Order Region": "order_region",
        "Order State": "order_state",
        "Order Status": "order_status",
        "Product Name": "product_name",
        "Product Price": "product_price",
        "Product Status": "product_status",
        "shipping date (DateOrders)": "shipping_date_raw",
        "Shipping Mode": "shipping_mode",
        "order_dt": "order_ts",
        "ship_dt": "shipping_ts",
        "order_month_label": "order_month",
        "order_year": "order_year",
        "ship_delay_days": "ship_delay_days",
        "is_negative_profit": "is_negative_profit",
        "is_problem_status": "is_problem_status",
    }
    order_sql = orders[list(order_cols)].rename(columns=order_cols)
    order_sql["order_ts"] = order_sql["order_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    order_sql["shipping_ts"] = order_sql["shipping_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    order_sql["is_negative_profit"] = order_sql["is_negative_profit"].astype(int)
    order_sql["is_problem_status"] = order_sql["is_problem_status"].astype(int)
    order_sql["product_key"] = order_sql["product_name"].str.lower().str.strip()

    access_sql = logs[
        ["Product", "Category", "Date", "Month", "Hour", "Department", "ip", "url", "log_dt", "log_month_label", "product_key"]
    ].rename(
        columns={
            "Product": "product",
            "Category": "category",
            "Date": "date_raw",
            "Month": "month_raw",
            "Hour": "hour",
            "Department": "department",
            "log_dt": "log_ts",
            "log_month_label": "log_month",
        }
    )
    access_sql["log_ts"] = access_sql["log_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")

    db_path = OUT_DIR / "dataco_supply_chain_eda.sqlite"
    if db_path.exists():
        db_path.unlink()
    with sqlite3.connect(db_path) as conn:
        order_sql.to_sql("orders_clean", conn, index=False)
        access_sql.to_sql("access_logs_clean", conn, index=False)
        conn.execute("CREATE INDEX idx_orders_month ON orders_clean(order_month)")
        conn.execute("CREATE INDEX idx_orders_product ON orders_clean(product_key)")
        conn.execute("CREATE INDEX idx_access_product ON access_logs_clean(product_key)")
        conn.execute("CREATE INDEX idx_access_month ON access_logs_clean(log_month)")


if __name__ == "__main__":
    summaries = summarize()
    write_outputs(summaries)
    write_sqlite_db()
