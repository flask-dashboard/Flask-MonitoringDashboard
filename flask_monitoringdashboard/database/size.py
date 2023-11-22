from sqlalchemy import text

from flask_monitoringdashboard.database import session_scope


def estimate_table_size(session, table_name):
    # Retrieve all column names for the table
    table_info = session.execute(text(f"PRAGMA table_info({table_name});")).fetchall()

    # Table_info is a list of tuples, where each tuple represents a column.
    # The second element (index 1) of each tuple is the column name.
    column_names = [col[1] for col in table_info]  # Extracting the column names

    # Construct a query to calculate the total length of all columns for all rows
    length_sum = ' + '.join(f"length({col})" for col in column_names)

    if not length_sum:
        return 0

    size_query = f"SELECT SUM({length_sum}) FROM {table_name};"
    size = session.execute(text(size_query)).scalar()

    return size if size is not None else 0


def get_table_sizes():
    try:
        with session_scope() as session:
            # Retrieve all table names in the database
            tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()

            table_sizes = {}
            for table_name, in tables:
                # Estimate the size of the table
                try:
                    table_size = estimate_table_size(session, table_name)
                except Exception as e:
                    print(f"Error estimating size for table {table_name}: {e}")
                    table_size = None
                # Store the result if size could be determined
                if table_size is not None:
                    table_sizes[table_name] = table_size
            return table_sizes
    except Exception as e:
        print(f"Error retrieving table sizes: {e}")
        return {}


def sum_table_sizes(table_sizes):
    total_size = sum(size for size in table_sizes.values() if size is not None)
    return total_size
