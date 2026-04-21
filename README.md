# regiswitch

A Python CLI tool to switch registered files based on profiles.

## How to use

1. Create a `profiles.json` in the root directory:
   ```json
   {
     "dev": "path/to/dev/files",
     "prod": "path/to/prod/files"
   }
   ```
2. Switch profiles:
   ```bash
   python -m regiswitch switch --profile dev
   ```
