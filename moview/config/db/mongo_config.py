class MongoConfig:
    def __init__(self, host: str = 'localhost', port: int = 27017, db_name: str = 'interview_database',
                 collection_name: str = 'interview_data'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name
