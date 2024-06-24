
#!/bin/bash

# Function to update import statements in a file
update_imports() {
    local FILE_PATH=$1
    if [[ -f "$FILE_PATH" ]]; then
        sed -i 's/from collections import Mapping, OrderedDict/from collections.abc import Mapping\nfrom collections import OrderedDict/' "$FILE_PATH"
        sed -i 's/from collections import Iterable, OrderedDict/from collections.abc import Iterable\nfrom collections import OrderedDict/' "$FILE_PATH"
        echo "Updated the import statements in $FILE_PATH"
    else
        echo "File not found: $FILE_PATH"
    fi
}

# Update graphene types/field.py
FIELD_FILE_PATH="$(pip show graphene | grep Location | cut -d' ' -f2)/graphene/types/field.py"
update_imports "$FIELD_FILE_PATH"

# Update graphene relay/connection.py
CONNECTION_FILE_PATH="$(pip show graphene | grep Location | cut -d' ' -f2)/graphene/relay/connection.py"
update_imports "$CONNECTION_FILE_PATH"

y
