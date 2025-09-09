# NYC Baby Names

## Tinybird

### Overview
This project analyzes the Popular Baby Names dataset from NYC, providing flexible querying capabilities to explore trends in baby names across different years, ethnicities, and genders. The dashboard enables users to discover popular names, track naming patterns over time, and filter by various demographic factors.

### Data sources

#### baby_names
Contains the NYC Popular Baby Names dataset with information about baby names by year, gender, ethnicity, count, and rank.

To ingest data into this datasource:

```bash
curl -X POST "https://api.us-west-2.aws.tinybird.co/v0/events?name=baby_names" \
     -H "Authorization: Bearer $TB_ADMIN_TOKEN" \
     -d '{"year_of_birth":2019,"gender":"FEMALE","ethnicity":"ASIAN AND PACIFIC ISLANDER","child_s_first_name":"Olivia","count":172,"rank":1}'
```

### Endpoints

#### baby_names_query
A flexible endpoint that allows querying the baby names dataset with various filtering parameters:
- `year`: Filter by year of birth (e.g., 2019)
- `name`: Filter by first name (prefix match)
- `gender`: Filter by gender
- `ethnicity`: Filter by ethnicity
- `min_count`: Filter by minimum count
- `max_rank`: Filter by maximum rank
- `sort_by`: Field to sort by (default: count)
- `sort_dir`: Sort direction (asc or desc)
- `limit`: Number of results to return (default: 100)

Example usage:

```bash
curl -X GET "https://api.us-west-2.aws.tinybird.co/v0/pipes/baby_names_query.json?token=$TB_ADMIN_TOKEN&year=2019&gender=FEMALE&ethnicity=ASIAN+AND+PACIFIC+ISLANDER&max_rank=10"
```
