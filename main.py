def login_creds():
    correct_username = "tooly"
    correct_password = "root"

    print("======L O G I N  S Y S T E M======")
    username = input("username: ")
    password = input("password: ")

    if username == correct_username and password == correct_password:
        print("Access Granted To System!")
        return True
    else:
        print("Invalid username or password")
        return False


if login_creds():
    print("###############################################")
    print("#              GraphQL-Tooly                  #")
    print("###############################################")

    import requests
    import json
    import time
    from typing import List, Dict, Any


    class GraphQLClient:
        def __init__(self, api_url: str, headers: Dict[str, str] = None):
            self.api_url = api_url
            self.headers = headers or {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

        def send_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
            """
            Send a single GraphQL query to the API
            """
            payload = {
                'query': query,
                'variables': variables or {}
            }

            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error sending query: {e}")
                return {'errors': [str(e)]}

        def send_multiple_queries(self, queries: List[str], delay: float = 0.1) -> List[Dict[str, Any]]:
            """
            Send multiple GraphQL queries with optional delay between requests
            """
            results = []

            for i, query in enumerate(queries, 1):
                print(f"Sending query {i}/{len(queries)}...")

                result = self.send_query(query)
                results.append(result)

                # Add delay to avoid overwhelming the server
                if i < len(queries):
                    time.sleep(delay)

            return results


    def get_api_details():
        """
        Interactive function to get API details from user
        """
        print("=== GraphQL API Configuration ===")
        print()

        # Get API URL
        api_url = input("Enter GraphQL API endpoint URL: ").strip()
        if not api_url:
            print("Error: API URL is required!")
            exit(1)

        # Get authentication method
        print("\nSelect authentication method:")
        print("1. No authentication")
        print("2. Bearer Token")
        print("3. API Key")
        print("4. Custom headers")

        auth_choice = input("Enter choice (1-4): ").strip()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if auth_choice == "2":
            token = input("Enter Bearer Token: ").strip()
            headers['Authorization'] = f'Bearer {token}'
        elif auth_choice == "3":
            api_key = input("Enter API Key: ").strip()
            key_name = input("Enter header name for API key (default: X-API-Key): ").strip()
            if not key_name:
                key_name = 'X-API-Key'
            headers[key_name] = api_key
        elif auth_choice == "4":
            print("Enter custom headers (leave header name empty to finish):")
            while True:
                header_name = input("Header name: ").strip()
                if not header_name:
                    break
                header_value = input("Header value: ").strip()
                headers[header_name] = header_value

        # Get GraphQL query
        print("\nEnter your GraphQL query:")
        print("(Press Enter on an empty line to finish)")
        graphql_query = ""
        while True:
            line = input()
            if not line:
                break
            graphql_query += line + "\n"

        if not graphql_query.strip():
            print("Error: GraphQL query is required!")
            exit(1)

        # Ask if user wants to use variables
        use_variables = input("\nDo you want to use variables in your query? (y/n): ").strip().lower()
        variables = None

        if use_variables == 'y':
            print("Enter variables as JSON (leave empty for no variables):")
            variables_input = input().strip()
            if variables_input:
                try:
                    variables = json.loads(variables_input)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format for variables!")
                    exit(1)

        # Get delay between requests
        try:
            delay = float(input("\nEnter delay between requests in seconds (default: 0.1): ").strip() or "0.1")
        except ValueError:
            print("Invalid delay, using default: 0.1")
            delay = 0.1

        return api_url, headers, graphql_query.strip(), variables, delay


    def create_queries(base_query: str, num_queries: int = 100) -> List[str]:
        """
        Create a list of queries - all identical in this case
        """
        return [base_query] * num_queries


    def create_queries_with_variables(base_query: str, variables_template: Dict[str, Any], num_queries: int = 100) -> \
    List[Dict[str, Any]]:
        """
        Create queries with different variables for each query
        This is an advanced option if you want to send different variables with each query
        """
        queries = []
        for i in range(num_queries):
            # Modify variables for each query if needed
            # For example, increment an ID or change parameters
            modified_variables = variables_template.copy()
            # You can modify variables here based on the query index
            # modified_variables['id'] = i + 1
            queries.append({
                'query': base_query,
                'variables': modified_variables
            })
        return queries


    def main():
        # Get API details interactively
        API_URL, headers, GRAPHQL_QUERY, variables, delay = get_api_details()

        # Fixed to send exactly 100 queries
        NUM_QUERIES = 100

        # Display configuration summary
        print("\n" + "=" * 50)
        print("Configuration Summary:")
        print(f"API URL: {API_URL}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Query: {GRAPHQL_QUERY}")
        if variables:
            print(f"Variables: {json.dumps(variables, indent=2)}")
        print(f"Number of queries: {NUM_QUERIES}")
        print(f"Delay between requests: {delay}s")
        print("=" * 50)

        # Confirm before proceeding
        confirm = input(f"\nProceed with sending {NUM_QUERIES} queries? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return

        # Initialize the GraphQL client
        client = GraphQLClient(API_URL, headers)

        # Create exactly 100 queries
        queries = create_queries(GRAPHQL_QUERY, NUM_QUERIES)

        print(f"\nStarting to send {len(queries)} GraphQL queries to {API_URL}")
        print("=" * 50)

        # Send all queries
        start_time = time.time()
        results = client.send_multiple_queries(queries, delay=delay)
        end_time = time.time()

        # Analyze results
        successful_queries = 0
        failed_queries = 0
        error_details = []

        print("\n" + "=" * 50)
        print("Results Summary:")
        for i, result in enumerate(results, 1):
            if 'errors' in result and result['errors']:
                error_msg = result['errors'][0] if result['errors'] else 'Unknown error'
                print(f"Query {i}: FAILED - {error_msg}")
                failed_queries += 1
                error_details.append({
                    'query_number': i,
                    'error': error_msg
                })
            else:
                print(f"Query {i}: SUCCESS")
                successful_queries += 1

        print("=" * 50)
        print(f"COMPLETED: Sent {NUM_QUERIES} queries")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Average time per query: {(end_time - start_time) / NUM_QUERIES:.3f} seconds")
        print(f"Successful queries: {successful_queries}")
        print(f"Failed queries: {failed_queries}")
        print(f"Success rate: {(successful_queries / NUM_QUERIES) * 100:.1f}%")

        # Save results to file
        timestamp = int(time.time())
        filename = f'graphql_100_queries_results_{timestamp}.json'

        output_data = {
            'config': {
                'api_url': API_URL,
                'headers': headers,
                'query': GRAPHQL_QUERY,
                'variables': variables,
                'num_queries': NUM_QUERIES,
                'delay': delay,
                'timestamp': timestamp
            },
            'summary': {
                'total_queries': NUM_QUERIES,
                'successful_queries': successful_queries,
                'failed_queries': failed_queries,
                'success_rate': (successful_queries / NUM_QUERIES) * 100,
                'total_time_seconds': end_time - start_time,
                'avg_time_per_query_seconds': (end_time - start_time) / NUM_QUERIES,
                'start_time': start_time,
                'end_time': end_time
            },
            'error_details': error_details,
            'all_results': results
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nDetailed results saved to '{filename}'")

        # Display performance metrics
        if successful_queries > 0:
            queries_per_second = successful_queries / (end_time - start_time)
            print(f"Performance: {queries_per_second:.2f} successful queries per second")

        # Show first few results as sample
        print(f"\nSample of first successful result:")
        for result in results:
            if 'errors' not in result or not result['errors']:
                print(
                    json.dumps(result, indent=2)[:500] + "..." if len(json.dumps(result)) > 500 else json.dumps(result,
                                                                                                                indent=2))
                break


    if __name__ == "__main__":
        main()
