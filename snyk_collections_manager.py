#!/usr/bin/env python3
"""
Snyk Collections Manager

This script uses the Snyk REST API to:
1. Retrieve a list of project IDs based on project name prefix using names_start_with
2. Create a Collection if needed (if there is not one existing with the Project name given above)
3. Add those projects by using the collected Project IDs to that Collection using the Snyk Collections API

Author: Generated for CollectionsAPI project
"""

import requests
import json
import argparse
import sys
from typing import List, Dict
import time


class SnykCollectionsManager:
    """Manages Snyk projects and collections using the Snyk REST API."""
    
    def __init__(self, api_token: str, org_id: str):
        """
        Initialize the Snyk Collections Manager.
        
        Args:
            api_token: Snyk API token
            org_id: Snyk organization ID
        """
        self.api_token = api_token
        self.org_id = org_id
        self.base_url = "https://api.snyk.io/rest"
        self.api_version = "2024-10-15"
        self.headers = {
            'Authorization': f'token {api_token}',
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json'
        }
    
    def get_projects_by_name_prefix(self, name_prefix: str) -> List[Dict]:
        """
        Retrieve projects that start with the specified name prefix using the REST API.
        
        Args:
            name_prefix: The prefix to match project names against
            
        Returns:
            List of project dictionaries matching the prefix
        """
        print(f"Retrieving projects with name prefix: '{name_prefix}'")
        
        projects = []
        url = f"{self.base_url}/orgs/{self.org_id}/projects?version={self.api_version}&names_start_with={name_prefix}"
        
        try:
            while url:
                print(f"Fetching projects from: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                # Extract projects from the REST API response format
                project_data = data.get('data', [])
                projects.extend(project_data)
                
                # Check for pagination
                links = data.get('links', {})
                url = links.get('next')
                
                if url:
                    print(f"Found {len(project_data)} projects on this page, continuing to next page...")
            
            print(f"Found {len(projects)} projects matching prefix '{name_prefix}'")
            for project in projects:
                # REST API uses 'attributes' for project data
                attributes = project.get('attributes', {})
                project_name = attributes.get('name', 'Unknown')
                project_id = project.get('id', 'Unknown')
                print(f"  - {project_name} (ID: {project_id})")
            
            return projects
            
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving projects: {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    print(f"⚠️  Projects endpoint not found. This organization may not have projects yet.")
                elif e.response.status_code == 401:
                    print(f"⚠️  Unauthorized. Please check your API token and organization ID.")
                elif e.response.status_code == 403:
                    print(f"⚠️  Forbidden. You may not have permission to access projects.")
            return []
    
    def get_collections(self) -> List[Dict]:
        """
        Retrieve all collections for the organization using the REST API.
        
        Returns:
            List of collection dictionaries
        """
        print("Retrieving existing collections...")
        
        collections = []
        url = f"{self.base_url}/orgs/{self.org_id}/collections?version={self.api_version}"
        
        try:
            while url:
                print(f"Fetching collections from: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                # Extract collections from the REST API response format
                collection_data = data.get('data', [])
                collections.extend(collection_data)
                
                # Check for pagination
                links = data.get('links', {})
                url = links.get('next')
                
                if url:
                    print(f"Found {len(collection_data)} collections on this page, continuing to next page...")
            
            print(f"Found {len(collections)} existing collections")
            for collection in collections:
                # REST API uses 'attributes' for collection data
                attributes = collection.get('attributes', {})
                collection_name = attributes.get('name', 'Unknown')
                collection_id = collection.get('id', 'Unknown')
                print(f"  - {collection_name} (ID: {collection_id})")
            
            return collections
            
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving collections: {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    print(f"⚠️  Collections are not available for this organization (404 Not Found)")
                    print(f"   Collections might be a premium feature or not enabled.")
                    print(f"   The script cannot proceed without collections support.")
                elif e.response.status_code == 401:
                    print(f"⚠️  Unauthorized. Please check your API token and organization ID.")
                elif e.response.status_code == 403:
                    print(f"⚠️  Forbidden. You may not have permission to access collections.")
            return []
    
    def find_collection_by_name(self, collection_name: str) -> Dict:
        """
        Find a collection by name using the REST API format.
        
        Args:
            collection_name: Name of the collection to find
            
        Returns:
            Collection dictionary if found, None otherwise
        """
        collections = self.get_collections()
        
        for collection in collections:
            # REST API uses 'attributes' for collection data
            attributes = collection.get('attributes', {})
            if attributes.get('name') == collection_name:
                return collection
        
        return None
    
    def create_collection(self, collection_name: str, project_ids: List[str] = None) -> Dict:
        """
        Create a new collection using the REST API format.
        
        Args:
            collection_name: Name of the collection to create
            project_ids: Optional list of project IDs to include
            
        Returns:
            Created collection dictionary
        """
        if project_ids:
            print(f"Creating collection '{collection_name}' with {len(project_ids)} projects...")
        else:
            print(f"Creating collection: '{collection_name}'")
        
        url = f"{self.base_url}/orgs/{self.org_id}/collections?version={self.api_version}"
        
        # Create payload with projects included if provided
        payload = {
            'data': {
                'type': 'collection',
                'attributes': {
                    'name': collection_name
                }
            }
        }
        
        # Add projects to the payload if provided
        if project_ids:
            payload['data']['relationships'] = {
                'projects': {
                    'data': [
                        {
                            'id': project_id,
                            'type': 'project'
                        } for project_id in project_ids
                    ]
                }
            }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            collection_data = response.json()
            
            # Extract collection from REST API response format
            collection = collection_data.get('data', {})
            collection_id = collection.get('id', 'Unknown')
            
            if project_ids:
                print(f"Successfully created collection '{collection_name}' with {len(project_ids)} projects (ID: {collection_id})")
            else:
                print(f"Successfully created collection '{collection_name}' (ID: {collection_id})")
            
            return collection
            
        except requests.exceptions.RequestException as e:
            print(f"Error creating collection: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            
            # If creating with projects fails, try creating without projects
            if project_ids:
                print("Falling back to creating collection without projects...")
                return self.create_collection(collection_name)
            else:
                sys.exit(1)
    
    def add_projects_to_collection(self, collection_id: str, project_ids: List[str], collection_name: str = "Collection") -> bool:
        """
        Add projects to a collection using the REST API format.
        
        Args:
            collection_id: ID of the collection
            project_ids: List of project IDs to add
            
        Returns:
            True if successful, False otherwise
        """
        if not project_ids:
            print("No projects to add to collection")
            return True
        
        print(f"Adding {len(project_ids)} projects to collection...")
        
        # Use the correct endpoint for adding projects to a collection
        url = f"{self.base_url}/orgs/{self.org_id}/collections/{collection_id}/relationships/projects?version={self.api_version}"
        payload = {
            'data': [
                {
                    'id': project_id,
                    'type': 'project'
                } for project_id in project_ids
            ]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            print(f"Successfully added {len(project_ids)} projects to collection")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error adding projects to collection: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return False
    
    def extract_project_ids(self, name_prefix: str) -> List[str]:
        """
        Extract project IDs that match the name prefix.
        
        Args:
            name_prefix: The prefix to match project names against
            
        Returns:
            List of project IDs
        """
        print(f"Extracting project IDs with name prefix: '{name_prefix}'")
        
        projects = self.get_projects_by_name_prefix(name_prefix)
        project_ids = [project['id'] for project in projects]
        
        print(f"Extracted {len(project_ids)} project IDs:")
        for i, project_id in enumerate(project_ids, 1):
            print(f"  {i}. {project_id}")
        
        return project_ids
    
    def save_project_ids(self, project_ids: List[str], output_file: str = None) -> None:
        """
        Save project IDs to a file.
        
        Args:
            project_ids: List of project IDs to save
            output_file: Optional output file path
        """
        if not output_file:
            output_file = f"project_ids_{int(time.time())}.txt"
        
        try:
            with open(output_file, 'w') as f:
                for project_id in project_ids:
                    f.write(f"{project_id}\n")
            
            print(f"Project IDs saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving project IDs to file: {e}")
    
    def process_projects_and_collection(self, project_name_prefix: str, collection_name: str, output_file: str = None) -> List[str]:
        """
        Main method to process projects, extract IDs, and manage collections.
        
        Args:
            project_name_prefix: Prefix to match project names
            collection_name: Name of the collection
            output_file: Optional output file path
            
        Returns:
            List of project IDs
        """
        print(f"Starting Snyk Collections Manager")
        print(f"Organization ID: {self.org_id}")
        print(f"Project name prefix: '{project_name_prefix}'")
        print(f"Collection name: '{collection_name}'")
        print("-" * 50)
        
        # Step 1: Extract project IDs
        project_ids = self.extract_project_ids(project_name_prefix)
        
        if not project_ids:
            print("-" * 50)
            print(f"No projects found with prefix '{project_name_prefix}'")
            return []
        
        # Step 2: Check if collections are available
        collections = self.get_collections()
        
        if collections is None or (isinstance(collections, list) and len(collections) == 0 and not collections):
            print(f"❌ Collections are not available for this organization.")
            print(f"   This could be because:")
            print(f"   1. Collections are a premium feature")
            print(f"   2. Collections are not enabled for your organization")
            print(f"   3. Your organization type doesn't support collections")
            print(f"   Please contact Snyk support or upgrade your plan to use collections.")
            return project_ids  # Still return the project IDs even if collections aren't available
        
        # Step 3: Check if collection exists, create if not
        collection = self.find_collection_by_name(collection_name)
        
        if not collection:
            # Try to create collection with projects included
            collection = self.create_collection(collection_name, project_ids)
            # Add projects to the newly created collection
            success = self.add_projects_to_collection(collection['id'], project_ids, collection_name)
        else:
            print(f"Collection '{collection_name}' already exists (ID: {collection['id']})")
            # Try to add projects to existing collection
            success = self.add_projects_to_collection(collection['id'], project_ids, collection_name)
        
        if success:
            print("-" * 50)
            print(f"Successfully processed {len(project_ids)} projects")
            collection_id = collection.get('id', 'Unknown')
            print(f"Collection: {collection_name} (ID: {collection_id})")
            
            # Save to file if requested
            if output_file:
                self.save_project_ids(project_ids, output_file)
            
            return project_ids
        else:
            print("-" * 50)
            print(f"Failed to add projects to collection")
            return project_ids


def load_config(config_file: str = "config.json") -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file '{config_file}' not found.")
        print("Please create a config.json file with your Snyk API token and organization ID.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Extract Snyk project IDs and manage collections using the Snyk REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python snyk_collections_manager.py --prefix "my-app" --collection "My Applications"
  python snyk_collections_manager.py --prefix "backend" --collection "Backend Services" --output project_ids.txt
  python snyk_collections_manager.py --prefix "frontend" --collection "Frontend Apps" --config custom_config.json
  python snyk_collections_manager.py --prefix "api" --collection "API Services" --token YOUR_TOKEN --org YOUR_ORG_ID
        """
    )
    
    parser.add_argument(
        '--prefix', '-p',
        required=True,
        help='Project name prefix to match (required)'
    )
    
    parser.add_argument(
        '--collection', '-c',
        required=True,
        help='Collection name (required)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file to save project IDs (optional)'
    )
    
    parser.add_argument(
        '--token', '-t',
        help='Snyk API token (can also be set in config file)'
    )
    
    parser.add_argument(
        '--org',
        help='Snyk organization ID (can also be set in config file)'
    )
    
    parser.add_argument(
        '--config', '-f',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be extracted without making API calls'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if not args.token or not args.org:
        config = load_config(args.config)
        api_token = args.token or config.get('api_token')
        org_id = args.org or config.get('org_id')
    else:
        api_token = args.token
        org_id = args.org
    
    if not api_token or not org_id:
        print("Error: Both API token and organization ID are required.")
        print("Provide them via command line arguments or config file.")
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN MODE - No API calls will be made")
        print(f"Would extract projects with prefix: '{args.prefix}'")
        print(f"Would use/create collection: '{args.collection}'")
        if args.output:
            print(f"Would save to file: '{args.output}'")
        return
    
    # Initialize manager and run
    manager = SnykCollectionsManager(api_token, org_id)
    project_ids = manager.process_projects_and_collection(args.prefix, args.collection, args.output)
    
    if project_ids:
        print("\n✅ Operation completed successfully!")
        print(f"Extracted {len(project_ids)} project IDs")
        sys.exit(0)
    else:
        print("\n❌ No projects found with the specified prefix!")
        sys.exit(1)


if __name__ == "__main__":
    main()