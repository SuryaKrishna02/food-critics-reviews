fetch_parameters = """
You are an expert in the extracting the information about the restaurant review from the given text.

You task is to extract the following values from the given text and give in the json format.
1. restaurant_name : string
2. action : string (values are insert, modify & delete)
3. review : string
4. rating : float (values are from 1-5)

Note:
Output should be in the below format:
```json
{
    "resturant_name": "<name of the restaurant>",
    "action": "<action>",
    "review": "<review that is being provided>",
    "rating": <rating value>
}
```
"""

sql_query_generator = """
You are an expert in the generating the error free optimized SQL query based on given parameters for the MongoDB Database.

Below is the schema of the `restaurants` collection present in the `food-critic-reviews` database:
'name': {'bsonType': 'string', 'minLength': 1},
'restaurant_id': {'bsonType': 'string'},
'address': {
    'bsonType': 'object',
    'required': ['building', 'coord', 'street', 'zipcode'],
    'properties': {
        'building': {'bsonType': 'string'},
        'coord': {
            'bsonType': 'array',
            'minItems': 2,
            'maxItems': 2,
            'items': {'bsonType': 'double'}
        },
        'street': {'bsonType': 'string'},
        'zipcode': {'bsonType': 'string', 'pattern': '^\d{5}$'}
    }
},
'avg_rating': {'bsonType': 'double', 'minimum': 0, 'maximum': 5},
'critic_reviews': {
    'bsonType': 'array',
    'items': {
        'bsonType': 'object',
        'required': ['name', 'review', 'rating'],
        'properties': {
            'name': {'bsonType': 'string'},
            'review': {'bsonType': 'string'},
            'rating': {
                'bsonType': ['double', 'int'],  # Allow both double and integer
                'minimum': 0,
                'maximum': 5
            },
            'sentiment_score': {
                'bsonType': 'double',
                'minimum': -1,
                'maximum': 1
            }
        }
    }
},
'created_at': {'bsonType': 'date'},
'updated_at': {'bsonType': 'date'}

Your task is to generate a SQL query based on the given json string parameters according to the given instructions:
1. You can only update the values in the `critic_reviews` or/and `avg_rating`.
2. Always include `restaurant_name` value in the where clause.
3. Either Insert, Update, or Delete the values given in the json string.

Note:
Output should be in the below format:
```sql
<sql_query>
``
"""