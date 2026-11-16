
"""Interactive PhonePe dashboard over the nine table databases."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import plotly.express as px

from phonepe.analysis import (
    available_states,
    available_years,
    device_breakdown,
    district_transactions,
    merchant_penetration,
    state_transaction_leaders,
    top_entities,
    transaction_mix,
    user_totals,
)
from phonepe.places import STATE_CENTROIDS


def main() -> None:
    import streamlit as st

    st.set_page_config(
        page_title="PhonePe Transaction Insights",
        layout="wide",
    )

    st.title("PhonePe Transaction Insights")
    st.caption(
        "Each warehouse table is served by its own Postgres container."
    )

    # --------------------------------------------------
    # Database connection
    # --------------------------------------------------

    try:
        years = available_years()
        states = available_states()

    except Exception as exc:
        st.error(
            "The table databases are not reachable. "
            "From this folder run `bash scripts/setup.sh`."
        )
        st.code(str(exc))
        return

    if not years:
        st.warning(
            "The databases are up but empty. "
            "Run `bash scripts/setup.sh`."
        )
        return

    if not states:
        st.warning("No states are available in the database.")
        return

    # --------------------------------------------------
    # Sidebar filters
    # --------------------------------------------------

    year = st.sidebar.selectbox(
        "Year",
        years,
        index=len(years) - 1,
    )

    quarter = st.sidebar.selectbox(
        "Quarter",
        [1, 2, 3, 4],
        index=0,
    )

    state = st.sidebar.selectbox(
        "State",
        states,
        index=(
            states.index("karnataka")
            if "karnataka" in states
            else 0
        ),
    )

    page = st.sidebar.radio(
        "Case study",
        [
            "Transaction dynamics",
            "User engagement",
            "Merchant penetration",
            "Top regions",
            "District map",
        ],
    )

    # --------------------------------------------------
    # Case Study 1: Transaction Dynamics
    # --------------------------------------------------

    if page == "Transaction dynamics":

        mix = transaction_mix(state, int(year))

        st.subheader(
            f"Payment categories in {state}, {year}"
        )

        if mix.empty:
            st.info("No rows for that filter.")

        else:
            mix = mix.reset_index(drop=True)
            mix.index += 1

            st.plotly_chart(
                px.bar(
                    mix,
                    x="quarter",
                    y="transaction_count",
                    color="transaction_type",
                    barmode="group",
                ),
                width="stretch",
            )

            st.dataframe(
                mix,
                width="stretch",
            )

        leaders = state_transaction_leaders(
            int(year),
            int(quarter),
            limit=15,
        )

        st.subheader(
            f"State leaders, {year} Q{quarter}"
        )

        if leaders.empty:
            st.info("No state leader data available.")

        else:
            leaders = leaders.reset_index(drop=True)
            leaders.index += 1

            st.plotly_chart(
                px.bar(
                    leaders,
                    x="transaction_count",
                    y="state",
                    orientation="h",
                ),
                width="stretch",
            )

    # --------------------------------------------------
    # Case Study 2: User Engagement
    # --------------------------------------------------

    elif page == "User engagement":

        users = user_totals(int(year))

        users = users[
            users["quarter"] == int(quarter)
        ]

        st.subheader(
            f"Registered users, {year} Q{quarter}"
        )

        if users.empty:
            st.info("No registered user data available.")

        else:
            users = users.reset_index(drop=True)
            users.index += 1

            st.plotly_chart(
                px.bar(
                    users.head(15),
                    x="registered_users",
                    y="state",
                    orientation="h",
                ),
                width="stretch",
            )

        devices = device_breakdown(
            int(year),
            int(quarter),
        )

        st.subheader("Device brands")

        if devices.empty:
            st.info(
                "This Pulse snapshot has registered-user "
                "totals only. Device rows appear when "
                "usersByDevice is present in the JSON."
            )

        else:
            devices = devices.reset_index(drop=True)
            devices.index += 1

            st.dataframe(
                devices.head(50),
                width="stretch",
            )

    # --------------------------------------------------
    # Case Study 3: Merchant Penetration
    # --------------------------------------------------

    elif page == "Merchant penetration":

        frame = merchant_penetration(
            int(year),
            int(quarter),
        )

        st.subheader(
            f"Merchants and users, {year} Q{quarter}"
        )

        st.caption(
            "The course brief calls this insurance. "
            "The live Pulse files are merchant counts."
        )

        if frame.empty:
            st.info("No rows.")

        else:
            frame = frame.reset_index(drop=True)
            frame.index += 1

            st.plotly_chart(
                px.scatter(
                    frame,
                    x="registered_users",
                    y="registered_merchants",
                    hover_name="state",
                    size="registered_merchants",
                ),
                width="stretch",
            )

            st.dataframe(
                frame,
                width="stretch",
            )

    # --------------------------------------------------
    # Case Study 4: Top Regions
    # --------------------------------------------------

    elif page == "Top regions":

        col1, col2, col3 = st.columns(3)

        # Top transactions
        with col1:

            st.markdown("**Transactions**")

            transactions = top_entities(
                "top_transaction",
                int(year),
                int(quarter),
                "state",
            )

            transactions = transactions.reset_index(
                drop=True
            )
            transactions.index += 1

            st.dataframe(
                transactions,
                width="stretch",
            )

        # Top users
        with col2:

            st.markdown("**Users**")

            users = top_entities(
                "top_user",
                int(year),
                int(quarter),
                "state",
            )

            users = users.reset_index(drop=True)
            users.index += 1

            st.dataframe(
                users,
                width="stretch",
            )

        # Top merchants
        with col3:

            st.markdown("**Merchants**")

            merchants = top_entities(
                "top_merchant",
                int(year),
                int(quarter),
                "state",
            )

            merchants = merchants.reset_index(
                drop=True
            )
            merchants.index += 1

            st.dataframe(
                merchants,
                width="stretch",
            )

        # Top districts
        st.subheader(
            "Top districts by transactions"
        )

        districts = top_entities(
            "top_transaction",
            int(year),
            int(quarter),
            "district",
        )

        districts = districts.reset_index(drop=True)
        districts.index += 1

        st.dataframe(
            districts,
            width="stretch",
        )

    # --------------------------------------------------
    # Case Study 5: District Map
    # --------------------------------------------------

    else:

        leaders = state_transaction_leaders(
            int(year),
            int(quarter),
            limit=40,
        )

        located = []

        for _, row in leaders.iterrows():

            point = STATE_CENTROIDS.get(
                row["state"]
            )

            if point:
                located.append(
                    {
                        "state": row["state"],
                        "lat": point[0],
                        "lon": point[1],
                        "transaction_count": (
                            row["transaction_count"]
                        ),
                        "transaction_amount": (
                            row["transaction_amount"]
                        ),
                    }
                )

        st.subheader(
            f"State transaction map, {year} Q{quarter}"
        )

        if located:

            geo = pd.DataFrame(located)

            geo = geo.reset_index(drop=True)
            geo.index += 1

            # Convert transaction counts to numeric
            # values for Plotly marker sizing.
            geo["transaction_count"] = pd.to_numeric(
                geo["transaction_count"],
                errors="coerce",
            ).fillna(0)

            st.plotly_chart(
                px.scatter_geo(
                    geo,
                    lat="lat",
                    lon="lon",
                    hover_name="state",
                    size=geo[
                        "transaction_count"
                    ].to_numpy(dtype=float),
                    size_max=35,
                    scope="asia",
                    projection="natural earth",
                ),
                width="stretch",
            )

        else:
            st.info(
                "No geographic transaction data available."
            )

        # District-level transactions
        districts = district_transactions(
            state,
            int(year),
            int(quarter),
        )

        st.subheader(
            f"Districts in {state}"
        )

        if districts.empty:
            st.info(
                "No district transaction data available."
            )

        else:
            districts = districts.reset_index(
                drop=True
            )
            districts.index += 1

            st.plotly_chart(
                px.bar(
                    districts.head(20),
                    x="transaction_count",
                    y="district",
                    orientation="h",
                ),
                width="stretch",
            )


if __name__ == "__main__":
    main()
