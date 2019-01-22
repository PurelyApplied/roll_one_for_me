from rofm.classes.tables.table import parse_enumerated_table

d3_table_text = """
d3 This God is

1. Evil

2. Good

3. Neutral"""

if __name__ == '__main__':
    t = parse_enumerated_table(d3_table_text)
    print(t)
