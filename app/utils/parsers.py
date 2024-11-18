import re
from pymongo import MongoClient
from typing import Dict, Any, List, Union

class MongoSQLParser:
    def __init__(self, connection_string: str, database: str):
        """Initialize MongoDB connection"""
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
    
    def parse_where_clause(self, where_clause: str) -> Dict[str, Any]:
        """Convert SQL WHERE clause to MongoDB filter"""
        if not where_clause:
            return {}
            
        # Basic operators conversion
        operators = {
            '=': '$eq',
            '>': '$gt',
            '<': '$lt',
            '>=': '$gte',
            '<=': '$lte',
            '!=': '$ne'
        }
        
        # Split on AND
        conditions = [c.strip() for c in where_clause.split('AND')]
        mongo_filter = {}
        
        for condition in conditions:
            for op in operators:
                if op in condition:
                    field, value = condition.split(op)
                    field = field.strip()
                    value = value.strip()
                    
                    # Try to convert value to number if possible
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        # Remove quotes if present
                        value = value.strip('"\'')
                    
                    mongo_filter[field] = {operators[op]: value}
                    break
                    
        return mongo_filter

    def execute_query(self, query: str) -> Union[List[Dict], Dict]:
        """Execute SQL-like query on MongoDB"""
        # Extract operation type
        operation = query.split()[0].upper()
        
        if operation == 'SELECT':
            return self._handle_select(query)
        elif operation == 'INSERT':
            return self._handle_insert(query)
        elif operation == 'UPDATE':
            return self._handle_update(query)
        elif operation == 'DELETE':
            return self._handle_delete(query)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _handle_select(self, query: str) -> List[Dict]:
        """Handle SELECT queries"""
        # Basic SELECT parsing
        match = re.match(r'SELECT .+ FROM (\w+)(?:\s+WHERE (.+))?', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT query format")
            
        collection_name = match.group(1)
        where_clause = match.group(2) if match.group(2) else ''
        
        mongo_filter = self.parse_where_clause(where_clause)
        return list(self.db[collection_name].find(mongo_filter))

    def _handle_insert(self, query: str) -> Dict:
        """Handle INSERT queries"""
        # Example: INSERT INTO collection (field1, field2) VALUES (value1, value2)
        match = re.match(r'INSERT INTO (\w+) \((.*?)\) VALUES \((.*?)\)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT query format")
            
        collection_name = match.group(1)
        fields = [f.strip() for f in match.group(2).split(',')]
        values = [v.strip().strip('\'\"') for v in match.group(3).split(',')]
        
        document = dict(zip(fields, values))
        result = self.db[collection_name].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    def _handle_update(self, query: str) -> Dict:
        """Handle UPDATE queries"""
        # Example: UPDATE collection SET field1 = value1 WHERE condition
        match = re.match(r'UPDATE (\w+) SET \((.*?)\)(?:\s+WHERE (.+))?', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE query format")
            
        collection_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3) if match.group(3) else ''
        
        # Parse SET clause
        updates = {}
        for item in set_clause.split(','):
            field, value = item.split('=')
            field = field.strip()
            value = value.strip().strip('\'\"')
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                pass
            updates[field] = value
        
        mongo_filter = self.parse_where_clause(where_clause)
        result = self.db[collection_name].update_many(
            mongo_filter,
            {'$set': updates}
        )
        return {"modified_count": result.modified_count}

    def _handle_delete(self, query: str) -> Dict:
        """Handle DELETE queries"""
        # Example: DELETE FROM collection WHERE condition
        match = re.match(r'DELETE FROM (\w+)(?:\s+WHERE (.+))?', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE query format")
            
        collection_name = match.group(1)
        where_clause = match.group(2) if match.group(2) else ''
        
        mongo_filter = self.parse_where_clause(where_clause)
        result = self.db[collection_name].delete_many(mongo_filter)
        return {"deleted_count": result.deleted_count}