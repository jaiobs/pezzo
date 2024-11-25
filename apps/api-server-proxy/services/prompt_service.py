import psycopg2
from db_config import get_db_connection

class PromptService:
    @staticmethod
    def validate_api_key(api_key):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute(
                """
                SELECT * FROM "ApiKey" 
                WHERE id = %s
                """,
                (api_key,)
            )
            
            row = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if row is None:
                raise Exception("Invalid API key")
                
            return True
            
        except psycopg2.Error as e:
            raise Exception(f'Database error: {str(e)}')

    @staticmethod
    def get_prompt_version(name, project_id, environment, api_key):
        try:
            # First validate the API key
            PromptService.validate_api_key(api_key)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute(
                """
                SELECT pv."promptId", pv.sha, pv.content
                FROM "Prompt" p 
                INNER JOIN "PromptEnvironment" pe ON p.id = pe."promptId"
                INNER JOIN "Environment" e ON pe."environmentId" = e.id
                INNER JOIN "PromptVersion" pv ON pe."promptVersionSha" = pv.sha
                WHERE p.name = %s
                AND e.name = %s
                AND e."projectId" = %s
                ;
                """,
                (name, environment, project_id)
            )
            
            row = cur.fetchone()
            
            cur.close()
            conn.close()    
            
            if row is None:
                return None

            response_data = {
                "promptId": row[0],
                "promptVersionSha": row[1],
                "content": row[2]
            }
            return response_data
            
        except psycopg2.Error as e:
            raise Exception(f'Database error: {str(e)}') 
        