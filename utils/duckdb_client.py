import duckdb

def run_duckdb_query(query: str) -> list:
    try:
        con = duckdb.connect(database=':memory:')
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("INSTALL parquet; LOAD parquet;")
        result = con.execute(query).fetchall()
        return result
    except Exception as e:
        return [{"error": str(e)}]
