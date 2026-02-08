import streamlit as st
from QueryParser import QueryParser

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="SQL Parser",
    page_icon="🗄️",
    layout="centered"
)

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("🗄️ SQL Query Parser")
st.caption("Validate SQL queries (DML, DDL, TCL) with clear feedback.")

# ---------------------------------------------------------
# Input
# ---------------------------------------------------------
sql_query = st.text_area(
    "Enter SQL query",
    height=120,
    placeholder="UPDATE users SET name = 'Alice' WHERE id = 1;"
)

col1, col2 = st.columns([1, 3])

with col1:
    run = st.button("▶ Parse")

with col2:
    st.caption("Examples: SELECT, INSERT, UPDATE, CREATE, DROP, COMMIT")

# ---------------------------------------------------------
# Run parser
# ---------------------------------------------------------
if run:
    if not sql_query.strip():
        st.warning("Please enter a SQL query.")
    else:
        parser = QueryParser(sql_query)
        result = parser.analyse()
        tokens = parser.tokenize()

        st.divider()

        # -----------------------------
        # VALID QUERY
        # -----------------------------
        if result is None:
            st.success("✅ Query is valid")

            st.info(f"""
**Query type:** `{tokens[0].upper()}`  
**Status:** Passed all syntax and validation checks
""")

        # -----------------------------
        # INVALID QUERY
        # -----------------------------
        elif isinstance(result, dict) and "error" in result:
            st.error("❌ Query is invalid")

            st.markdown(f"**Error:** {result['error']}")

            if "suggestion" in result and result["suggestion"]:
                st.markdown(f"💡 **Suggestion:** {result['suggestion']}")

        # -----------------------------
        # UNEXPECTED
        # -----------------------------
        else:
            st.warning("Unexpected parser output")
            st.write(result)

        # -----
