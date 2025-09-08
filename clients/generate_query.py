from openai import OpenAI
import textwrap

grammar = textwrap.dedent(r"""
// ---------- Start ----------
start: select_stmt 

// ---------- Select Statement ----------
select_stmt: SELECT select_expr_list FROM TABLE_NAME (WHERE where_clause)? (GROUP BY group_by_clause)? (ORDER BY order_by_clause)? (LIMIT NUMBER)? FORMAT FORMAT_TYPE

// ---------- Select Expressions ----------
select_expr_list: select_expr ("," select_expr)*
select_expr: aggregation -> agg_expr
           | column_name -> col_expr

// ---------- Aggregations ----------
aggregation: func_name "(" ((DISTINCT)? column_name)? ")"
func_name: COUNT | SUM | AVG | MIN | MAX

// ---------- Columns ----------
column_name: "year_of_birth"
           | "gender" 
           | "ethnicity"
           | "child_s_first_name"
           | "count"
           | "rank"

// ---------- WHERE Clause ----------
where_clause: condition (AND condition)*

year_of_birth_condition: "year_of_birth" comparator YEAR
gender_condition: "gender" comparator gender_value
ethnicity_condition: "ethnicity" comparator ethnicity_value
child_s_first_name_condition: "child_s_first_name" comparator NAME
count_condition: "count" comparator NUMBER
rank_condition: "rank" comparator NUMBER

condition: year_of_birth_condition
         | gender_condition 
         | ethnicity_condition
         | child_s_first_name_condition
         | count_condition
         | rank_condition

comparator: "=" | "!=" | ">" | "<" | ">=" | "<="

// ---------- Constrained Values ----------
gender_value: MALE | FEMALE
ethnicity_value: HISPANIC 
               | WHITE_NON_HISPANIC
               | BLACK_NON_HISPANIC
               | ASIAN_AND_PACIFIC_ISLANDER 

// ---------- GROUP BY ----------
group_by_clause: column_name ("," column_name)*

// ---------- ORDER BY ----------
order_by_clause: order_expr ("," order_expr)*
order_expr: column_name (ASC | DESC)?

// ---------- Keywords (case-insensitive) ----------
SELECT: "SELECT"
FROM: "from"i | "FROM" 
WHERE: "where"i | "WHERE"
GROUP: "group"i | "GROUP"
BY: "by"i | "BY"
ORDER: "order"i | "ORDER"
LIMIT: "limit"i | "LIMIT"
AND: "and"i | "AND"
DISTINCT: "distinct"i | "DISTINCT"
ASC: "asc"i | "ASC"
DESC: "desc"i | "DESC"
COUNT: "count"i | "COUNT"
SUM: "sum"i | "SUM"
AVG: "avg"i | "AVG"
MIN: "min"i | "MIN"  
MAX: "max"i | "MAX"
FORMAT: "format"i | "FORMAT"

// ---------- Constants ----------
MALE: "'MALE'"
FEMALE: "'FEMALE'"
HISPANIC: "'HISPANIC'"
WHITE_NON_HISPANIC: "'WHITE NON HISPANIC'"
BLACK_NON_HISPANIC: "'BLACK NON HISPANIC'"
ASIAN_AND_PACIFIC_ISLANDER: "'ASIAN AND PACIFIC ISLANDER'"
TABLE_NAME: "baby_names"
FORMAT_TYPE: "CSVWithNames" 

// ---------- Terminals ----------
NUMBER: /[1-9]+/
NAME: /'[^']*'/
YEAR: /201[1-9]|202[01]/

// ---------- Whitespace handling ----------
%import common.WS
%ignore WS
""")

class QueryGenerator: 
    def __init__(self, openai_token): 
        self.client = OpenAI(api_key=openai_token)

    def generate_query(self, prompt: str): 
        response = self.client.responses.create(
            model="gpt-5",
            input=prompt,
            text={"format": {"type": "text"}},
            tools=[
                {
                    "type": "custom",
                    "name": "baby_names_query_generator",
                    "description": "Creates read-only Tinybird queries limited to SELECT statements.YOU MUST REASON HEAVILY ABOUT THE QUERY AND MAKE SURE IT OBEYS THE GRAMMAR.",
                    "format": {
                        "type": "grammar",
                        "syntax": "lark",
                        "definition": grammar
                    }
                },
            ],
            parallel_tool_calls=False
        )

        return response.output[1].input
