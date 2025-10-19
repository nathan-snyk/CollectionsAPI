# Snyk Collections Manager

A Python script that uses the Snyk REST API to extract project IDs and manage collections. This tool allows you to:

- Retrieve a list of project IDs based on project name prefix using the `names_start_with` field
- Create a Collection if needed (if there is not one existing with the Project name given above)
- Extract project IDs for further processing (collections API has limitations)
- Save project IDs to a file for further processing
- Handle pagination automatically

## Features

- ✅ Filter projects by name prefix using the Snyk REST API
- ✅ Extract project IDs from matching projects
- ✅ Create collections (when collections are available)
- ✅ Save project IDs to a file (optional)
- ✅ Handle pagination automatically
- ✅ Dry-run mode to preview what would be extracted
- ✅ Comprehensive error handling
- ✅ Command-line interface with flexible configuration

## ⚠️ Important Notes

**API Requirements:** 

- **Collections API**: Collections may not be available for all organization types and might require a premium Snyk plan
- **Snyk REST API**: The script uses the [Snyk REST API endpoint](https://docs.snyk.io/snyk-api/reference/collection#post-orgs-org_id-collections-collection_id-relationships-projects) to add projects to collections

If your organization doesn't have collections enabled, the script will provide clear error messages explaining the situation and potential solutions.

## Prerequisites

1. **Python 3.7+** - The script requires Python 3.7 or higher
2. **Snyk API Token** - You need a valid Snyk API token with appropriate permissions
3. **Snyk Organization ID** - Your Snyk organization ID

### Getting Your Snyk API Token and Organization ID

1. **API Token**: 
   - Log into your Snyk account
   - Go to Account Settings → General → API Token
   - Copy your API token

2. **Organization ID**:
   - In the Snyk web interface, look at the URL when viewing your organization
   - The organization ID is typically in the format: `https://app.snyk.io/org/[ORG_ID]/`
   - Or check your account settings under "Organization ID"

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**:
   ```bash
   cp config.json.example config.json
   # Edit config.json with your Snyk API token and organization ID
   ```

## Configuration

### Option 1: Configuration File (Recommended)

Create a `config.json` file in the same directory as the script:

```json
{
  "api_token": "your_actual_snyk_api_token",
  "org_id": "your_actual_organization_id"
}
```

### Option 2: Command Line Arguments

You can also provide the credentials via command line arguments:

```bash
python snyk_collections_manager.py --token YOUR_TOKEN --org YOUR_ORG_ID --prefix "my-app" --collection "My Applications"
```

## Usage

### Basic Usage

```bash
python snyk_collections_manager.py --prefix "my-app"
```

This will:
1. Find all projects whose names start with "my-app"
2. Display the project IDs in the terminal
3. Optionally save them to a file

### Advanced Usage

#### Save to File

Save the extracted project IDs to a file:

```bash
python snyk_collections_manager.py --prefix "backend" --output backend_project_ids.txt
```

#### Dry Run Mode

Preview what the script would extract without making API calls:

```bash
python snyk_collections_manager.py --prefix "backend" --dry-run
```

#### Custom Configuration File

Use a different configuration file:

```bash
python snyk_collections_manager.py --config my_config.json --prefix "frontend"
```

#### Command Line Credentials

Provide credentials directly via command line:

```bash
python snyk_collections_manager.py --token YOUR_TOKEN --org YOUR_ORG_ID --prefix "api"
```

### Command Line Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--prefix` | `-p` | Project name prefix to match | ✅ Yes |
| `--output` | `-o` | Output file to save project IDs | No |
| `--token` | `-t` | Snyk API token | No* |
| `--org` | `-o` | Snyk organization ID | No* |
| `--config` | `-f` | Configuration file path | No (default: config.json) |
| `--dry-run` | | Preview what would be extracted without API calls | No |

*Required if not provided in config file

## Examples

### Example 1: Extract Backend Project IDs

```bash
python snyk_collections_manager.py --prefix "backend-"
```

This will find all projects starting with "backend-" and display their IDs.

### Example 2: Save Project IDs to File

```bash
python snyk_collections_manager.py --prefix "prod-" --output production_projects.txt
python snyk_collections_manager.py --prefix "staging-" --output staging_projects.txt
python snyk_collections_manager.py --prefix "dev-" --output development_projects.txt
```

### Example 3: Extract Team Project IDs

```bash
python snyk_collections_manager.py --prefix "team-alpha-" --output team_alpha_projects.txt
python snyk_collections_manager.py --prefix "team-beta-" --output team_beta_projects.txt
```

## Output

The script provides detailed output showing:

- Number of projects found matching the prefix
- List of matching projects with their IDs
- Extracted project IDs
- Optional file save confirmation
- Success/failure status

Example output:
```
Starting Snyk Collections Manager
Organization ID: your-org-id
Project name prefix: 'my-app'
Collection name: 'My Applications'
--------------------------------------------------
Extracting project IDs with name prefix: 'my-app'
Retrieving projects with name prefix: 'my-app'
Fetching projects from: https://api.snyk.io/rest/orgs/your-org-id/projects?version=2024-10-15&names_start_with=my-app
Found 3 projects matching prefix 'my-app'
  - my-app-frontend (ID: abc123)
  - my-app-backend (ID: def456)
  - my-app-mobile (ID: ghi789)
Extracted 3 project IDs:
  1. abc123
  2. def456
  3. ghi789
Retrieving existing collections...
Found 5 existing collections
Creating collection: 'My Applications'
Successfully created collection 'My Applications' (ID: collection123)
Adding 3 projects to collection...
Successfully added 3 projects to collection
--------------------------------------------------
Successfully processed 3 projects
Collection: My Applications (ID: collection123)

✅ Operation completed successfully!
Extracted 3 project IDs
```

## Error Handling

The script includes comprehensive error handling for:

- Invalid API tokens
- Network connectivity issues
- Missing organization IDs
- Invalid project or collection names
- API rate limiting
- Malformed responses

## Troubleshooting

### Common Issues

1. **"Error retrieving projects" / "Projects API endpoint is deprecated (410 Gone)"**
   - The Snyk v1 API projects endpoint is deprecated
   - Your organization may not have any projects yet
   - This is normal for new organizations
   - The script will continue to work with collections

2. **"Collections are not available for this organization (404 Not Found)"**
   - Collections might be a premium feature
   - Collections may not be enabled for your organization type
   - Contact Snyk support or upgrade your plan to use collections
   - This is the most common issue for free/organization accounts

3. **"No projects found with prefix"**
   - Verify the prefix is correct
   - Check that projects exist with that naming pattern
   - Use `--dry-run` to preview what would be found
   - Your organization may not have any projects yet

4. **"Error creating collection"**
   - Check if you have permission to create collections
   - Verify the collection name doesn't contain invalid characters
   - Ensure collections are available for your organization

5. **"Error adding projects to collection"**
   - Ensure the projects exist and are accessible
   - Check that the collection was created successfully

### API Limitations

**Important:** This script uses the Snyk v1 API, which has some limitations:

- **Projects API (410 Gone)**: The projects endpoint is deprecated but still functional for organizations with existing projects
- **Collections API (404 Not Found)**: Collections may not be available for all organization types or may require a premium plan

If you encounter these issues, the script will provide helpful error messages explaining what's happening and potential solutions.

### Getting Help

If you encounter issues:

1. Run with `--dry-run` to preview changes
2. Check your API token and organization ID
3. Verify your Snyk account has the necessary permissions
4. Check the Snyk API documentation for any changes

## API Rate Limits

The script respects Snyk's API rate limits. If you encounter rate limiting issues:

- The script will show appropriate error messages
- Consider running the script during off-peak hours
- For large numbers of projects, the script may need to be modified to include delays

## Security Notes

- Never commit your `config.json` file with real credentials to version control
- Keep your API token secure and rotate it regularly
- Use environment variables for production deployments when possible

## License

This script is provided as-is for educational and operational purposes.
